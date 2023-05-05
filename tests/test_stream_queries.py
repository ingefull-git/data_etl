import os

import mock
import pytest
from mockfactory import MockFactory
from PowerSchool import powerQueriesPull_generic

from ..powerQueriesPull_generic import *


# @pytest.mark.skip
@mock.patch.object(powerQueriesPull_generic, "json_to_txt")
@mock.patch.object(powerQueriesPull_generic, "stream_to_json")
def test_stream_queries_200(mock_json, mock_json_txt, response_200, global_config):
    logger, config_file, session, client = global_config
    mock_object = MockFactory(status=[response_200], stream=True)
    mock_json.side_effect = mock_object.side_effects
    mock_json_txt.return_value = None
    req = stream_queries_request(session, client, client.stream_list, yearid=99)
    assert req.values()[0][0] == "200"


# @pytest.mark.skip
@mock.patch.object(powerQueriesPull_generic, "json_to_txt")
@mock.patch.object(powerQueriesPull_generic, "stream_to_json")
def test_stream_queries_404(mock_json, mock_json_txt, response_404, global_config):
    logger, config_file, session, client = global_config
    mock_object = MockFactory(status=[response_404], stream=True)
    mock_json.side_effect = mock_object.side_effects
    mock_json_txt.return_value = None
    req = stream_queries_request(session, client, client.stream_list, yearid=99)
    assert req.values()[0][0] == "HTTP error: 404 Client Error: None for url: None"


# @pytest.mark.skip
@mock.patch.object(powerQueriesPull_generic, "json_to_txt")
@mock.patch.object(powerQueriesPull_generic, "stream_to_json")
def test_stream_queries_404_200(
    mock_json, mock_json_txt, response_404, response_200, global_config
):
    logger, config_file, session, client = global_config
    mock_object = MockFactory(status=[response_404, response_200], stream=True)
    mock_json.side_effect = mock_object.side_effects
    mock_json_txt.return_value = None
    req = stream_queries_request(session, client, client.stream_list, yearid=99)
    args = mock_json.call_args_list
    assert len(args) == 2
    assert req.values()[0][0] == "200"


# @pytest.mark.skip
@mock.patch.object(powerQueriesPull_generic, "json_to_txt")
@mock.patch.object(powerQueriesPull_generic, "stream_to_json")
def test_stream_queries_readtimeout(
    mock_json, mock_json_txt, response_read_timeout, response_200, global_config
):
    logger, config_file, session, client = global_config
    mock_object = MockFactory(status=[response_read_timeout, response_200], stream=True)
    mock_json.side_effect = mock_object.side_effects
    mock_json_txt.return_value = None
    req = stream_queries_request(session, client, client.stream_list, yearid=99)
    args = mock_json.call_args_list
    assert len(args) == 2
    assert req.values()[0][0] == "200"


# @pytest.mark.skip
@mock.patch.object(powerQueriesPull_generic, "json_to_txt")
@mock.patch.object(powerQueriesPull_generic, "stream_to_json")
def test_stream_queries_404_timeout_200(
    mock_json, mock_json_txt, response_404, response_200, response_read_timeout, global_config
):
    logger, config_file, session, client = global_config
    mock_object = MockFactory(
        status=[response_404, response_read_timeout, response_200], stream=True
    )
    mock_json.side_effect = mock_object.side_effects
    mock_json_txt.return_value = None
    req = stream_queries_request(session, client, client.stream_list, yearid=99)
    args = mock_json.call_args_list
    assert len(args) == 3
    assert req.values()[0][0] == "200"


# @pytest.mark.skip
@mock.patch.object(powerQueriesPull_generic, "json_to_txt")
@mock.patch.object(powerQueriesPull_generic, "stream_to_json")
def test_stream_queries_retry_exception(
    mock_json, mock_json_txt, response_retry_exception, response_200, global_config
):
    logger, config_file, session, client = global_config
    mock_object = MockFactory(status=[response_retry_exception], stream=True)
    mock_json.side_effect = mock_object.side_effects
    mock_json_txt.return_value = None
    req = stream_queries_request(session, client, client.stream_list, yearid=99)
    args = mock_json.call_args_list
    assert len(args) == 1
    assert "RetryError" in req.values()[0][0]


@mock.patch.object(powerQueriesPull_generic.requests, "session")
def test_stream_to_json_200(mock_session, response_200, global_config):
    logger, config_file, session, client = global_config
    mock_object = MockFactory(status=[response_200])
    mock_session.post.return_value.__enter__.side_effect = mock_object.side_effects
    result = stream_to_json(
        mock_session, client, "query_url", "params", "student", 10000.00, yearid_payload=None
    )
    assert result == 200
    assert os.path.exists("student.txt.json")
    with open("student.txt.json", "r") as file:
        content = file.read()
    assert content == '{"record": "content"}'


@pytest.mark.skip(
    "Skipped because r.raise_for_status()	raises an exception and interrupts the test"
)
@mock.patch.object(powerQueriesPull_generic.requests, "session")
def test_stream_to_json_404(mock_session, response_404, global_config):
    logger, config_file, session, client = global_config
    mock_object = MockFactory(status=[response_404])
    mock_session.post.return_value.__enter__.side_effect = mock_object.side_effects
    result = stream_to_json(
        mock_session, client, "query_url", "params", "student", 10000.00, yearid_payload=None
    )
    assert result == 404
