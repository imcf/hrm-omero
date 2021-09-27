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

    try:
        return argparser.parse_args(args)
    except IOError as err:
        argparser.error(str(err))


def run_task(args):
    """Parse commandline arguments and initiate the requested tasks."""
    args = parse_arguments(args)

    # one of the downsides of loguru is that the level of an existing logger can't be
    # changed - so to adjust verbosity we actually need to remove the default logger and
    # re-add it with the new level (see https://github.com/Delgan/loguru/issues/138)
    log_level = "WARNING"  # no verbosity flag has been provided -> use "WARNING"
    if args.verbosity > 3:  # -vvvv (4) and more will result in "TRACE"
        log_level = "TRACE"
    if args.verbosity == 3:  # -vvv will be "DEBUG"
        log_level = "DEBUG"
    elif args.verbosity == 2:  # -vv will be "INFO"
        log_level = "INFO"
    elif args.verbosity == 1:  # -v will be "SUCCESS"
        log_level = "SUCCESS"
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
    if args.password:
        log.warning("Using the '--password' parameter is deprecated!")
        passwd = args.password
    if not passwd:
        msg = "ERROR: no password given to connect to OMERO!"
        print(msg)
        log.error(msg)
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
        conn.connect()
        group = conn.getGroupFromContext()
        log.info(f"New OMERO connection [user={args.user}].")
        log.debug(f"The user's default group is {group.getId()} ({group.getName()}).")

        if args.action == "checkCredentials":
            return dotomero.check_credentials(conn)

        if args.action == "retrieveChildren":
            return formatting.print_children_json(conn, args.id)

        if args.action == "OMEROtoHRM":
            return transfer.from_omero(conn, args.imageid, args.dest)

        if args.action == "HRMtoOMERO":
            return transfer.to_omero(conn, args.dset, args.file, omero_logfile)

        raise Exception("Huh, how could this happen?!")
    finally:
        conn.close()
        log.info(f"Closed OMERO connection [user={args.user}].")


@log.catch
def main(args=None):
    """Wrapper to call the run_task() function and return its exit code."""
    if not args:
        args = sys.argv[1:]
    sys.exit(bool_to_exitstatus(run_task(args)))
