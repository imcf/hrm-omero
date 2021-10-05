"""Command-line interface related functions."""

import argparse
import os
import sys

import omero.gateway

from loguru import logger as log

from .__init__ import __version__
from . import formatting
from . import hrm
from . import omero as dotomero
from . import transfer
from .misc import printlog, OmeroId


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
    if isinstance(value, bool):
        return not value

    return value


def parse_arguments(args):  # pragma: no cover
    """Parse the commandline arguments.

    DEPRECATED function, use `arguments_parser()` instead!
    """
    log.warning("'parse_arguments()' is deprecated and will be removed!")
    argparser = arguments_parser()
    try:
        return argparser.parse_args(args)
    except IOError as err:
        argparser.error(str(err))


def arguments_parser():
    """Set up the commandline arguments parser.

    Returns
    -------
    argparse.ArgumentParser
        The parser instance ready to be run using its `parse_args()` method.
    """
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

    argparser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="print requested action and parameters without actually performing it",
    )

    # deprecated arguments group
    dep_args = argparser.add_argument_group(
        "DEPRECATED arguments",
        "See the documentation for instructions on how to adapt your call!",
    )
    dep_args.add_argument(
        "-w",
        "--password",
        required=False,
        help=(
            "OMERO password  ******** DEPRECATED ********"
            "Use the environment variable 'OMERO_PASSWORD' instead!"
        ),
    )

    # required arguments group
    req_args = argparser.add_argument_group(
        "required arguments", "NOTE: MUST be given before any subcommand!"
    )
    req_args.add_argument("-u", "--user", required=True, help="OMERO username")

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

    return argparser


def verbosity_to_loglevel(verbosity):
    """Map the verbosity count to a named log level for `loguru`.

    Parameters
    ----------
    verbosity : int
        Verbosity count as returned e.g. by the following argparse code:
        `argparser.add_argument("-v", dest="verbosity", action="count", default=0)`

    Returns
    -------
    str
        A log level name that can be used with `loguru.logger.add()`.
    """
    log_level = "WARNING"  # no verbosity flag has been provided -> use "WARNING"
    if verbosity > 3:  # -vvvv (4) and more will result in "TRACE"
        log_level = "TRACE"
    if verbosity == 3:  # -vvv will be "DEBUG"
        log_level = "DEBUG"
    elif verbosity == 2:  # -vv will be "INFO"
        log_level = "INFO"
    elif verbosity == 1:  # -v will be "SUCCESS"
        log_level = "SUCCESS"
    return log_level


def run_task(args):
    """Parse commandline arguments and initiate the requested tasks."""
    argparser = arguments_parser()
    args = argparser.parse_args(args)

    # one of the downsides of loguru is that the level of an existing logger can't be
    # changed - so to adjust verbosity we actually need to remove the default logger and
    # re-add it with the new level (see https://github.com/Delgan/loguru/issues/138)
    log_level = verbosity_to_loglevel(args.verbosity)
    log.remove()
    log.add(sys.stderr, level=log_level)

    log.success(f"Logging verbosity requested: {args.verbosity} ({log_level})")

    hrm_config = hrm.parse_config(args.config)
    host = hrm_config.get("OMERO_HOSTNAME", "localhost")
    port = hrm_config.get("OMERO_PORT", 4064)
    omero_logfile = hrm_config.get("OMERO_DEBUG_LOG", "")

    log_level = hrm_config.get("OMERO_CONNECTOR_LOGLEVEL", "")
    if log_level:
        log.remove()
        log.add(sys.stderr, level=log_level)
        log.success(f"Log level set from config file: {log_level}")

    # NOTE: reading the OMERO password from an environment variable instead of an
    # argument supplied on the command line improves handling of this sensitive data as
    # the value is *NOT* immediately revealed to anyone with shell access by simply
    # looking at the process list (which is an absolute standard procedure to do). Since
    # it is not passed to any other functions here (except the call to `BlitzGateway`)
    # this also prevents it from being shown in an annotated stack trace in case an
    # uncaught exception is coming through.
    # However, this doesn't provide super-high security as it will still be possible for
    # an admin to inspect the environment of a running process. Nevertheless going
    # beyond this seems a bit pointless here as an admin could also modify the code that
    # is actually calling the connector to get hold of user credentials.
    passwd = os.environ.get("OMERO_PASSWORD")
    # while being deprecated an explicitly specified password still has priority:
    if args.password:  # pragma: no cover
        passwd = args.password
        printlog("WARNING", "Using the '--password' parameter is deprecated!")
    if not passwd:
        printlog("ERROR", "ERROR: no password given to connect to OMERO!")
        return False

    if args.action == "checkCredentials":
        perform_action = dotomero.check_credentials
        kwargs = {}

    elif args.action == "retrieveChildren":
        perform_action = formatting.print_children_json
        kwargs = {"omero_id": OmeroId(args.id)}

    elif args.action == "OMEROtoHRM":
        perform_action = transfer.from_omero
        kwargs = {
            "id_str": args.imageid,
            "dest": args.dest,
        }

    elif args.action == "HRMtoOMERO":
        perform_action = transfer.to_omero
        kwargs = {
            "id_str": args.dset,
            "image_file": args.file,
            "omero_logfile": omero_logfile,
        }

    else:
        printlog("ERROR", "No valid action specified that should be performed!")
        return False

    conn = omero.gateway.BlitzGateway(
        username=args.user,
        passwd=passwd,
        host=host,
        port=port,
        secure=True,
        useragent="hrm-omero.py",
    )

    try:
        if args.dry_run:
            printlog("INFO", "*** dry-run, only showing action and parameters ***")
            printlog("INFO", f"function: {perform_action.__qualname__}")
            for key, value in kwargs.items():
                printlog("INFO", f"{key}: [{str(value)}]")

            return True

        conn.connect()
        log.info(f"New OMERO connection [user={args.user}].")

        return perform_action(conn, **kwargs)

    finally:
        conn.close()
        log.info(f"Closed OMERO connection [user={args.user}].")


@log.catch
def main(args=None):
    """Wrapper to call the run_task() function and return its exit code."""
    if not args:
        args = sys.argv[1:]
    sys.exit(bool_to_exitstatus(run_task(args)))
