
import mock
import pytest
from PowerSchool.utils.mockfactory import MockFactory

from ..utils import session_request
from ..utils.session_request import RequestRetry


# @pytest.mark.skip
def test_request_generic_200(request_args_200, global_config):
    headers, params, payload = request_args_200
    logger, config_file, session, client, url = global_config
    headers, params, payload = request_args_200
    args = {
        "entity_name": "section",
        "stream": False,
        "url": "/ws/schema/query/com.blackboard.datalink.section",
        "params": {"page": 1, "pagesize": 5},
        "file_headers": [
            "organizationid",
            "organizationinternalID",
            "sectionid",
            "sectioninternalID",
            "courseid",
            "period",
            "number",
            "teacherid",
            "teacherinternalID",
            "room",
            "url",
            "termid",
        ],
        "payload": {"yearid": 32},
    }
    requestretry = RequestRetry(
        session=session,
        method="POST",
        hostname=client.hostname,
        headers=headers,
        logger=logger,
        retry_params={"yearid": 32},
    )
    response = requestretry.make_request(context=args, stream=False, timeout=600.0)
    json_response = response.json()
    print(json_response)
    assert response.status_code == 200
    assert json_response["name"] == "sections"
    assert len(json_response["record"]) == 1


@pytest.mark.skip
def test_request_generic_404(request_args_404, global_config):
    logger, config_file, session, client, url = global_config
    headers, params, payload = request_args_404
    requestretry = RequestRetry(
        session=session,
        method="POST",
        hostname=client.hostname + url,
        headers=headers,
        payload=payload,
        logger=logger,
    )
    response = requestretry.make_request(stream=False, timeout=600.0)
    assert response.status_code == 404
    assert "Not Found" in response.text


@pytest.mark.skip
@mock.patch.object(session_request, "session_retry")
def test_request_generic_timeout_exception(
    mock_session, request_args_404, response_read_timeout, global_config
):
    logger, config_file, session, client, url = global_config
    headers, params, payload = request_args_404
    requestretry = RequestRetry(logger=logger)
    mock_object = MockFactory(status=[response_read_timeout])
    mock_session.return_value.request.return_value.__enter__.side_effect = mock_object.side_effects
    requestretry = RequestRetry(logger=logger)
    response = requestretry.make_request(
        "POST",
        url=url,
        headers=headers,
        params=params,
        payload=payload,
        stream=False,
        timeout=600.0,
    )
    assert response.status_code == 408
    assert "Timeout" in response.text
