import os
import sys
from optparse import OptionParser

import loggering


def get_log_level():
    """
    It returns the log level for the script
    :return: The log level.
    """
    log_type = False
    # local_environment = False
    log_level = "INFO"
    for arg in sys.argv:
        if log_type:
            log_level = arg.upper()
        if arg == "-l" or arg == "--log":
            log_type = True

    if log_level not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
        log_level = "INFO"

    return log_level


def get_site_folder(folder):
    """
    It takes a folder name and returns the full path to that folder

    :param folder: The folder that the site is in
    """
    if os.path.exists("/home/{}".format(folder)):
        return folder
    else:
        return None


def get_config_file(options, logger):
    """
    It returns the config file.

    :param options: A dictionary of options that were passed to the script
    :param logger: a logger object
    """
    if "NULL" not in options.test:
        file_path = options.test
        config_file = os.getcwd() + "/" + file_path
        if not os.path.exists(config_file):
            loggering.error_log(
                msg="Configuration file does not exist in the defined path: {0}".format(
                    config_file
                ),
                logger=logger,
            )

    else:
        site_folder = get_site_folder(options.folder)
        if site_folder:
            rootdir = "/home/{}".format(
                site_folder if "/" not in site_folder else site_folder.split("/")[0]
            )
            config_file = "{}/{}.json".format(
                rootdir,
                "." + site_folder
                if "/" not in site_folder
                else "/.".join(site_folder.split("/")[::-1]),
            )
        else:
            loggering.error_log(
                msg="Configuration file does not exist on the site folder: {0}".format(config_file),
                logger=logger,
            )

    return config_file


def get_opts_and_args(args):
    """
    It takes a list of strings, and returns a tuple of two lists of strings

    :param args: The command line arguments
    """
    parser = OptionParser()
    parser.add_option(
        "-a",
        "--attendance",
        action="store_true",
        dest="attendance",
        default=False,
        help="Send only attendance messaging files (not including history)",
    )

    parser.add_option(
        "-s",
        "--single",
        dest="single",
        default="NULL",
        type="string",
        help="Send only one specified file.  SINGLE should match endpoint including case. EXAMPLE: /ws/schema/query/com.blackboard.datalink.daily  SINGLE=daily",
    )

    parser.add_option(
        "-e",
        "--exclude",
        dest="exclude",
        default="NULL",
        type="string",
        help="Exclude the specified endpoints, separated by comas WITHOUT SPACES. EXAMPLE: --exclude history,staff",
    )

    parser.add_option(
        "-f",
        "--folder",
        dest="folder",
        default="NULL",
        help="This is the numeric folder name for this district, not used as option, but among the args",
    )

    parser.add_option(
        "-l",
        "--log",
        dest="log_level",
        default="NULL",
        help='Set the desired log level, defaults to "INFO". Valid options are: "DEBUG", "INFO", "WARNING", "ERROR" and "CRITICAL".',
    )

    parser.add_option(
        "-t",
        "--test",
        dest="test",
        default="NULL",
        help="Run the script in a development environment. The option is the config file's name.",
    )

    options, _ = parser.parse_args()
    return options
