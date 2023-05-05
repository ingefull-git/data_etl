import json
import mmap
import os
import re
import shutil
import sys
import time

from utils import loggering
from decorators import debuglog

CHUNK_SIZE = 2 ** 13
BUFFERING = 2 ** 21
BATCH = 5000


@debuglog()
def stream_to_json(response, entity, logger):
    """
    It takes a response object, an entity name, and a logger object, and writes the response to a file in chunks

    :param response: the response from the API call
    :param entity: the name of the entity you're downloading
    :param logger: a logger object
    :return: The index of the last chunk.
    """
    t1 = time.time()
    try:
        with open('{}.json.tmp'.format(entity), 'wb') as f:
            for index, chunk in enumerate(response.iter_content(chunk_size=CHUNK_SIZE)):
                f.write(chunk)
                if index % BATCH == 0:
                    logger.debug('Chunks: {}'.format(index))
            logger.debug('Index: {}.'.format(index))
    except Exception as exc:
        print(exc)
        loggering.except_log(exc, logger)
        index = 0
    return index


def dict_to_record(record_dict, headers, logger=None):
    """
    It's replacing new lines and tabs with spaces

    :param record_dict: A dictionary of the record.  The keys are the headers and the values are the values
    :param headers: a list of headers that you want to use in the output file
    :param logger: a logger object
    :return: A string of the record_list joined by tabs.
    """
    record_list = []
    for header in headers:
        if header in record_dict:
            try:
                field = record_dict.get(header).replace('\r\n', '   ').replace('\n', '   ').replace('\t', ' ').replace('"', '').replace("'", '')
                record_list.append(field.encode('utf-8'))
            except:
                e = sys.exc_info()[0]
                loggering.except_log('Error: {0}.  Value: {1}'.format(e, field))
                record_list.append(''.encode('utf-8'))
        else:
            record_list.append(''.encode('utf-8'))
    return '\t'.join(record_list)+'\n'


@debuglog()
def pages_to_txt(headers, data, entity, logger):
    """
    This function takes in a list of headers, a list of data, and an entity name, and writes the data to a text file

    :param headers: a list of headers for the data
    :param data: a list of dictionaries, each dictionary is a page of data
    :param entity: the name of the entity you're scraping
    :param logger: a logger object
    """
    initial_time = time.time()
    overlooked_records = 0
    headers = headers
    lower_headers = [header.lower() for header in headers]

    with open('{}.txt.tmp'.format(entity), 'ab') as temp_file:
        temp_file.write('\t'.join([header.encode('utf-8') for header in headers])+'\n')

        try:
            for index, record_dict in enumerate(data, start=1):
                record = dict_to_record(record_dict=record_dict, headers=lower_headers, logger=logger)
                temp_file.write(record)
            # logger.info('Page created with {} records.'.format(index))
        except Exception as err:
            loggering.except_log('{0} file created with 0 records'.format(entity.upper()), str(err))
    return index


@debuglog()
def pages_to_gen(headers, data, file_name, logger):
    """
    This function takes in a list of headers, a list of data, a file name, and a logger, and returns a list of dictionaries

    :param headers: a list of strings that will be used as the headers for the table
    :param data: a list of dictionaries, each dictionary is a row of data
    :param file_name: the name of the file to be generated
    :param logger: a logger object
    """
    headers = headers
    lower_headers = [header.lower() for header in headers]
    yield('\t'.join([header.encode('utf-8') for header in headers])+'\n')
    try:
        index = 0
        while data:
            record_dict = data.next()
            index += 1
            record = dict_to_record(record_dict=record_dict, headers=lower_headers, logger=logger)
            yield(record)
        logger.info('Page created with {} records.'.format(index))
    except Exception as err:
        loggering.except_log('{0} file created with 0 records'.format(file_name.upper()), str(err))


@debuglog()
def json_to_txt(headers, entity, logger=None):
    """
    It converts a json file to a txt file.

    :param headers: a list of strings that are the headers for the output file
    :param entity: the name of the entity you want to convert
    :param logger: a logger object
    """
    initial_time = time.time()
    headers = headers
    lower_headers = [header.lower() for header in headers]
    with open('{}.json.tmp'.format(entity), mode='r+b', buffering=BUFFERING) as json_file:
        try:
            mmap_json = mmap.mmap(json_file.fileno(), 0, access=mmap.ACCESS_READ)
            logger.debug('File mapped succesfully')
            items = re.finditer(b'(?<=[,\[])\{\"[a-zA-Z0-9\-_]+\":\s?\".*?\"\}(?=[,\]])', mmap_json)
            if any(items):
                logger.debug('Items found succesfully')
                overlooked_records = 0
                # reinitialize items because "any(items)" consumed the first record 
                data = re.finditer(b'(?<=[,\[])\{\"[a-zA-Z0-9\-_]+\":\s?\".*?\"\}(?=[,\]])', mmap_json)
                with open('{}.txt.tmp'.format(entity), 'w') as temp_file:
                    temp_file.write('\t'.join([header.encode('utf-8') for header in headers])+'\n')
                    try:
                        for index, record_dict in enumerate(data, start=1):
                            record_dict = json.loads(record_dict.group(0))
                            record = dict_to_record(record_dict=record_dict, headers=lower_headers)
                            temp_file.write(record)
                    except Exception as err:
                        logger.except_log('{0} file created with 0 records. Error: {1}'.format(entity.upper(), str(err)))

                logger.debug('{} converted after {}.'.format(entity.upper(), time.time() - initial_time))
                logger.debug('Number of Records: {}'.format(index))
                logger.debug('Number of Skipped Records: {}'.format(overlooked_records))
                # review_temporary_file(entity, powerschool_error)

            else:
                logger.warning('Could not find any matches inside the json file')
            mmap_json.close()

        except Exception as err:
            print(err)
            logger.debug('Memory map assignment failed.')
            loggering.except_log(err)
    return index


@debuglog()
def check_and_delete_file(full_filename, logger):
    """
    Check if a file exists and delete it if it does

    :param full_filename: The full path to the file you want to check and delete
    :param logger: a logger object
    """
    file_not_exists = True
    if os.path.exists(full_filename):
        try:
            os.remove(full_filename)
            logger.debug(msg='File {} succesfully deleted'.format(full_filename))
        except Exception as e:
            logger.warning(msg='File {0} was not deleted because error: {1}'.format(full_filename, e))
            file_not_exists = False
    else:
        logger.debug(msg='File {} does not exist'.format(full_filename))
    
    return file_not_exists


@debuglog()
def review_temporary_file(filename, logger):
    """
    It takes a filename and a logger, and it prints the contents of the file to the logger

    :param filename: The name of the file to be reviewed
    :param logger: a logger object
    """
    ori_file_size = ''
    new_file_size = ''
    txt_filename = '{}.txt'.format(filename)
    tmp_filename = '{}.txt.tmp'.format(filename)
    json_filename = '{}.json.tmp'.format(filename)
    check_and_delete_file(full_filename=json_filename, logger=logger)
    if os.path.exists(tmp_filename):
        ori_file_size = '{}'.format(os.stat(txt_filename).st_size) if os.path.exists(txt_filename) else 'Unknown'
        new_file_size = '{}'.format(os.stat(tmp_filename).st_size)
        logger.debug('\nOriginal file size: {}; Generated file size: {}'.format(ori_file_size, new_file_size))
        logger.debug('Filename to rename {}'.format(filename))
        shutil.move(tmp_filename, txt_filename)

    else:
        logger.warning('\n{0} file not found, leaving {1} unchanged.'.format(tmp_filename, txt_filename))

    return ori_file_size, new_file_size
