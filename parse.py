#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import time
import random
import urllib2
from bs4 import BeautifulSoup
from urllib2 import URLError 


"""
This module is very very very very DIRTY
I just wrote for weibo.cn ONLY
SORRY for those DIRTY codes.......so sorry :)
"""

def is_pub_page(html):
    """
    just to check whether this page the pub page,
     which also means the crawler may have been detected by sina....
      so, the crawler needs to stop for a while?
    """
    soup = BeautifulSoup(html)
    if soup.title.string == u"微博广场":
        return True
    else:
        return False

def parse_user_home(home):
    """
    this function will take the user_home.wml as input
    and then get the user_id, users following, followers and status_counts,
    would return a dict
    """
    user_home = {'user_id':'','followings_count':'', 'followers_count':'', 'statuses_count':''}
    try:
        home_soup = BeautifulSoup(home)
        user_info_html = home_soup.find_all(href=re.compile("/info"))[0]
        user_id_href_str = str(user_info_html['href'])
        start_index = 1
        end_index = start_index + user_id_href_str[start_index:].index('/info')
        user_home['user_id'] = user_id_href_str[start_index:end_index]
        status_start_index = home.index('微博[') + len('微博[')
        status_end_index = status_start_index + home[status_start_index:].find(']')
        user_home['statuses_count'] = home[status_start_index:status_end_index]
        following_start_index = home.index('关注[') + len('关注[')
        following_end_index = following_start_index + home[following_start_index:].find(']')
        user_home['followings_count'] = home[following_start_index:following_end_index]
        follower_start_index = home.index('粉丝[') + len('粉丝[')
        follower_end_index = follower_start_index + home[follower_start_index:].find(']')
        user_home['followers_count'] = home[follower_start_index:follower_end_index]
    except:
        user_home = {'user_id':'', 'followings_count':'', 'followers_count':'', 'statuses_count':''}
    return user_home

def parse_user_info(info, user_id, headers, opener, logger):
    """
    this function will take the user_info.wml as input
    and then get all the users info,
    would return a dict
    """
    user_info = {'screen_name':'',
                 'gender':'', 'location':'', 'birthday':'', 'description':'',
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
    except:
        user_info['profile_image_url'] = ""
    try:
        soup = BeautifulSoup(info)
        tip_div_list = soup.find_all("div", class_="tip")
        basic_info_soup = tip_div_list[0].find_next()
        basic_info = str(basic_info_soup)
    except:
        logger.error("looks like the info page html has no such class, maybe speed is too fast")
        logger.info("will now sleep for 10 seconds")
        file = open('infopage_error.html', 'w')
        file.write(info)
        file.close()
        print "infopage_error....."
        time.sleep(10)
        return user_info
    user_info['screen_name'] = get_user_info_by_key(">昵称:",basic_info)
    if -1 != basic_info.find('>认证:'):
        user_info['is_verified'] = '1'
        user_info['verify_info'] = get_user_info_by_key(">认证:",basic_info)
    else:
        user_info['is_verified'] = '0'
    if -1 != basic_info.find('>达人:'):
        user_info['is_daren'] = '1'
    else:
        user_info['is_daren'] = '0'
    user_info['gender'] = get_user_info_by_key(">性别:", basic_info)
    user_info['location'] = get_user_info_by_key(">地区:", basic_info)
    user_info['birthday'] = get_user_info_by_key(">生日:", basic_info)
    user_info['description'] = get_user_info_by_key(">简介:", basic_info)
    user_info['tag'] = get_user_tags(user_id, basic_info_soup, headers, opener, logger)
    #get the edu_info and career_info html soup from the html
    edu_info_soup, career_info_soup = get_user_edu_career_html(tip_div_list)
    user_info['ei'] = get_user_education(edu_info_soup)
    user_info['ci'] = get_user_career(career_info_soup)
    return user_info

def get_user_edu_career_html(tip_div_list):
    edu_info = ""
    career_info = "" 
    if 4 == len(tip_div_list):
        edu_info = tip_div_list[1].find_next()
        career_info = tip_div_list[2].find_next()
    elif 3 == len(tip_div_list):
        temp = str(tip_div_list[1].find_next())
        if -1 != temp.find("学习经历"):
            edu_info = tip_div_list[1].find_next()
        else:
            career_info = tip_div_list[1].find_next()
        print 'missing one info'
    else:
        print 'just basic info, no ei or ci'
    return edu_info, career_info

def get_user_info_by_key(key, info):
    """
    this function is called by parse_use_info() ONLY
    ONLY used for >昵称:  >认证:  >性别:  >地区:  >生日:  >简介:
    """
    try:
        start_index = info.index(key) + len(key)
        end_index = start_index + info[start_index:].index('<br')
        print "%s %s" % (key, info[start_index:end_index])
        return info[start_index:end_index]
    except:
        print "no such: ", key
        return ""

def get_user_tags(user_id, basic_info_soup, headers, opener, logger):
    """
    get_user_tags may have more(更多),
    so we have to request for another time to get all the tags
    """
    tags = ""
    basic_info_str = str(basic_info_soup)
    if -1 == basic_info_str.find('account/privacy/tags/'):
        # means that just parse this page to get the tags will be fine
        tags = get_current_tags(basic_info_soup, logger)
    else:
        # means that we have to get another page to get all the tags
        tags = get_more_tags(user_id, headers, opener, logger)
    print "tags:", tags
    return tags

def get_current_tags(basic_info_soup, logger):
    """
    just parse one page which is the user info page to get the tags
    """
    tags = "no"
    try:
        tags = ""
        tag_soup_a_list = basic_info_soup.find_all('a')
        for a in tag_soup_a_list:
            tags = tags + a.string+','
        tags = tags[:-1]
    except:
        logger.error("something is wrong with the tags..maybe it has no tags'>")
        tags = ""
    return tags

def get_more_tags(user_id, headers, opener, logger):
    """
    will visit the /account/privacy/tags/***** page to get all the tags
    """
    to_visit_url = "http://weibo.cn/account/privacy/tags/?uid=" + str(user_id)
    req = urllib2.Request(url = to_visit_url, headers=headers)
    try:
        response = opener.open(req)
        html_str = response.read()
        soup = BeautifulSoup(html_str)
        class_c_list = soup.find_all('div', class_='c')
        try:
            tags = ""
            tag_soup = class_c_list[2]
            tag_soup_a_list = tag_soup.find_all('a')
            for a in tag_soup_a_list:
                tags = tags + a.string+','
            tags = tags[:-1]
        except:
            logger.error("index out of bound...less than 3 <div class='c'>")
            tags = ""
        response.close()
    except URLError, e:
        if hasattr(e, 'reason'):
            logger.error("http url error reason: %s" % e.reason)
        elif hasattr(e, 'code'):
            logger.error("http url error code: %s" % e.code)
    return tags

def get_user_education(info):
    """
    will get users education info
    """
    if "" == info:
        return "NULL"
    ei_list = info.findAll(text=True)
    new_ei_list = []
    # the reason here is that we have an annoying little point before each line
    # so I have to remove the first char which is the little point of each line
    for ei in ei_list:
        ei = ei[1:]
        new_ei_list.append(ei)
    ei = "\n".join(new_ei_list)
    print "edu info: ",ei
    return ei

def get_user_career(info):
    """
    will get users career info
    """
    if "" == info:
        return "NULL"
    ci_list = info.findAll(text=True)
    new_ci_list = []
    # the reason here is that we have an annoying little point before each line
    # so I have to remove the first char which is the little point of each line
    for ci in ci_list:
        ci = ci[1:]
        new_ci_list.append(ci)
    ci = "\n".join(new_ci_list)
    print "career info", ci
    return ci

def get_following_url_list(user_id, following_page, page_num, total_page_num,  headers, opener, logger):
    """
    will return a list containing the fake urls(****)
    these fake urls are the url of the followings
        for example:
            following_url = "http://weibo.cn" + ***
            here *** can be /user_id(12345) or user_name(swarm)
            and *** is the fake user_url and is extracted from the following page
    """
    following_url_list = []
    following_soup = BeautifulSoup(following_page)
    try:
        table_soup_list = following_soup.find_all('table')
        for table_soup in table_soup_list:
            href_str = str(table_soup.find_all('a')[0]['href'])
            following_url = href_str[1:]
            print "following url of current page", following_url
            following_url_list.append(following_url)
    except:
        logger.error("%s maybe 0 followings or speed too fast.." % str(user_id))
        return following_url_list
    try:
        pagelist_div = following_soup.select('div[id="pagelist"]')[0]
        pagelist_div_div = pagelist_div.find_all('div')[0]
        pagelist_div_div_str = str(pagelist_div_div)
    except:
        logger.error("%s pagelist div NOT FOUND. maybe just a few(one page..) followings or speed too fast.." % str(user_id))
        print 'len of list: ', len(following_url_list)
        return following_url_list
    # if now is the first page of user followings
    # will need to get the total num of pages and the next page url
    if 1 == page_num:
        # number of pages of the following users
        # this part is so dirty ...just to get the togal number of pages
        try:
            start_index = pagelist_div_div_str.index('1/') + len('1/')
            end_index = start_index + pagelist_div_div_str[start_index:].index("页")
            total_page_num = int(pagelist_div_div_str[start_index:end_index])
        except:
            logger.error("Error:...when trying to get pagelist: total_page_num")
            filename = "%s.html" % str(user_id)
            file = open(filename, "w")
            file.write(following_page)
            file.close()
            total_page_num = 1
        print "total_page_num: ", total_page_num
    # if this is still not the last page
    # then need to visit the next page and then get followings urls again...(recursively)
    if page_num < total_page_num:
        to_visit_url = ""
        try:
            to_visit_url = "http://weibo.cn" + pagelist_div_div.find_all('a')[0]['href']
        except:
            logger.error("Error:...pagelist: to_visit_url(meaning next page url)")
            to_visit_url = ""
        print "next_page_url: ", to_visit_url
        req = urllib2.Request(url = to_visit_url, headers=headers)
        page_num = page_num + 1
        try:
            response = opener.open(req)
            html_str = response.read()
            time_sleep = random.randint(2,3)
            print "sleep for %s seconds" % (time_sleep)
            time.sleep(time_sleep)
            following_url_list = following_url_list \
                    + get_following_url_list(user_id, html_str, page_num, total_page_num, headers, opener, logger)
            response.close()
        except URLError, e:
            if hasattr(e, 'code'):
                logger.error("http url error code: %s" % e.code)
                if hasattr(e, 'reason'):
                    logger.error("http url error reason: %s" % e.reason)
    print 'len of list: ', len(following_url_list)
    return following_url_list



if __name__ == '__main__':
    info_file = 'pub.html'
    info = open(info_file,'r')
    info_str = info.read()
    if is_pub_page(info_str):
        print "is pub"
    #print parse_user_info(info_str)['screen_name']
    info.close()

