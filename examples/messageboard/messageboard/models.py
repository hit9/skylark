# coding=utf8


from CURD import Database, Model, Field, PrimaryKey
from messageboard import app


class Message(Model):
    title = Field()
    content = Field()
    create_at = Field()


Database.config(**app.config['DB_CONN_CFG'])
