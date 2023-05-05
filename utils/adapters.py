import decimal as dec
import time
from datetime import datetime

import loggering
from base import AdapterGeneric

from utils import file_processors as fp
from utils import get_info as gi


# @for_all_methods(['__init__'], debuglog())
class PowerSchoolAdapter(AdapterGeneric):
    """
    This class is a generic adapter for the PowerSchool API
    """

    def get_context_data(self, **kwargs):
        """
        It returns a dictionary of the context data.
        """
        kwargs.setdefault("headers", {})
        kwargs.setdefault("payload", {})
        kwargs.setdefault("pages", {})
        kwargs.setdefault("result", {})
        return kwargs

    def preadapter_token(self, *args, **kwargs):
        """
        This function takes in a string and returns a list of tokens
        """
        # self.context['result'] = {}
        entity = args[0]
        request = []
        if "token" in entity and not self.query.request.headers:
            entity_name = "token"
            params = {
                "grant_type": "client_credentials",
                "client_id": self.client.clientId,
                "client_secret": self.client.clientSecret,
            }
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            payload = {}
            request.append(
                {
                    "payload": payload,
                    "params": params,
                    "headers": headers,
                    "url": entity,
                    "entity_name": entity_name,
                }
            )
        return request

    def postadapter_token(self, *args, **kwargs):
        """
        A function that takes in a self parameter and any number of arguments and keyword arguments.
        """
        try:
            response, request = kwargs.get("response")
            entity = request.get("entity_name")
            self.context["result"][entity] = response.json()["access_token"]
        except Exception as exc:
            self.context["result"][entity] = {
                "error": "No access_token in the response: {}".format(exc)
            }
            loggering.error_log(msg=exc)
        return self.context["result"]

    def preadapter_yearid(self, *args, **kwargs):
        """
        This function takes a yearid and returns a list of all the preadapter ids for that year
        """
        # self.context['result'] = {}
        entity = args[0]
        request = []
        if "yearid" in entity:
            entity_name = "yearid"
            rollover_month_day = self.client.get("rollover_month_day", "08/01")
            try:
                cutover_date = "{0}/{1}".format(rollover_month_day, datetime.today().year)
                rollover_date = datetime.strptime(cutover_date, "%m/%d/%Y").date()
                self.context["rollover_date"] = rollover_date
            except Exception as err:
                loggering.error_log(
                    'Invalid roll-over date entered, please format "mm/dd", received: {0}, {1}'.format(
                        rollover_month_day, err
                    ),
                    logger=self.logger,
                )
            year_range = gi.settle_year_range(rollover_date=rollover_date, logger=self.logger)
            payload = {"yearrange": year_range}
            request.append({"payload": payload, "url": entity, "entity_name": entity_name})
        return request

    def postadapter_yearid(self, *args, **kwargs):
        """
        A function that takes in a self, *args, and **kwargs.
        """
        today = datetime.today().date()
        yearid = today.year - 1990 if today > self.context["rollover_date"] else today.year - 1991
        try:
            response, request = kwargs.get("response")
            entity = request.get("entity_name")
            yearid = response.json()["record"][0]["yearid"]
        except KeyError as exc:
            self.logger.debug(msg="Could not find yearid: {}".format(exc))
        except Exception as exc:
            self.context["result"][entity] = {"error": "No yearid in the response: {}".format(exc)}
            loggering.error_log(msg=exc)
        self.context["yearid"] = yearid
        self.context["result"][entity] = yearid
        return self.context["result"]

    def preadapter_numpages(self, *args, **kwargs):
        """
        It returns the number of pages in a PDF file
        """
        # self.context['result'] = {}
        entity = args[0]
        request = []
        entity_name = entity.split(".")[-1]
        url = "{}{}".format(entity, "/count")
        request.append({"url": url, "count": 0, "entity_name": entity_name})
        return request

    def postadapter_numpages(self, *args, **kwargs):
        """
        It returns the number of pages in the post
        """
        response, request = kwargs.get("response")
        entity_name = request.get("entity_name")
        self.context["payload"][entity_name] = request.get("payload", {})
        self.context["result"][entity_name] = {"count": response.json()["count"]}
        self.logger.debug(
            "{} has {} records.".format(entity_name, self.context["result"][entity_name])
        )
        return self.context["result"]

    def preadapter_data(self, *args, **kwargs):
        """
        This function takes a list of pages and returns a list of pages
        """
        context = kwargs.get("context", "")
        request = {}
        entity = args[0]
        entity_name = entity.split(".")[-1]
        json_filename = "{}.json.tmp".format(entity_name)
        txt_filename = "{}.txt.tmp".format(entity_name)
        self.context["result"][entity_name]["error_file"] = []
        num_records = dec.Decimal(context["num_pages"][entity_name]["count"])
        num_pagelimit = dec.Decimal(context["records_per_page"])
        pagenum = (
            int(
                dec.Decimal(num_records / num_pagelimit).quantize(
                    dec.Decimal("0"), rounding=dec.ROUND_UP
                )
            )
            if entity_name in context["num_pages"]
            else 1
        )
        stream = pagenum > context["stream_threshold"]
        txt_file_deleted = fp.check_and_delete_file(full_filename=txt_filename, logger=self.logger)
        json_file_deleted = fp.check_and_delete_file(
            full_filename=json_filename, logger=self.logger
        )
        if stream:
            if not (json_file_deleted and txt_file_deleted):
                self.context["result"][entity_name]["error_file"] = list(
                    "" if json_file_deleted else json_filename,
                    "" if txt_file_deleted else txt_filename,
                )
        else:
            if not txt_file_deleted:
                self.context["result"][entity_name]["error_file"] = list(
                    "" if txt_file_deleted else txt_filename
                )
        pages = 1 if stream else pagenum
        url = "{}".format(entity)
        self.context["headers"][entity_name] = gi.get_file_type_headers(
            client=self.client, entity=entity_name, logger=self.logger
        )
        payload = self.context["payload"][entity_name]
        self.context["result"][entity_name].update(
            {"stream": 0, "records": 0} if stream else {"pages": 0, "records": 0}
        )
        self.context["result"][entity_name].update(
            {"payload": self.context["payload"][entity_name]}
        )
        if json_file_deleted and txt_file_deleted:
            request = [
                {
                    "payload": payload,
                    "params": {
                        "page": page,
                        "pagesize": 0 if stream else context["records_per_page"],
                    },
                    "url": url,
                    "entity_name": entity_name,
                    "stream": stream,
                }
                for page in range(1, pages + 1)
            ]
        self.context["pages"][entity_name] = pages
        return request or []

    def postadapter_data_to_txt(self, *args, **kwargs):
        """
        It takes a stream of pages and converts them to text.
        """
        response, request = kwargs.get("response")
        entity_name = request.get("entity_name")
        t1 = time.time()
        try:
            if request["stream"]:
                chunks_count = fp.stream_to_json(
                    response=response, entity=entity_name, logger=self.logger
                )
                if chunks_count:
                    records_count = fp.json_to_txt(
                        headers=self.context["headers"][entity_name],
                        entity=entity_name,
                        logger=self.logger,
                    )
                self.context["result"][entity_name]["stream"] += 1
                self.context["result"][entity_name]["records"] += records_count
            else:
                data = response.json()["record"]
                records_count = fp.pages_to_txt(
                    headers=self.context["headers"][entity_name],
                    data=data,
                    entity=entity_name,
                    logger=self.logger,
                )
                self.logger.debug(
                    "Page {0} out of {1} successfully created for {2} with {3} records.".format(
                        request["params"]["page"],
                        self.context["pages"][entity_name],
                        entity_name,
                        records_count,
                    )
                )
                self.context["result"][entity_name]["pages"] += 1
                self.context["result"][entity_name]["records"] += records_count
        except Exception as e:
            print(e)
            records_count = 0
        return self.context["result"]
