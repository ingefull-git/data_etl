import time

import pytest

from ..utils import adapters
from ..utils import queries_request as qr
from ..utils import session_request as sr


@pytest.mark.skip
def test_queries_request_pages_200(global_config, request_args_200):
    t0 = time.time()
    headers, params, payload = request_args_200
    logger, config_file, session, client, url = global_config
    yearid = None
    entities = client.fileList
    payload = {"yearid": yearid} if yearid else None
    headers = {
        "Authorization": "Bearer {0}".format("111222333444"),
        "Content-Type": "application/JSON",
    }
    requestps = sr.RequestRetry(
        session=session,
        method="POST",
        hostname=client.hostname,
        headers=headers,
        logger=logger,
        retry_params={"yearid": 32},
    )
    queryps = qr.QueriesGeneric(
        request=requestps,
        client=client,
        entities=entities,
        streamlimit=101,
        pagelimit=50,
        preadapter=adapters.ps_request_pages_stream_adapter,
        postadapter=adapters.ps_data_to_txt_adapter,
        logger=logger,
    )
    result = queryps.make_query_async()
    # result = queryps.make_query()
    logger.warning("Time: {}".format(round(time.time(), 2) - t0))
    logger.warning("Result: {}".format(result))
    assert result == 4


def test_queries_request_gettoken_getnumpages_pages_200(global_config, request_args_200):
    t0 = time.time()
    headers, params, payload = request_args_200
    logger, config_file, session, client, url = global_config
    token_url = ("/oauth/access_token/",)
    file_list = client.fileList
    tokenpreadapter = adapters.ps_preadapter_token
    tokenpostadapter = adapters.ps_postadapter_token
    pagespreadapter = adapters.ps_preadapter_numpages
    pagespostadapter = adapters.ps_postadapter_numpages
    querypreadapter = adapters.ps_preadapter_data
    querypostadapter = adapters.ps_postadapter_data_to_txt

    requestps = sr.RequestRetry(
        session=session,
        method="POST",
        hostname=client.hostname,
        logger=logger,
        retry_params={"yearid": 32},
    )

    query_token = qr.QueriesGeneric(
        request=requestps,
        client=client,
        entities=token_url,
        preadapter=tokenpreadapter,
        postadapter=tokenpostadapter,
        logger=logger,
    )
    token = query_token.make_query()
    logger.warning("Token: {}".format(token))

    requestps.headers = {
        "Authorization": "Bearer {0}".format(token[0]),
        "Content-Type": "application/JSON",
    }

    query_numpages = qr.QueriesGeneric(
        request=requestps,
        client=client,
        entities=file_list,
        preadapter=pagespreadapter,
        postadapter=pagespostadapter,
        logger=logger,
    )
    num_pages = {k: v for k, v in query_numpages.make_query().items()}
    logger.warning("Pages: {}".format(num_pages))

    queryps = qr.QueriesGeneric(
        request=requestps,
        client=client,
        entities=file_list,
        preadapter=querypreadapter,
        postadapter=querypostadapter,
        logger=logger,
    )
    result = queryps.make_query(asinc=True, num_pages=num_pages, streamlimit=500, pagelimit=50)

    logger.warning("Time: {}".format(round(time.time(), 2) - t0))
    logger.warning("Result: {}".format(result))
    assert result == 4


@pytest.mark.skip
def test_queries_request_pages_generator(global_config, request_args_200):
    headers, params, payload = request_args_200
    logger, config_file, session, client, url = global_config
    yearid = None
    entities = [client.fileList[0]]
    payload = {"yearid": yearid} if yearid else None
    headers = {
        "Authorization": "Bearer {0}".format("111222333444"),
        "Content-Type": "application/JSON",
    }
    requestps = sr.RequestRetry(
        session=session,
        method="POST",
        hostname=client.hostname,
        headers=headers,
        payload=payload,
        logger=logger,
    )
    queryps = qr.QueriesGeneric(
        request=requestps,
        client=client,
        entities=entities,
        streamlimit=10,
        pagelimit=10,
        file_generator=qr.gen_file,
        logger=logger,
    )
    gen_file = queryps.make_queries()
    queryps2 = qr.QueriesGeneric(
        request=requestps,
        client=client,
        entities=gen_file,
        streamlimit=10,
        pagelimit=10,
        file_generator=qr.ps_file,
        logger=logger,
    )
    result = queryps2.make_queries()
    assert result == 9
