#!/usr/bin/env python2
#coding:utf-8
# search on 370kan

from urllib import urlopen
from json import loads
from cStringIO import StringIO
import logging
import sys
import re
import util

_logger = logging.getLogger('search370kan')
_loggerHandler = logging.StreamHandler(sys.stderr)
_loggerHandler.setLevel(logging.DEBUG)
_loggerHandler.setFormatter(logging.Formatter('[%(asctime)s - %(levelname)s:%(filename)s:%(funcName)s:%(lineno)d] %(message)s'))
_logger.addHandler(_loggerHandler)
_logger.setLevel(logging.INFO)

class MetaDataPicker:
    def pick(self, data):
        raise NotImplementedError()

class MetaRegExPicker(MetaDataPicker):
    group_idx = 0
    def pick(self, data):
        ans = list()
        for line in data:
            m = self.pattern.search(line)
            if m: ans.append(m.groups()[self.group_idx])
            # _logger.debug("%s %s", line, m)
        return ans

class TitlePicker(MetaRegExPicker):
    pattern = re.compile(r'<a\s+href="/kanview/kanindex\d+\.html"\s+title="([^"]+)"\s+target="_blank"', re.I)

class ImagePicker(MetaRegExPicker):
    pattern = re.compile(r'<img\s+src="(http://.*/uploadimg/.*\.(jpg|gif|png))"', re.I)

class IdPicker(MetaRegExPicker):
    pattern = re.compile(r'<a\s+href="/kanview/kanindex(\d+)\.html"\s+title="[^"]+"\s+target="_blank"', re.I)

class Search370Kan:
    def postsearch(self, key):
        params = {
                'searchword':key.encode('gbk'),
                'submit':'',
                }
        headers = {
                'User-Agent':r'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.19 Safari/537.31', 
                'Referer':'http://www.370kan.com/',
                'Origin':'http://www.370kan.com/',
                'Content-Type':'application/x-www-form-urlencoded'
                }

        page = util.postto('http://www.370kan.com/search.asp', params, headers)
        return page

    def parsemovies(self, page):
        if not page:
            _logger.error("Can't fetch movies. Check network.")
            return list()
        page = page.split('\n')
        titles = TitlePicker().pick(page)
        images = ImagePicker().pick(page)
        ids    = IdPicker().pick(page)
        if len(set([len(titles), len(images), len(ids)])) > 1:
            _logger.error("Different length of tuples: %d, %d, %d", len(titles), len(images), len(ids))
            _logger.error("Different length of tuples: %s, %s, %s", titles, images, ids)
            return None
        ans = []
        for i in range(0, len(titles)):
            ans.append({'title':titles[i], 'img':images[i], 'id':ids[i]})
        return ans

    def search(self, key):
        pagedata = self.postsearch(key)
        # _logger.debug("data: %s", pagedata)
        return self.parsemovies(pagedata)

if __name__ == '__main__':
    s = Search370Kan()
    _logger.info(s.search(u'暮光之城'))
    #_logger.info(s.search(u'matrix'))
