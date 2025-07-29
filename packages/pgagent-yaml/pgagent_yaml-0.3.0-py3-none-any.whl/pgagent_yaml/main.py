import os
import argparse
import asyncio
import shutil

from .extractor import Extractor
from .runner import Runner
from .synchronizer import Synchronizer
from .pg import Pg
from . import __version__

node_format = 'migration_path -> [user@]host:port/database'


async def run(args):
    pg = Pg(args)
    await pg.init()

    if args.command == 'export':
        await Extractor(args, pg).export()

    elif args.command in ('diff', 'sync'):
        await Synchronizer(args, pg).sync(show_diff_only=args.command == 'diff')

    elif args.command in ('run_now'):
        await Runner(args, pg).run_now()


def main():
    def add_connection_args(parser):
        parser.add_argument('-d', '--dbname',
                            type=str, help='database name to connect to')
        parser.add_argument('-h', '--host',
                            type=str, help='database server host or socket directory')
        parser.add_argument('-p', '--port',
                            type=str, help='database server port')
        parser.add_argument('-U', '--user',
                            type=str, help='database user name')
        parser.add_argument('-W', '--password',
                            type=str, help='database user password')

    def add_ignore_version(parser):
        parser.add_argument(
            '--ignore-version',
            action="store_true",
            help='try exporting an unsupported server version'
        )

    arg_parser = argparse.ArgumentParser(
        epilog='Report bugs: https://gitlab.uis.dev/pg_tools/pgagent-yaml/issues',
        conflict_handler='resolve',
    )

    arg_parser.add_argument(
        '--version',
        action='version',
        version=__version__
    )

    subparsers = arg_parser.add_subparsers(
        dest='command',
        title='commands'
    )

    parser_export = subparsers.add_parser(
        'export',
        help='export pgagent jobs to files',
        conflict_handler='resolve',
    )
    add_connection_args(parser_export)
    parser_export.add_argument(
        '--out-dir',
        required=True,
        help='directory for exporting files'
    )
    parser_export.add_argument(
        '--clean',
        action="store_true",
        help='clean out_dir if not empty '
        '(env variable PGAGENT_YAML_AUTOCLEAN=true)'
    )
    add_ignore_version(parser_export)
    parser_export.add_argument(
        '--include-schedule-start-end',
        action="store_true",
        help='include "start", "end" fields (without by default)'
    )

    parser_diff = subparsers.add_parser(
        'diff',
        help='show diff files and pgagent jobs',
        conflict_handler='resolve',
    )
    add_connection_args(parser_diff)
    parser_diff.add_argument(
        '--source',
        required=True,
        help='directory or file with jobs to compare with pgagent'
    )
    add_ignore_version(parser_diff)

    parser_sync = subparsers.add_parser(
        'sync',
        help='sync files to pgagent jobs',
        conflict_handler='resolve',
    )
    add_connection_args(parser_sync)
    parser_sync.add_argument(
        '--source',
        required=True,
        help='directory or file with jobs to sync to pgagent'
    )
    parser_sync.add_argument(
        '--dry-run',
        action="store_true",
        help='test run without real changes'
    )
    parser_sync.add_argument(
        '--echo-queries',
        action="store_true",
        help='echo commands sent to server'
    )
    parser_sync.add_argument(
        '-y', '--yes',
        action="store_true",
        help='do not ask confirm'
    )
    add_ignore_version(parser_sync)

    parser_run_now = subparsers.add_parser(
        'run_now',
        help='sync files to pgagent jobs',
        conflict_handler='resolve',
    )
    add_connection_args(parser_run_now)
    parser_run_now.add_argument(
        '--job',
        required=True,
        help='name of job to run'
    )
    add_ignore_version(parser_run_now)

    args = arg_parser.parse_args()

    if args.command == 'export':
        if os.path.exists(args.out_dir) and os.listdir(args.out_dir):
            if args.clean or os.environ.get('PGAGENT_YAML_AUTOCLEAN') == 'true':
                shutil.rmtree(args.out_dir)
            else:
                parser_export.error('out_dir directory not empty '
                                    '(you can use option --clean)')
        try:
            os.makedirs(args.out_dir, exist_ok=True)
        except Exception:
            arg_parser.error("can not access to directory '%s'" % args.out_dir)

    if args.command == 'diff':
        if not os.path.exists(args.source):
            parser_diff.error(f'file or directory not found: {args.source}')

    if args.command == 'sync':
        if not os.path.exists(args.source):
            parser_export.error(f'file or directory not found: {args.source}')

    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run(args))
