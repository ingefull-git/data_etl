VERSION = "1.6.0"
"""
+==============================================================================+
|             PowerQueries API Connection and File Creation Script             |
+==============================================================================+
|    Script: powerQueriesPull_generic.py                                       |
|      date: 2022-05-06                                                        |
+------------------------------------------------------------------------------+
|   Authors Globant Team:                                                      |
|                       - Pantazis, Nicolas Javier                             |
|                       - Chungo, Fabricio                                     |
|                       - Belzunce, Jose Martin                                |
|                       - Sosa, Raul                                           |
|                       - Zavatto, Fernando Esteban                            |
|                       - Rodriguez Quiroga, Alexander Nestor                  |
|                       - Loaeza, Luis                                         |
|                       - Drada Davila, Mauricio                               |
|                       - Morales Sanchez, Alejandro Alfredo                   |
|                       - Gordon, Brian                                        |
|                       - Fuenmayor, David                                     |
|                       - Rodriguez Yanes, Juan Manuel                         |
+------------------------------------------------------------------------------+
| Usage:                                                                       |
|                                                                              |
|   * [] indicates the content is optional.                                    |
|   * {} indicates the content is mandatory and needs to be replaced.          |
|                                                                              |
| +-------------------------------------------------------------------------+  |
| | ptpython /usr/bin/powerQueriesPull_generic.py -f {folder_name} [Options]|  |
| +-------------------------------------------------------------------------+  |
|                                                                              |
| Where:                                                                       |
|   {folder_name} (mandatory) The name of the folder within the /home/ folder  |
|       in the SFTP server where the files for this district are to be placed. |
|   [Options] (optional) can be:                                               |
|       to run the standard demographics data pull:                            |
|           None                                                               |
|       to pull the files in the "attendanceList":                             |
|           -a                                                                 |
|           --attendance                                                       |
|       to pull a single file from any files' list:                            |
|           -s {endpoint_id}                                                   |
|           --single={endpoint_id}                                             |
|       to exclude a file or a list of files from the standard data pull:      |
|           -e {endpoint_id or endpoint_ids list}                              |
|           --exclude={endpoint_id or endpoint_ids list}                       |
|         Where {endpoint_id} is the last node of the endpoint                 |
|         and {endpoint_ids list} is list of last nodes of endpoints           |
|         separated by commas with no spaces.                                  |
|                                                                              |
|         For Example:                                                         |
|           -for /ws/schema/query/com.blackboard.datalink.students.student     |
|                 use "student"                                                |
|           -for /ws/schema/query/com.blackboard.datalink.busroute             |
|                 use "busroute"                                               |
|           -for both                                                          |
|                 use "student,busroute"                                       |
|       to define the logging level:                                           |
|           -l {mode}                                                          |
|           --log {mode}                                                       |
|         Where {mode} in ["debug", "info", "warning", "error", "critical"]    |
|           {mode} is case insensitive, and defaults to "INFO"                 |
|       to run locally:                                                        |
|           -t <config file's name>                                            |
|           --test <config file's name>                                        |
|                                                                              |
| NOTES: Be aware that a single letter as the option parameter DOES NOT        |
| require the equal sign (=) whereas the whole word DOES.                      |
+------------------------------------------------------------------------------+
| Examples of usage:                                                           |
|                                                                              |
| Demographics:                                                                |
|   ptpython powerQueriesPull_generic.py -f 9999                               |
|                                                                              |
| Attendance:                                                                  |
|   ptpython powerQueriesPull_generic.py -f 9999 -a                            |
|   ptpython powerQueriesPull_generic.py -f 9999 --attendance                  |
|                                                                              |
| Single file to process:                                                      |
|   ptpython powerQueriesPull_generic.py -f 9999 -s student                    |
|   ptpython powerQueriesPull_generic.py -f 9999 --single=busroute             |
|                                                                              |
| Multiple files to exclude:                                                   |
|   ptpython powerQueriesPull_generic.py -f 9999 -e parent,staff               |
|   ptpython powerQueriesPull_generic.py -f 9999 --exclude=organizations,staff |
|                                                                              |
| Logging level definition:                                                    |
|   ptpython powerQueriesPull_generic.py -f 9999 -l warning                    |
|   ptpython powerQueriesPull_generic.py -f 9999 --log warning                 |
|                                                                              |
| To run locally:                                                              |
|   ptpython powerQueriesPull_generic.py -t <config file's name>               |
|   ptpython powerQueriesPull_generic.py --test <config file's name>           |
|                                                                              |
| NOTE: All the endpoint_ids must be separated by ',' wihtout spaces.          |
+------------------------------------------------------------------------------+
"""
import datetime as dt
import json
import sys
import time
from utils.get_info import updatedict

from utils import client_info as ci
from utils import configuration
from utils import file_processors as fp
from utils import loggering
from utils import queries_request as qr
from utils import session_request as sr
from utils.adapters import PowerSchoolAdapter
from utils.base import PullGeneric
from utils.decorators import debuglog, for_all_methods

TIMEOUT = 600.0

BASE_YEAR = 1990


@for_all_methods("__init__", debuglog())
class PowerSchoolPull(PullGeneric):
    """
    This class is a subclass of the PullGeneric class, which is a subclass of the Pull class.
    """

    def get_context_data(self, **kwargs):
        """
        It returns a dictionary of the context data.
        """
        kwargs.setdefault("result", {})
        return kwargs

    def get_files_to_pull(self, options):
        """
        It returns a list of files to pull from the remote repository

        :param options: A dictionary of options that were passed to the command
        """
        files_to_pull = self.adapter.client.full_list()
        if options.attendance:
            files_to_pull = self.adapter.client.attendanceList
        elif "NULL" not in options.single:
            files_to_pull = [f for f in files_to_pull if f.split(".")[-1] == options.single]
        return files_to_pull

    def get_token(self, tokenurl):
        """
        This function takes a tokenurl as an argument and returns a token

        :param tokenurl: The URL to get the token from
        """
        t0 = time.time()
        self.query.entities = [tokenurl]
        self.query.preadapter = self.adapter.preadapter_token
        self.query.postadapter = self.adapter.postadapter_token
        result = self.query.make_query()
        if "error" in result["token"]:
            loggering.error_log(msg=result["token"], logger=self.logger)
        else:
            self.logger.debug("Token: {}".format(result["token"]))
            self.logger.debug("Time: {}".format(round(time.time(), 2) - t0))
        updatedict(self.context["result"], result)
        return result.get("token", "")

    def get_request_headers(self, *args, **kwargs):
        """
        It returns the request headers.
        """
        token = kwargs.get("token")
        self.query.request.headers = {
            "Authorization": "Bearer {0}".format(token),
            "Content-Type": "application/JSON",
        }
        return self.query.request.headers

    def get_year_id(self):
        """
        It returns the year id of the current year.
        """
        t0 = time.time()
        self.query.entities = ["/ws/schema/query/com.blackboard.datalink.yearid"]
        self.query.preadapter = self.adapter.preadapter_yearid
        self.query.postadapter = self.adapter.postadapter_yearid
        result = self.query.make_query()
        # TODO: make something when error and no yearid
        self.logger.debug("Time: {}".format(round(time.time(), 2) - t0))
        updatedict(self.context["result"], result)
        return result.get("yearid", "")

    def get_num_pages(self, filelist, yearid):
        """
        Get the number of records that every entity has from the server

        :param filelist: a list of filenames to be processed
        """
        t0 = time.time()
        self.query.entities = filelist
        self.query.preadapter = self.adapter.preadapter_numpages
        self.query.postadapter = self.adapter.postadapter_numpages
        self.query.request.retry_params = {"payload": {"yearid": yearid}}
        result = self.query.make_query()
        # TODO: make something when error and no NUM_PAGES
        self.logger.debug("Time: {}".format(round(time.time(), 2) - t0))
        updatedict(self.context["result"], result)
        return result

    def get_files(self, filelist, numpages):
        """
        This function takes a list of files and a number of pages and returns a list of files that have the same number of
        pages

        :param filelist: a list of files to be processed
        :param numpages: the number of pages to be processed
        """
        t0 = time.time()
        self.query.entities = filelist
        self.query.preadapter = self.adapter.preadapter_data
        self.query.postadapter = self.adapter.postadapter_data_to_txt
        result = self.query.make_query(
            num_pages=numpages, records_per_page=5000, stream_threshold=10
        )
        self.logger.debug("Time: {}".format(round(time.time(), 2) - t0))
        updatedict(self.context["result"], result)
        return result

    def review_tmp_files(self, filelist):
        """
        > This function takes a list of files

        :param filelist: a list of files to be reviewed
        """
        t0 = time.time()
        result = {}
        for file in filelist:
            filename = file.split(".")[-1]
            ori_file_size, new_file_size = fp.review_temporary_file(
                filename=filename, logger=self.logger
            )
            result[filename] = {"file_sizes": {"original": ori_file_size, "new": new_file_size}}
        tt = round(time.time() - t0, 2)
        total_time = "Time: {}".format(dt.timedelta(seconds=tt)).split(".")[0]
        self.logger.debug(total_time)
        updatedict(self.context["result"], result)
        return result

    def run(self, *args, **kwargs):
        """
        A function that takes in a variable number of arguments and keyword arguments.
        """
        try:
            t0 = time.time()
            options = kwargs.get("options", "")
            files_to_pull = self.get_files_to_pull(options)
            token = self.get_token(tokenurl=self.adapter.client.tokenUrl)
            req_headers = self.get_request_headers(token=token)
            yearid = self.get_year_id()
            num_pages = self.get_num_pages(filelist=files_to_pull, yearid=yearid)
            files = self.get_files(filelist=files_to_pull, numpages=num_pages)
            review = self.review_tmp_files(filelist=files_to_pull)
            file_json = json.dumps(self.context["result"], indent=4)
            self.logger.info("Final pull results: {}".format(file_json))
            tt = round(time.time() - t0, 2)
            total_time = "Time: {}".format(dt.timedelta(seconds=tt)).split(".")[0]
            self.logger.info(total_time)
        except Exception as exc:
            loggering.except_log(exc, logger=self.logger)


def main():
    """
    A function that prints the string "Hello World"
    """
    t0 = time.time()
    log_level = configuration.get_log_level()
    logger = loggering.LoggerPowerSchool(log_level=log_level).get_logger()
    logger2 = loggering.LoggerPowerSchool(file_name="debug.log", name="PowerSchoolPull").get_logger(
        file_level="INFO"
    )
    loggering.start_log(version=VERSION, logger=logger)
    session = sr.session_retry(logger=logger)
    options = configuration.get_opts_and_args(args=sys.argv[1:])
    config_file = configuration.get_config_file(options=options, logger=logger)
    client = ci.ClientPowerSchool(config_file=config_file)
    request_ps = sr.RequestRetryPowerSchool(
        session=session, method="POST", hostname=client.hostname, logger=logger
    )
    query_ps = qr.QueriesPowerSchool(request=request_ps, logger=logger)
    adapter = PowerSchoolAdapter(client=client, query=query_ps, logger=logger)
    ps_pull = PowerSchoolPull(logger=logger2, adapter=adapter)
    ps_pull.run(options=options)
    tt = round(time.time() - t0, 2)
    total_time = "Time: {}".format(dt.timedelta(seconds=tt)).split(".")[0]
    logger.info(total_time)


if __name__ == "__main__":
    main()
