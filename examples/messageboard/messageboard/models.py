# coding=utf8


import pymysql
from skylark import Database, Model, Field
from messageboard import app


class Message(Model):
    title = Field()
    content = Field()
    create_at = Field()


Database.set_dbapi(pymysql)
Database.config(**app.config['DB_CONN_CFG'])
