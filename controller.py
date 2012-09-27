#!/usr/bin/python
# -*- coding: utf-8 -*-
from ConfigParser import ConfigParser
import re
import os
import logging
import urllib
import urllib2
import cookielib
import codecs
import time
from urllib2 import Request, build_opener, urlopen, HTTPCookieProcessor, HTTPHandler, URLError, HTTPError
import sys

import login
from login import Login


class Controller:
    def __init__(self):
        print 'init controller'
        self.login_instance = Login()
        self.logger = self.login_instance.get_logger()
        self.config = self.login_instance.get_config()
        self.cj = self.login_instance.cj
        self.cookie_dict = self.login_instance.cookie_dict
        self.opener = self.login_instance.opener


    def start_crawler(self):
        """start_crawler function is the entry main func
           will start the crawler
        """
        self.login_instance.login_weibo()
        self.logger.info('OKAY, this info is from controller class')
        cookie_str = self.config.get('crawler','user_token') + '=' + self.cookie_dict[self.config.get('crawler','user_token')] \
                        + ';' + \
                        self.config.get('crawler','user_id') + '=' + self.cookie_dict[self.config.get('crawler','user_id')]
        print 'start visiting!: ', cookie_str
        headers = {
                'User-Agent': self.config.get('crawler','User-Agent'),
                'Cookie': cookie_str}
        to_visit_url = 'http://weibo.cn/xicilion'
        req = urllib2.Request(url = to_visit_url, headers=headers)
        try:
            response = self.opener.open(req)
            html = response.read()
            response.close()
        except URLError, e:
            if hasattr(e, 'reason'):
                self.logger.error("http url error reason: %s" % e.reason)
            elif hasattr(e, 'code'):
                self.logger.error("http url error code: %s" % e.code)
                html = 'ERROR'
            # TODO you need to think calfully how to deal with this login error here
        finally:
            file = open('visit.html','w')
            file.write(html)
            file.close()




if __name__ == '__main__':
    controller = Controller()
    controller.start_crawler()
