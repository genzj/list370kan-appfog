#!/usr/bin/env python2
#coding:utf-8
# I use this poor script to read playlist from www.370kan.com

from urllib import urlopen, urlencode
from urllib2 import Request, urlopen as urlopen2
from json import loads
from cStringIO import StringIO
import logging
import sys
import re

_logger = logging.getLogger('util')
_loggerHandler = logging.StreamHandler(sys.stderr)
_loggerHandler.setLevel(logging.DEBUG)
_loggerHandler.setFormatter(logging.Formatter('[%(asctime)s - %(levelname)s:%(filename)s:%(funcName)s:%(lineno)d] %(message)s'))
_logger.addHandler(_loggerHandler)
_logger.setLevel(logging.INFO)

def loadpage(url, decodec='gbk'):
    if not url: return None
    _logger.info('getting url %s', url)
    try:
        con = urlopen(url)
    except Exception, err:
        _logger.error(str(err))
        return None
    if con:
        _logger.info("Hit %s %d", str(con), con.getcode())
        data = con.read(-1)
        # _logger.debug(str(data))
        return data.decode(decodec)
    else:
        _logger.error("No data returned.")
    return None

def postto(url, datadict, headers={}, decodec='gbk'):
    params = urlencode(datadict)
    _logger.info('Post %s to %s, headers %s', params, url, headers)
    try:
        req = Request(url=url, data=params)
        for k,v in headers.items():
            req.add_header(k,v)
        con = urlopen2(req)
        if con:
            _logger.info("Hit %s %d", str(con), con.getcode())
            data = con.read(-1)
            return data.decode(decodec)
        else: 
            _logger.error("No data returned.")
            return None

    except Exception, err:
        _logger.error(str(err))

