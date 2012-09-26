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


class Login:
    def __init__(self):
        self.logger = self.set_logger()
        self.config = self.set_config()
        #Create a CookieJar object to hold the cookies
        self.cj = cookielib.CookieJar()
        self.cookie_dict = {self.config.get('crawler','user_token'):'', self.config.get('crawler','user_id'):''}
        #Create an opener to open pages using the http protocol and to process cookies.
        self.opener = build_opener(HTTPCookieProcessor(self.cj), HTTPHandler())

    def set_logger(self):
        """
        will set up the logger for the program
        """
        logger = logging.getLogger('crawler')
        hdlr = logging.FileHandler('crawler.log')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr) 
        logger.setLevel(logging.INFO)
        return logger

    def set_config(self):
        """ will read config.ini and then return the config for further use
        """
        filename = os.path.join('.', 'config.ini')
        print filename
        config = ConfigParser()
        config.read(filename)
        return config
        ''' # just show you how to use config
        passwd = config.get('database','passwd')
        print passwd
        '''

    def get_logger(self):
        return self.logger

    def get_config(self):
        return self.config

    def get_randomNum(self, txt):
        """
        used only in the login part.
        coz sina weibo would give a random num in the password input part
        so I have to get this number before post
        """
        re1='(password)'    # Word 1
        re2='(_)'   # Any Single Character 1
        re3='(\\d)' # Any Single Digit 1
        re4='(\\d)' # Any Single Digit 2
        re5='(\\d)' # Any Single Digit 3
        re6='(\\d)' # Any Single Digit 4
        rg = re.compile(re1+re2+re3+re4+re5+re6,re.DOTALL)
        m = rg.search(txt)
        random_num = '0000'
        if m:
            word1=m.group(1)
            c1=m.group(2)
            d1=m.group(3)
            d2=m.group(4)
            d3=m.group(5)
            d4=m.group(6)
            random_num = d1+d2+d3+d4
            print word1+c1+random_num
        else:
            random_num = '0000'
        return random_num


    def get_vk_by_randomNum(self,random_num, txt):
        """
        used only in the login part
        coz sina weibo would give a random num in the password input part and also vk is related to this num
        so I have to get vk before post
        """
        start_str = "%s_" % random_num
        start_index = txt.find(start_str)
        end_index = start_index + txt[start_index:].find('"')
        return txt[start_index:end_index]

    def get_pwdRandom_vk(self, logger, login_html):
        """
        used only in the login part
        I have to get this random_num and vk before post
        """
        pwd_random = "password_1234"
        vk = "1243_123_123"
        random_num = self.get_randomNum(login_html)
        pwd_random = "password_%s" % random_num
        vk = self.get_vk_by_randomNum(random_num, login_html)
        if '0000' == random_num:
            logger.error("login_html random_num error: random_num == 0000")
        return {'pwd_random':pwd_random, 'vk':vk}

    def login_weibo(self):
        """
        this part will check the password_randomNum firstly
        thus the crawler would the what the randomNum is
        and then request the page after submitting,
        and parse the redirect page to fetch the final weibo url
        At last open the final weibo url to the main page of weibo
        """
        logger = self.logger
        config = self.config
        # set user-agent to be Firefox 15.0a2
        headers = {'User-Agent': config.get('crawler','User-Agent')}
        login_url = "http://3g.sina.com.cn/prog/wapsite/sso/login.php?ns=1&revalid=2&backURL=http%3A%2F%2Fweibo.cn%2F%3Fs2w%3Dlogin&backTitle=%D0%C2%C0%CB%CE%A2%B2%A9&vt=4"
        print config.get('weibo', 'username')
        req = urllib2.Request(url = login_url, headers=headers)
        #req = urllib2.Request("http://weibo.cn")
        html = "None"
        try:
            response = self.opener.open(req)
            html = response.read()
            response.close()
        except URLError, e:
            if hasattr(e, 'reason'):
                logger.error("http url error reason: %s" % e.reason)
            elif hasattr(e, 'code'):
                logger.error("http url error code: %s" % e.code)
            html = 'ERROR' 
            # TODO you need to think calfully how to deal with this login error here
            # TODO remember to edit this part later
            self.login_weibo()
        pwd_random_vk_dict = self.get_pwdRandom_vk(logger, html)
        print 'pwd_random: ', pwd_random_vk_dict['pwd_random']
        print 'vk: ', pwd_random_vk_dict['vk']
        postdata=urllib.urlencode({
            'mobile': config.get('weibo', 'username'),
            pwd_random_vk_dict['pwd_random']: config.get('weibo', 'password'),
            'remember': 'on',
            'backURL': 'http://weibo.cn/',
            'backTitle': '新浪微博',
            'vk': pwd_random_vk_dict['vk'],
            'submit': '登录'
        })
        req = urllib2.Request(url = login_url, data = postdata, headers=headers)
        try:
            response = self.opener.open(req)
            html = response.read()
            #Check out the cookies
            print "the cookies are: "
            for cookie in self.cj:
                print cookie.name + ' ' + cookie.value + ' ' 
                self.cookie_dict[cookie.name] = cookie.value
            response.close()
        except URLError, e:
            if hasattr(e, 'reason'):
                logger.error("http url error reason: %s" % e.reason)
            elif hasattr(e, 'code'):
                logger.error("http url error code: %s" % e.code)
            html = 'ERROR' 
            # TODO you need to think calfully how to deal with this login error here
            # TODO remember to edit this part later
        self.login_weibo_last_step(html)

    def login_weibo_last_step(self, login_redirect):
        redirect_start_index = login_redirect.find('url=') + 4
        redirect_end_index = redirect_start_index + login_redirect[redirect_start_index:].find('"')
        redirect_url = login_redirect[redirect_start_index:redirect_end_index]
        print "redirect_url: ", redirect_url
        cookie_str = self.config.get('crawler','user_token') + '=' + self.cookie_dict[self.config.get('crawler','user_token')]
        headers = {
                'User-Agent': self.config.get('crawler','User-Agent'),
                'Cookie': cookie_str}
        req = urllib2.Request(url = redirect_url, headers=headers)
        try:
            response = self.opener.open(req)
            html = response.read()
            #update the cookies, this time my add _WEIBO_UID
            for cookie in self.cj:
                self.cookie_dict[cookie.name] = cookie.value
            response.close()
        except URLError, e:
            if hasattr(e, 'reason'):
                self.logger.error("http url error reason: %s" % e.reason)
            elif hasattr(e, 'code'):
                self.logger.error("http url error code: %s" % e.code)
            html = 'ERROR' 
            # TODO you need to think calfully how to deal with this login error here
            # TODO remember to edit this part later
        self.logger.info("the Login module has finished login")


    def start_testing(self):
        """start_crawler function is the entry main func
           will start the crawler
        """
        self.login_weibo()
        cookie_str = self.config.get('crawler','user_token') + '=' + self.cookie_dict[self.config.get('crawler','user_token')] \
                     + ';' + \
                     self.config.get('crawler','user_id') + '=' + self.cookie_dict[self.config.get('crawler','user_id')]
        print 'start visiting!: ', cookie_str
        headers = {
                'User-Agent': self.config.get('crawler','User-Agent'),
                'Cookie': cookie_str}
        #headers = {'User-Agent': self.config.get('crawler','User-Agent')}
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
    login = Login()
    login.start_testing()
