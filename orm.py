#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import os
from ConfigParser import ConfigParser
from sqlalchemy import create_engine, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.mysql import \
        BIGINT, BINARY, BIT, BLOB, BOOLEAN, CHAR, DATE, \
        DATETIME, DECIMAL, DECIMAL, DOUBLE, ENUM, FLOAT, INTEGER, \
        LONGBLOB, LONGTEXT, MEDIUMBLOB, MEDIUMINT, MEDIUMTEXT, NCHAR, \
        NUMERIC, NVARCHAR, REAL, SET, SMALLINT, TEXT, TIME, TIMESTAMP, \
        TINYBLOB, TINYINT, TINYTEXT, VARBINARY, VARCHAR, YEAR

filename = os.path.join('.', 'config.ini')
config = ConfigParser()
config.read(filename)
host = config.get('database','host')
user = config.get('database','user')
passwd = config.get('database','passwd')
db = config.get('database','db')
engine_str = "mysql://%s:%s@%s/%s?charset=utf8" % (user, passwd, host, db)

engine = create_engine(engine_str, encoding="utf8", convert_unicode=True, echo=False)
Base = declarative_base(engine)

def set_dblogger():
    logger = logging.getLogger('sqlalchemy.engine')
    hdlr = logging.FileHandler('db_orm.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.ERROR)


class Users(Base):
    __tablename__ = 'users'
    idusers = Column(BIGINT, primary_key = True)
    username = Column(VARCHAR)
    screen_name = Column(VARCHAR)
    gender = Column(VARCHAR)
    location = Column(VARCHAR)
    description = Column(VARCHAR)
    profile_image_url = Column(VARCHAR)
    followings_count = Column(INTEGER)
    followers_count = Column(INTEGER)
    statuses_count = Column(INTEGER)
    is_verified = Column(TINYINT)
    is_daren = Column(TINYINT)
    verify_info = Column(VARCHAR)
    insert_time = Column(DATETIME)
    tag = Column(VARCHAR)
    education_info = Column(VARCHAR)
    career_info = Column(VARCHAR)
    create_time = Column(DATETIME)
    birthday = Column(VARCHAR)
    is_visited = Column(TINYINT)
    is_picked = Column(TINYINT)
    pick_time = Column(DATETIME)

    def __init__(self, idusers, username, screen_name, gender, location,
                 description, profile_image_url, followings_count, followers_count,
                 statuses_count, is_verified, is_daren, verify_info, insert_time,
                 tag, education_info, career_info, create_time, birthday, is_visited,
                 is_picked, pick_time):
        self.idusers = idusers
        self.username = username
        self.screen_name = screen_name
        self.gender = gender
        self.location = location
        self.description = description
        self.profile_image_url = profile_image_url
        self.followings_count = followings_count
        self.followers_count = followers_count
        self.statuses_count = statuses_count
        self.is_verified = is_verified
        self.is_daren = is_daren
        self.verify_info = verify_info
        self.insert_time = insert_time
        self.tag = tag
        self.education_info = education_info
        self.career_info = career_info
        self.create_time = create_time
        self.birthday = birthday
        self.is_visited = is_visited
        self.is_picked = is_picked
        self.pick_time = pick_time

    def __repr__(self):
        """
        will return a pretty string of current object
        """
        return "<User- '%s' - '%s'- '%s' - '%s'- '%s' - '%s' \
                - '%s' - '%s'- '%s' - '%s'- '%s' - '%s'- '%s' - '%s' \
                - '%s' - '%s'- '%s' - '%s'- '%s'- '%s'>" % (self.idusers, self.username, self.screen_name,
                self.gender, self.location, self.description, self.profile_image_url, self.followings_count,
                self.followers_count, self.statuses_count, self.is_verified, self.is_daren, self.verify_info,
                self.insert_time, self.tag, self.education_info, self.career_info, self.create_time, self.birthday, self.is_visited)

class Follow(Base):
    __tablename__ = 'follow'
    user_id = Column(BIGINT, primary_key = True)
    following_id = Column(BIGINT, primary_key = True)

    def __init__(self, user_id, following_id):
        self.user_id = user_id
        self.following_id = following_id

    def __repr__(self):
        return "<Follow- '%s' -> '%s'>" % (self.user_id, self.following_id)

def load_session():
    """
    """
    metadata = Base.metadata
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

if __name__ == "__main__":
    set_dblogger()
    session = load_session()
    query = session.query(Users)
    count = query.filter(Users.idusers == "2407207504").count()
    print count
    session.commit()
