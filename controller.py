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

if __name__ == '__main__':
    controller = Controller()
    controller.start_crawler()
