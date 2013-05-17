#!/usr/bin/env python2
#coding:utf-8
# I use this poor script to read playlist from www.370kan.com

from urllib import urlopen
from json import loads
from cStringIO import StringIO
import logging
import sys
import re
import util

_logger = logging.getLogger('list370kan')
_loggerHandler = logging.StreamHandler(sys.stderr)
_loggerHandler.setLevel(logging.DEBUG)
_loggerHandler.setFormatter(logging.Formatter('[%(asctime)s - %(levelname)s:%(filename)s:%(funcName)s:%(lineno)d] %(message)s'))
_logger.addHandler(_loggerHandler)
_logger.setLevel(logging.INFO)

def cmd_pipeline(cmdchain, input):
    for f in cmdchain:
        out = f(input)
        input = out
    return out
    
class PlaylistReaper:
    urlbase = {'js':'http://www.370kan.com/playdata/{0}/{1}.js',
               'index':'http://www.370kan.com/player/index{0}.html'
              }
    default_title = 'Playlist'
    
    def __init__(self):
        pass

    def __log(self, level, *args, **kargs):
        level_i = logging.__dict__[level.strip('[').strip(']')]
        _logger.log(level_i, *args, **kargs)
        
    def __geturl(self, _type, _id):
        if _type not in self.urlbase.keys() or not _id:
            return None
        return self.urlbase[_type].format(*_id)

    def __getjsurl(self, _id):
        return self.__geturl('js', _id)

    def __loadpage(self, url, decodec='gbk'):
        return util.loadpage(url, decodec)

    def __extractjson(self, js):
        if not js: return None
        # JS looks like
        #    var VideoListJson=[...],urlinfo=...;
        return js[js.find('=[')+1:js.rfind('],')+1].replace("'",'"')

    def __extractjsurl(self, indexpage):
        if not indexpage: return None
        pattern = re.compile(r'/playdata/(\d+)/(\d+)\.js')
        ids = pattern.search(indexpage)
        if ids:
            self.__log('[INFO]', 'js ids %s', ids.groups())
            return ids.groups()
        else:
            return None
        
    def __readplaylist(self, _json):
        if not _json: return None
        try:
            return loads(_json,encoding='utf8')
        except Exception as err:
            self.__log('[ERROR]', 'JSON parsing error %s: %s', str(err), _json)
            return None

    def __gettitle(self, pagedata, pid):
        if not pagedata or not pid: return None
        title_pattern = re.compile(r'<title>\s*([^</ ]+)\s*[^<]*</title>', re.I)
        title = title_pattern.search(pagedata)
        if title:
            self.__log('[INFO]', 'Title found: %s', title.groups())
            return title.groups()[0]
        else:
            self.__log('[WARNING]', 'Title not found in data')
            return self.default_title

    def fromjsurl(self, url):
        cmdchain = (self.__loadpage, self.__extractjson, self.__readplaylist)
        return cmd_pipeline(cmdchain, url)

    def fromjsid(self, _id):
        cmdchain = (self.__getjsurl, self.fromjsurl)
        return cmd_pipeline(cmdchain, _id)

    def fromindex(self, url):
        self.__log('[INFO]', 'player url: %s', url)
        if re.match(r'\d+', url):
            url = self.__geturl('index', (url,))
            self.__log('[INFO]', 'Real url: %s', url)
        if not re.match(r'^\w+:.+$', url):
            url = "http://" + url
        pagedata = self.__loadpage(url)
        title = self.__gettitle(pagedata, -1)
        cmdchain = (self.__extractjsurl, self.fromjsid)
        return (title, cmd_pipeline(cmdchain, pagedata))
        
    @staticmethod
    def pretty(playlist):
        ans = []
        if not playlist: return u"Empty list."
        for player in playlist:
            ans.append(u' '.join([player[0],u":",u'\n']))
            for ep in player[1]:
                ep = ep.split('$')
                s=u'{0}:\n{1}\n'.format(ep[0],ep[1])
                ans.append(s)
            ans.append(u'\n')
        return u'\n'.join(ans)

if __name__ == "__main__":
    print PlaylistReaper.pretty(PlaylistReaper().fromindex(raw_input().strip('\n'))[1])
