#!/usr/bin/python
# -*- coding: utf-8 -*-
from ConfigParser import ConfigParser
import re
import os
import logging
import time
import sys


"""
This module is very very very very DIRTY
coz I do not use any HTMLParser here and 
I just wrote for weibo.cn ONLY
SORRY for those DIRTY codes.......so sorry :)
"""

def parse_user_home(home):
    """
    this function will take the user_home.wml as input
    and then get the users following, followers and status_counts,
    would return a dict
    """
    user_home = {'followings_count':'', 'followers_count':'', 'statuses_count':''}
    try:
        following_start_index = home.index('关注[') + len('关注[')
        following_end_index = following_start_index + home[following_start_index:].find(']')
        user_home['followings_count'] = home[following_start_index:following_end_index]
        follower_start_index = home.index('粉丝[') + len('粉丝[')
        follower_end_index = follower_start_index + home[follower_start_index:].find(']')
        user_home['followers_count'] = home[follower_start_index:follower_end_index]
        status_start_index = home.index('微博[') + len('微博[')
        status_end_index = status_start_index + home[status_start_index:].find(']')
        user_home['statuses_count'] = home[status_start_index:status_end_index]
    except:
        user_home = {'followings_count':'', 'followers_count':'', 'statuses_count':''}
    return user_home

def parse_user_info(info):
    """
    this function will take the user_info.wml as input
    and then get all the users info,
    would return a dict
    """
    user_info = {'idusers':'', 'username':'', 'screen_name':'',
                 'gender':'', 'location':'', 'description':'',
                 'profile_image_url':'', 'is_verified':'', 'is_daren':'',
                 'verify_info':'', 'tag':'', 'education_info':'',
                 'career_info':''} 
    # WARNING: Here comes the DIRTY parts
    img_part_end_index = 1
    try:
        img_part_end_index = info.index('头像')
        img_part = info[:img_part_end_index]
        profile_img_start_index = img_part.rindex('src="') + len('src="')
        profile_img_end_index = profile_img_start_index + img_part[profile_img_start_index:].index('"')
        user_info['profile_image_url'] = img_part[profile_img_start_index:profile_img_end_index]
        info = info[img_part_end_index:]
        start_index = info.index('?uid=') + len('?uid=')
        end_index = start_index + info[start_index:].index('"')
        print info[start_index:end_index]
        user_info['idusers'] = info[start_index:end_index]
    except:
        user_info['profile_image_url'] = ""
    user_info['screen_name'] = get_user_info_by_key(">昵称:",info)
    if -1 != info.find('>认证:'):
        user_info['is_verified'] = '1'
        user_info['verify_info'] = get_user_info_by_key(">认证:",info)
    else:
        user_info['is_verified'] = '0'
    user_info['gender'] = get_user_info_by_key(">性别:",info)
    user_info['location'] = get_user_info_by_key(">地区:",info)
    user_info['birthday'] = get_user_info_by_key(">生日:",info)
    user_info['description'] = get_user_info_by_key(">简介:",info)
    user_info['tag'] = get_user_tags(user_info['idusers'],info)
    user_info['ei'] = get_user_education(info)
    user_info['ci'] = get_user_career(info)
    return user_info

def get_user_info_by_key(key, info):
    """
    this function is called by parse_use_info() ONLY
    ONLY used for >昵称:  >认证:  >性别:  >地区:  >生日:  >简介:
    """
    try:
        start_index = info.index(key) + len(key)
        end_index = start_index + info[start_index:].index('<br')
        print info[start_index:end_index]
        return info[start_index:end_index]
    except:
        return ""

def get_user_tags(user_id, info):
    """
    get_user_tags may have more(更多),
    so we have to request for another time to get all the tags
    """
    tags = ""
    if -1 == info.find('account/privacy/tags/'):
        # means that just parse this page to get the tags will be fine
        tags = get_current_tags(info)
    else:
        # means that we have to get another page to get all the tags
        tags = get_more_tags(info)
    print tags
    return tags

def get_current_tags(info):
    """
    just parse one page which is the user info page to get the tags
    """
    tags = "no"
    return tags

def get_more_tags(info):
    """
    will visit the /account/privacy/tags/***** page to get all the tags
    """
    tags = "more"
    return tags

def get_user_education(info):
    """
    will get users education info
    """
    ei = ""
    #TODO   
    print ei
    return ei

def get_user_career(info):
    """
    will get users career info
    """
    ci = ""
    #TODO   
    print ci
    return ci

if __name__ == '__main__':
    info = open('test.html','r')
    info_str = info.read()
    print parse_user_info(info_str)['screen_name']
    info.close()

