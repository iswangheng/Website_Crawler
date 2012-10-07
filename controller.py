#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2
import time
import datetime
import orm
from urllib2 import URLError

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
        orm.set_dblogger()
        self.session = orm.load_session()

    def is_stored_user(self, user_id):
        query = self.session.query(orm.Users)
        count = query.filter(orm.Users.idusers == user_id).count()
        self.session.commit()
        return count != 0

    def is_stored_username(self, username):
        query = self.session.query(orm.Users)
        count = query.filter(orm.Users.username == username).count()
        self.session.commit()
        return count != 0

    def get_userid_by_username(self, username):
        """
        will query the db and get the user_id by username
        """
        user_id = 0
        query = self.session.query(orm.Users.idusers, orm.Users.username)
        try:
            user_id = query.filter(orm.Users.username == username).first().idusers
        except:
            self.logger.error("query.filter(orm.Users.username == %s).first().idusers" % username)
            user_id = 0
        return user_id

    def store_user_into_db(self, user_home, user_info, username):
        """
        store the user into the users table
        """
        insert_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        add_user = orm.Users(idusers=user_home['user_id'], username=username,
                   screen_name=user_info['screen_name'], gender=user_info['gender'],
                   location=user_info['location'], description=user_info['description'],
                   profile_image_url=user_info['profile_image_url'],
                   followings_count=user_home['followings_count'],
                   followers_count=user_home['followers_count'],
                   statuses_count=user_home['statuses_count'], is_verified=user_info['is_verified'],
                   is_daren=user_info['is_daren'], verify_info=user_info['verify_info'],
                   insert_time=insert_time, tag=user_info['tag'],
                   education_info=user_info['education_info'], career_info=user_info['career_info'],
                   create_time = "2000-01-01 00:00:00", birthday=user_info['birthday'], is_visited='0')
        self.session.add(add_user)
        self.session.commit()

    def update_user_is_visited(self, user_id):
        """
        change the is_visited of the user from 0 to 1,
           means that this user has been visited, and will not be visited again
        """
        try:
            self.session.query(orm.Users).filter(orm.Users.idusers == user_id).update(
                    {'is_visited': 1})
            self.session.commit()
        except:
            self.logger.error("update is_visited error...user_id: %s" % user_id)

    def store_follow_into_db(self, user_id, following_id):
        """
        store the user following relationship into the follow table
        """
        add_follow = orm.Follow(user_id=user_id, following_id=following_id)
        self.session.add(add_follow)
        self.session.commit()

    def fill_to_visit_list(self):
        """
        will query the db and return a to_visit_list with length of 100
        """
        to_visit_list = []
        try:
            query = self.session.query(orm.Users)
            users = query.filter(orm.Users.is_visited == 0).limit(100)
            for user in users:
                to_visit_list.append(user.idusers)
        except:
            self.logger.error("fill_to_visit_list...")
            to_visit_list = self.fill_to_visit_list()
        return to_visit_list

    def get_user_info(self, headers, user_url):
        user_home = {}
        user_info = {}
        user_id = 0
        username = user_id
        is_stored = 0
        is_banned = False
        if 'u/' in user_url:
            # means that u/***, *** is a number namely user_id
            user_url = user_url[2:]
            user_id = user_url
        # if user_url is the user_id, then username will also be user_id
        # else, the username would be the user_url
        username = user_url
        # judge the user_id here    
        # check if the user_id exists in the database already
        # if so...do not proceed....
        # else go on and get the user info
        if user_id == 0:  # if still not get the user_id
            is_stored = self.is_stored_username(username)
        else:   # already have the user_id
            is_stored = self.is_stored_user(user_id)
        if is_stored:
            user_id = self.get_userid_by_username(username)
            print '%s has been stored already' % user_id
            return is_banned, user_id
        else:  # if a new user, add it to db
            to_visit_url = 'http://weibo.cn/' + str(user_url)
            req = urllib2.Request(url = to_visit_url, headers=headers)
            # user_home contains the user_id, following, follower, and status count
            try:
                response = self.opener.open(req)
                html = response.read()
                if parse.is_pub_page(html):
                    is_banned = True
                    return is_banned, user_id
                user_home = parse.parse_user_home(html)
                print user_home
                user_id = user_home['user_id']
                response.close()
            except URLError, e:
                user_id = 0
                is_banned = True
                if hasattr(e, 'code'):
                    self.logger.error("http url error code: %s" % e.code)
                    if hasattr(e, 'reason'):
                        self.logger.error("http url error reason: %s" % e.reason)
                return is_banned, user_id
            to_visit_url = 'http://weibo.cn/' + str(user_id) + "/info"
            req = urllib2.Request(url = to_visit_url, headers=headers)
            # to get the user info
            try:
                response = self.opener.open(req)
                html_str = response.read()
                if parse.is_pub_page(html_str):
                    is_banned = True
                    return is_banned, user_id
                user_info = parse.parse_user_info(str(html_str), user_id, headers, self.opener, self.logger)
                response.close()
                # store the user_home(u know, those numbers) and user_info into database
                if user_info['screen_name'] != '':
                    self.store_user_into_db(user_home, user_info, username)
            except URLError, e:
                if hasattr(e, 'code'):
                    self.logger.error("http url error code: %s" % e.code)
                    if hasattr(e, 'reason'):
                        self.logger.error("http url error reason: %s" % e.reason)
        return is_banned, user_id

    def get_user_following(self, headers, user_id):
        """
        # will get all the user following urls and then get the user info one by one
        """
        user_following_url_list = []
        to_visit_url = 'http://weibo.cn/' + str(user_id) + '/follow'
        req = urllib2.Request(url = to_visit_url, headers=headers)
        try:
            response = self.opener.open(req)
            html = response.read()
            # if is the pub page, means too fast.. have been detected and banned by sina
            if parse.is_pub_page(html):
                self.logger.error("BANNED by sina, coz is_pub_page..")
                print "BANNED by sina, coz is_pub_page..sleep for 20 mins.."
                return False
            user_following_url_list = parse.get_following_url_list(html,
                    page_num=1, total_page_num=111,headers=headers, 
                    opener = self.opener, logger=self.logger)
            print len(user_following_url_list)
            response.close()
        except URLError, e:
            if hasattr(e, 'code'):
                self.logger.error("http url error code: %s" % e.code)
                if hasattr(e, 'reason'):
                    self.logger.error("http url error reason: %s" % e.reason)
            # TODO you need to think calfully how to deal with this login error here
        following_id_list = []
        for following_url in user_following_url_list:
            # will get and store the followings user info
            is_banned, following_id = self.get_user_info(headers, following_url)
            if is_banned:
                self.logger.error("BANNED by sina again..is_pub_page. from get_user_info()")
                print 'banned...sleep for 1800 seconds...'
                time.sleep(1800)
            else:
                following_id_list.append(following_id)
        for following_id in following_id_list:
            print following_id
            #self.store_follow_into_db(user_id, following_id)
        return True


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
        start_user_id = self.config.get("crawler", "start_user_id")
        self.get_user_following(headers, start_user_id)
        while 1:
            to_visit_list = self.fill_to_visit_list()
            for user_id in to_visit_list:
                if self.get_user_following(headers, user_id):
                    self.update_user_is_visited(user_id)
                else:
                    time.sleep(1200)
                time.sleep(10)


if __name__ == '__main__':
    controller = Controller()
    controller.start_crawler()
