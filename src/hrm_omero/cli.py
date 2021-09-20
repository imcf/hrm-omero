"""Command-line interface related functions."""

import argparse
import sys

from loguru import logger as log

from .__init__ import __version__
from . import formatting
from . import hrm
from . import omero
from . import transfer


def bool_to_exitstatus(value):
    """Convert a boolean to a POSIX process exit code.

    As boolean values in Python are a subset of int, `True` corresponds to the int value
    '1', which is the opposite of a successful POSIX return code. Therefore, this
    function simply inverts the boolean value to turn it into a proper exit code. In
    case the provided value is not of type `bool` it will be returned unchanged.

    Parameters
    ----------
    value : bool or int
        The value to be converted.

    Returns
    -------
    int
        0 in case `value` is `True`, 1 in case `value` is `False` and `value` itself in
        case it is not a bool.
    """
    if type(value) is bool:
        return not value
    else:
        return value


def parse_arguments(args):
    """Parse the commandline arguments."""
    # log.debug("Parsing command line arguments...")
    argparser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    argparser.add_argument(
        "-v",
        "--verbose",
        dest="verbosity",
        action="count",
        default=0,
        help="verbose messages (repeat for more details)",
    )

    argparser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    argparser.add_argument(
        "-c",
        "--config",
        default="/etc/hrm.conf",
        help="the HRM configuration file (default: '/etc/hrm.conf')",
    )

    # required arguments group
    req_args = argparser.add_argument_group(
        "required arguments", "NOTE: MUST be given before any subcommand!"
    )
    req_args.add_argument("-u", "--user", required=True, help="OMERO username")
    req_args.add_argument("-w", "--password", required=True, help="OMERO password")

    subparsers = argparser.add_subparsers(
        help=".",
        dest="action",
        description="Action to be performed, one of the following:",
    )

    # checkCredentials parser
    subparsers.add_parser(
        "checkCredentials", help="check if login credentials are valid"
    )

    # retrieveChildren parser
    parser_subtree = subparsers.add_parser(
        "retrieveChildren", help="get the children of a given node object (JSON)"
    )
    parser_subtree.add_argument(
        "--id",
        type=str,
        required=True,
        help='ID of the parent object, e.g. "ROOT", "G:4:Experimenter:7',
    )

    # OMEROtoHRM parser
    parser_o2h = subparsers.add_parser(
        "OMEROtoHRM", help="download an image from the OMERO server"
    )
    parser_o2h.add_argument(
        "-i",
        "--imageid",
        required=True,
        help='the OMERO ID of the image to download, e.g. "G:4:Image:42"',
    )
    parser_o2h.add_argument(
        "-d",
        "--dest",
        type=str,
        required=True,
        help="the destination directory where to put the downloaded file",
    )

    # HRMtoOMERO parser
    parser_h2o = subparsers.add_parser(
        "HRMtoOMERO", help="upload an image to the OMERO server"
    )
    parser_h2o.add_argument(
        "-d",
        "--dset",
        required=True,
        dest="dset",
        help='the ID of the target dataset in OMERO, e.g. "G:7:Dataset:23"',
    )
    parser_h2o.add_argument(
        "-f",
        "--file",
        type=str,
        required=True,
        help="the image file to upload, including the full path",
    )
    parser_h2o.add_argument(
        "-n",
        "--name",
        type=str,
        required=False,
        help="a label to use for the image in OMERO",
    )
    parser_h2o.add_argument(
        "-a",
        "--ann",
        type=str,
        required=False,
        help="annotation text to be added to the image in OMERO",
    )

    try:
        return argparser.parse_args(args)
    except IOError as err:
        argparser.error(str(err))


def run_task(args):
    """Parse commandline arguments and initiate the requested tasks."""
    args = parse_arguments(args)

    # one of the downsides of loguru is that the level of an existing logger can't be
    # changed - so to adjust verbosity we actually need to remove the default logger and
    # re-add it with the new level (unless maximum verbosity was requested anyway...)
    # see https://github.com/Delgan/loguru/issues/138 for more information
    log_level = "TRACE"
    if args.verbosity < 4:  # -vvvv (4) will result in "TRACE", nothing to be done then
        log.remove()
        if args.verbosity == 3:  # -vvv will be "DEBUG"
            log_level = "DEBUG"
        elif args.verbosity == 2:  # -vv will be "INFO"
            log_level = "INFO"
        elif args.verbosity == 1:  # -v will be "SUCCESS"
            log_level = "SUCCESS"
        else:  # no verbosity flag has been provided
            log_level = "WARNING"
        log.add(sys.stderr, level=log_level)

    # uncomment the lines below and adjust to manually set the log level until this is
    # possible through the HRM configuration file
    # log_level = "DEBUG"
    # log.remove()
    # log.add(sys.stderr, level=log_level)

    log.success("Logging verbosity requested: {} ({})", args.verbosity, log_level)

    hrm_config = hrm.parse_config(args.config)
    host = hrm_config.get("OMERO_HOSTNAME", "localhost")
    port = hrm_config.get("OMERO_PORT", 4064)

    conn = omero.connect(args.user, args.password, host, port)

    # TODO: implement requesting groups via cmdline option

    try:
        if args.action == "checkCredentials":
            return omero.check_credentials(conn)
        elif args.action == "retrieveChildren":
            return formatting.print_children_json(conn, args.id)
        elif args.action == "OMEROtoHRM":
            return transfer.from_omero(conn, args.imageid, args.dest)
        elif args.action == "HRMtoOMERO":
            return transfer.to_omero(conn, args.dset, args.file)
        else:
            raise Exception("Huh, how could this happen?!")
    finally:
        conn.close()


@log.catch
def main(args=None):
    """Wrapper to call the run_task() function and return its exit code."""
    if not args:
        args = sys.argv[1:]
    sys.exit(bool_to_exitstatus(run_task(args)))
