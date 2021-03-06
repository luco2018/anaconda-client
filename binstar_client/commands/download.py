"""
Usage:
    anaconda download notebook
    anaconda download user/notebook
"""

from __future__ import unicode_literals

import argparse
import logging

from binstar_client import errors
from binstar_client.utils import get_server_api
from binstar_client.utils.notebook import Downloader, parse, has_environment

logger = logging.getLogger("binstar.download")


def add_parser(subparsers):
    description = 'Download notebooks from your Anaconda repository'
    parser = subparsers.add_parser(
        'download',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help=description,
        description=description,
        epilog=__doc__
    )

    parser.add_argument(
        'handle',
        help="user/notebook",
        action='store'
    )

    parser.add_argument(
        '-f', '--force',
        help='Overwrite',
        action='store_true'
    )

    parser.add_argument(
        '-o', '--output',
        help='Download as',
        default='.'
    )

    parser.set_defaults(main=main)


def main(args):
    aserver_api = get_server_api(args.token, args.site)
    username, notebook = parse(args.handle)
    username = username or aserver_api.user()['login']
    downloader = Downloader(aserver_api, username, notebook)
    try:
        download_info = downloader(output=args.output, force=args.force)
        logger.info("{} has been downloaded as {}.".format(args.handle, download_info[0]))
        if has_environment(download_info[0]):
            logger.info("{} has an environment embedded.".format(download_info[0]))
            logger.info("Run:")
            logger.info("    conda env create {}".format(download_info[0]))
            logger.info("To install the environment in your system")
    except (errors.DestionationPathExists, errors.NotFound, errors.BinstarError, OSError) as err:
        logger.info(err)
