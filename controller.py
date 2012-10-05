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
import parse


class Controller:
    def __init__(self):
        print 'init controller'
        self.login_instance = Login()
        self.logger = self.login_instance.get_logger()
        self.config = self.login_instance.get_config()
        self.cj = self.login_instance.cj
        self.cookie_dict = self.login_instance.cookie_dict
        self.cookie_str = ""
        self.opener = self.login_instance.opener

    def get_user_info(self, headers, user_url):
        user_home = {}
        user_info = {}
        user_id = 0
        to_visit_url = 'http://weibo.cn/' + str(user_url)
        req = urllib2.Request(url = to_visit_url, headers=headers)
        # TODO to get the following,follower,status count and then
        try:
            response = self.opener.open(req)
            html = response.read()
            user_home = parse.parse_user_home(html)
            print user_home
            user_id = user_home['user_id']
            response.close()
        except URLError, e:
            user_id = ''
            if hasattr(e, 'reason'):
                self.logger.error("http url error reason: %s" % e.reason)
            elif hasattr(e, 'code'):
                self.logger.error("http url error code: %s" % e.code)
            # TODO you need to think calfully how to deal with this login error here
            return
        # TODO
        # Remember to judge the user_id here    
        # check if the user_id exists in the database already
        # if so...do not proceed....
        # else go on and get the user nfo
        to_visit_url = 'http://weibo.cn/' + str(user_id) + "/info"
        req = urllib2.Request(url = to_visit_url, headers=headers)
        # TODO to get the user info
        try:
            response = self.opener.open(req)
            html_str = response.read()
            user_info = parse.parse_user_info(str(html_str), headers, self.opener, self.logger)
            response.close()
        except URLError, e:
            if hasattr(e, 'reason'):
                self.logger.error("http url error reason: %s" % e.reason)
            elif hasattr(e, 'code'):
                self.logger.error("http url error code: %s" % e.code)
        # TODO store the user_home(numbers) and user_info into database

    def get_user_following(self, headers, user_id):
        """
        # will get all the user following urls and then get the user info one by one
        """
        user_following_url_list = []
        # TODO need to store the relationship into database
        to_visit_url = 'http://weibo.cn/' + str(user_id) + '/follow'
        req = urllib2.Request(url = to_visit_url, headers=headers)
        try:
            response = self.opener.open(req)
            html = response.read()
            user_following_url_list = parse.get_following_url_list(html,
                    page_num=1, total_page_num=111,headers=headers, 
                    opener = self.opener, logger=self.logger)
            print len(user_following_url_list)
            response.close()
        except URLError, e:
            if hasattr(e, 'reason'):
                self.logger.error("http url error reason: %s" % e.reason)
            elif hasattr(e, 'code'):
                self.logger.error("http url error code: %s" % e.code)
            # TODO you need to think calfully how to deal with this login error here
        for following_url in user_following_url_list:
            self.get_user_info(headers, following_url)

    def start_crawler(self):
        """start_crawler function is the entry main func
           will start the crawler
        """
        self.login_instance.login_weibo()
        self.logger.info('OKAY, this info is from controller class')
        cookie_str = self.config.get('crawler','user_token') + '=' + self.cookie_dict[self.config.get('crawler','user_token')] \
                        + ';' + \
                        self.config.get('crawler','user_id') + '=' + self.cookie_dict[self.config.get('crawler','user_id')]
        self.cookie_str = cookie_str
        print 'start visiting!: ', self.cookie_str
        headers = {
                'User-Agent': self.config.get('crawler','User-Agent'),
                'Cookie': cookie_str}
        #self.get_user_info(headers, '2041028560')
        self.get_user_following(headers, user_id='1693298840')


if __name__ == '__main__':
    controller = Controller()
    controller.start_crawler()
