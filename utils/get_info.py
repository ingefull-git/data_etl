import datetime
import collections

from utils import loggering
from utils.decorators import debuglog


@debuglog()
def get_file_type_headers(client, entity, logger):
    """
    This function returns a list of headers for a given entity

    :param client: The client object that you created in the previous step
    :param entity: The entity that you want to get the headers for
    :param logger: a logger object
    """
    headers = []
    if '{}.txt'.format(entity) in client.headerDict:
        headers = client.headerDict.get('{}.txt'.format(entity))
        logger.debug('Headers for entity {} are: {}'.format(entity, headers))
    else:
        logger.warning('Could not find valid headers for the {0} file.'.format(entity))
    return headers


@debuglog()
def settle_year_range(rollover_date, logger):
    """
    Given a rollover date, return a list of years that the rollover date falls within

    :param rollover_date: the date of the last day of the year
    :param logger: a logger object
    """
    year_range = ''
    today = datetime.date.today()
    if rollover_date == '':
        loggering.error_log('Please define a roll-over date', exc_info=True)
    if today < rollover_date:
        current_year = today.year
        previous_year = current_year - 1
        year_range = ('{0}-{1}').format(previous_year, current_year)
    else:
        current_year = today.year
        next_year = current_year + 1
        year_range = ('{0}-{1}').format(current_year, next_year)
    return year_range


def updatedict(d, u):
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
            d[k] = updatedict(d.get(k, {}), v)
        else:
            d[k] = v
    return d