"""
    General Utils for the API
"""
import logging

import requests

from .exceptions import PFAPIException

logging.basicConfig(level=logging.INFO)
STATUS_OK = 200


def _check_status_code_raise_error(ret):
    """
        Check a request return status code and raise
        error if necessary.

        :param ret: return object from requests lib
        :raises PFAPIException: If the response is not an HTTP OK response
    """
    if ret.status_code < STATUS_OK or ret.status_code >= STATUS_OK+100:
        try:
            dat = ret.json()
            if 'detail' in dat:
                message = dat["detail"]
            else:
                message = ret.content
        except Exception:
            raise PFAPIException("Non description error: HTTP {}".format(ret.status_code))

        raise PFAPIException("Error: {}".format(message))


def get_url_call_response(url, headers):
    logging.info("GET %s", url)
    ret = requests.get(url, headers=headers)
    _check_status_code_raise_error(ret)
    return ret.json()


def get_json_url(url, raw=False):
    """
        Utility function to download a json url (be it JSON
        or GeoJSON)

        :param url: Url to retrieve JSON data from
        :param raw: Do not parse the output as JSON, return it as is
        :return: Either the raw content of a response or a dictionary with the
                 parsed json structure
        :rtype: String or Dict
        :raises PFAPIException: If the response is not an HTTP OK response
    """
    logging.info("GET %s", url)
    ret = requests.get(url)
    _check_status_code_raise_error(ret)
    if raw:
        return ret.content

    return ret.json()


def get_binary_url(url):
    """
        Utility function to download a binary url which is always returned
        as RAW data

        :param url: Url to retrieve JSON data from
        :return: Raw content of an url known to be a binary file
        :rtype: bytes
        :raises PFAPIException: If the response is not an HTTP OK response
    """
    logging.info("GET %s", url)
    ret = requests.get(url)
    _check_status_code_raise_error(ret)
    return ret.content
