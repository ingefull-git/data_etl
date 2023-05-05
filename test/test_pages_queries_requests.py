from ast import Raise
import mock
from requests import head, request

from ..powerQueriesPull_generic import *
from PowerSchool import powerQueriesPull_generic
import os
import pytest
from datetime import datetime
from mockfactory import MockFactory


#@pytest.mark.skip
def test_pages_queries_request_without_yearid(global_config):
    logger, config_file, session, client = global_config
    result = pages_queries_request(session, client, client.file_list, yearid=None)
    assert os.path.exists(os.getcwd() + "/student.txt")
    assert isinstance(result, dict)
    assert isinstance(result["student"], list)
    assert result["student"][0] == 3
    log_time = datetime.strptime(result["student"][1], "%H:%M:%S.%f")
    assert isinstance(log_time, datetime)
    expected_header = "organizationid	organizationinternalID	studentid	studentinternalID	lastName	firstName	middleName	preferredName	webLoginID	password	birthDate	gender	gradeLevel	gradYear	track	preferredLanguage1ID	address1	address2	city	state	zip	emailAddress	phoneNumber"
    expected_line = "4020		84597		Garcia	Caitlin	Micah		James_Knight		2013-05-05	F	3	2031			991 Carpenter Rest Apt. 434   East Alejandro, KY 18283		Liberty	MO	64068"
    expected_trailer = "7500		110737		Parrish	Jo	Paul		Mary_Noble		2018-01-31	M	-1	2035			PSC 3961, Box 6210   APO AA 41578		Liberty	MO	64068		55556666"
    with open(os.getcwd() + "/student.txt", "r") as s:
        lines = s.readlines()

    assert len(lines) == 12943
    assert lines[0].strip() == expected_header
    assert lines[10050].strip() == expected_line
    assert lines[-1].strip() == expected_trailer


#@pytest.mark.skip
def test_pages_queries_request_with_yearid(global_config):
    logger, config_file, session, client = global_config
    result = pages_queries_request(session, client, client.by_year_list, yearid=31)
    assert os.path.exists(os.getcwd() + "/section.txt")
    assert isinstance(result, dict)
    assert isinstance(result["section"], list)
    assert result["section"][0] == 2
    log_time = datetime.strptime(result["section"][1], "%H:%M:%S.%f")
    assert isinstance(log_time, datetime)
    expected_header = "organizationid	organizationinternalID	sectionid	sectioninternalID	courseid	period	number	teacherid	teacherinternalID	room	url	termid"
    expected_line = "1070	20	191215		SS03156100	3(A-B)	3	04298	488	817		3101"
    expected_trailer = "4220	27	197261		ZZ99999999	9(A-E)	057	11642	31318	308		3100"
    with open(os.getcwd() + "/section.txt", "r") as s:
        lines = s.readlines()

    assert len(lines) == 9046
    assert lines[0].strip() == expected_header
    assert lines[3720].strip() == expected_line
    assert lines[-1].strip() == expected_trailer


#@pytest.mark.skip
def test_pages_queries_request_500(global_config):
    logger, config_file, session, client = global_config
    result = pages_queries_request(session, client, client.by_year_list, yearid=666)
    assert result == {
        "section": [
            "With payload",
            "Status code: 500",
            "With payload",
            "TypeError",
            "With payload",
            "Status code: 500",
            "With payload",
            "TypeError",
        ]
    }


#@pytest.mark.skip
@mock.patch.object(powerQueriesPull_generic, "getnum_pages", return_value=1)
@mock.patch.object(powerQueriesPull_generic.requests, "session")
def test_pages_queries_request_timeout_exception(mock_session, mock_pages, response_422, response_read_timeout, response_200_with_content, response_retry_exception, global_config):
    logger, config_file, session, client = global_config
    mock_object = MockFactory(status = [response_422, response_read_timeout, response_200_with_content, response_read_timeout, response_200_with_content, response_422, response_retry_exception, response_200_with_content, response_retry_exception, response_200_with_content])
    mock_session.post.side_effect = mock_object.side_effects
    result = pages_queries_request(mock_session, client, client.by_year_list, yearid=31)
    args = mock_session.post.call_args_list
    assert result["section"][0] == 1
    log_time = datetime.strptime(result["section"][1], "%H:%M:%S.%f")
    assert isinstance(log_time, datetime)
    # Timeout without payload
    result = pages_queries_request(mock_session, client, client.by_year_list, yearid=31)
    assert result["section"][0] == 1
    log_time = datetime.strptime(result["section"][1], "%H:%M:%S.%f")
    assert isinstance(log_time, datetime)


#@pytest.mark.skip
@mock.patch.object(powerQueriesPull_generic, "getnum_pages", return_value=1)
@mock.patch.object(powerQueriesPull_generic.requests, "session")
def test_mock_factory_exception_retry(mock_session, mock_pages, response_retry_exception, response_404, global_config):
    logger, config_file, session, client = global_config
    mock_object = MockFactory(status=[response_404,response_retry_exception])
    mock_session.post.side_effect = mock_object.side_effects
    result = pages_queries_request(mock_session, client, client.by_year_list, yearid=31)
    assert 'RetryError' in result.values()[0]
    assert 'Status code: 404' in result.values()[0]

#@pytest.mark.skip
@mock.patch.object(powerQueriesPull_generic, "getnum_pages", return_value=1)
@mock.patch.object(powerQueriesPull_generic.requests, "session")
def test_mock_factory_exception_retry_200(mock_session, mock_pages, response_retry_exception, response_200,global_config):
    logger, config_file, session, client = global_config
    mock_object = MockFactory(status=[response_retry_exception, response_200])
    mock_session.post.side_effect = mock_object.side_effects
    result = pages_queries_request(mock_session, client, client.by_year_list, yearid=31)
    assert result.values()[0][0] == 1

#@pytest.mark.skip
@mock.patch.object(powerQueriesPull_generic, "getnum_pages", return_value=1)
@mock.patch.object(powerQueriesPull_generic.requests, "session")
def test_mock_factory_code_200(mock_session, mock_pages, response_404, global_config):
    logger, config_file, session, client = global_config
    mock_object = MockFactory(status=[response_404])
    mock_session.post.side_effect = mock_object.side_effects
    result = pages_queries_request(mock_session, client, client.by_year_list, yearid=31)
    assert 'Status code: 404' in result.values()[0]


##@pytest.mark.skip
@mock.patch.object(powerQueriesPull_generic, "getnum_pages", return_value=110)
@mock.patch.object(powerQueriesPull_generic.requests, "session")
def test_mock_pages_queries_page_count_gt_100(mock_session, mock_getnum, global_config, response_200):
    logger, config_file, session, client = global_config
    mock_object = MockFactory(status=[response_200])
    mock_session.post.side_effect = mock_object.side_effects
    result = pages_queries_request(mock_session, client, client.by_year_list, yearid=31)
    assert result.values()[0][0] == 110


##@pytest.mark.skip
@mock.patch.object(powerQueriesPull_generic, "getnum_pages", return_value=110)
@mock.patch.object(powerQueriesPull_generic.requests, "session")
def test_mock_pages_queries_page_count_gt_100_with_payload(mock_session, mock_getnum, global_config, response_200, response_404):
    logger, config_file, session, client = global_config
    mock_object = MockFactory(status=[response_404, response_200])
    mock_session.post.side_effect = mock_object.side_effects
    result = pages_queries_request(mock_session, client, client.by_year_list, yearid=31)
    assert result.values()[0][0] == 110