"""
test code so far:
---------------------------------- test code -------------------
from mysqlorm import *

Database.config(db = "mydb", user = 'root', passwd = "123456", charset = "utf8")

class User(Model):
    username = Field()
    email = Field()

user = User.find(1)

print user._data

----------------------------------------------------------------

implemented APIs and Attributes

model_instance Model.create(**field_value)

list Model.fields

str Model.table_name

model_instance Model.find(key)

model_instance.save()



"""

import MySQLdb
import MySQLdb.cursors 
import re

vg_cursor_matched_re = re.compile(r'Rows matched: (\d+)')

vg_join_fields = lambda dct : ", ".join([x+"='"+MySQLdb.escape_string(str(y))+"'" for x, y in dct.iteritems()])

class Database:
    """class to manage Database connection"""

    configs = { # default configs for connection
            'host' : 'localhost' , # mysql host
            'port' : 3306 , # mysql port
            'db' : "" , # database name
            'user' : "" ,  # mysql user
            'passwd' : "" , # mysql passwd for user
            'charset' : "utf8"   # mysql connection charset, default set as utf8
            }

    conn = None # connection object of MySQLdb

    @classmethod
    def config(cls, **configs):
        cls.configs.update(configs)

    @classmethod
    def connect(cls):
        if not cls.conn or not cls.conn.open: # if not connected, new one, else use the exist
            cls.conn = MySQLdb.connect(cursorclass=MySQLdb.cursors.DictCursor, **cls.configs) 
        return cls.conn

    @classmethod
    def close(cls):
        cls.conn.close()

    @classmethod
    def get_con(cls):
        return cls.connect()

    @classmethod
    def query(cls, sql):
        cursor = Database.get_con().cursor()
        setattr(cursor, 're', None) # add attribute 'match' to cursor:store query matched rows number
        cursor.execute(sql)
        cursor.re = int(vg_cursor_matched_re.search(cursor._info).group(1)) if cursor._info else cursor.rowcount
        return cursor



class Field(object):

    def __init__(self, primarykey = False):
        self.name = None
        primarykey = False

    def __get__(self, instance, type = None):
        if instance:
            return instance._data[self.name]
        return self
    def __set__(self, instance, value):
        instance._data[self.name] = value


class PrimaryKey(Field):

    def __init__(self):
        self.primarykey = True


class MetaModel(type):

    def __init__(cls, name, bases , attrs):

        cls.table_name = cls.__name__.lower() 
        cls.primarykey = 'id'
        cls._data = {'id':None}

        for name, attr in cls.__dict__.iteritems():
            if isinstance(attr, Field):
                attr.name = name
                cls._data[name] = None
            if isinstance(attr, PrimaryKey):
                cls.primarykey = name
                cls._data.pop('id')
        cls.fields = cls._data.keys()


class Model(object):

    __metaclass__ = MetaModel

    def __init__(self, **attrs):
        self._data.update(attrs)
        self._cache = self._data.copy() # cache data last time changed 
        self.sync = False # if this object data sync to database

    @classmethod
    def obj_from(cls, data_dct): # return a instance marked sync True from a data_dct
        obj = cls(**data_dct)
        obj.sync = True
        return obj

    def data_changed(self):# get changed data of this object
        return dict(set(self._data.iteritems())-set(self._cache.iteritems()))
        
    def commit_cache(self): # commit cache after save success
        self._cache = self._data.copy()

    def save(self): # return True for success
        data = dict((x, y) for x, y in self._data.iteritems() if y) 
        if not self.sync :
            if  self.__class__.insert(data):
                self.sync = True # sync success
                self.commit_cache()
                return True # success save
        else:
            if self.update_by_key() :
                self.commit_cache()
                return True
        return False # failed

    @classmethod
    def insert(cls, dct): # just insert one row to db, do nothing to the obj
        cur = Database.query("insert into "+cls.table_name+" set "+vg_join_fields(dct))
        return cur.re # return 0 for failure, else for success

    def update(self, conditions):# where conditions
        dct = self.data_changed()
        if dct:
            cur = Database.query("update "+self.table_name+" set "+vg_join_fields(dct)+" where "+conditions) # where conditions temporarily as string~
            return cur.re # return 0 for failuer ...
        return 1 # noting to update

    def update_by_key(self): # update one row by primarykey
        return self.update(self.primarykey+"="+str(self._data[self.primarykey]))

    @classmethod
    def select(cls):pass

    @classmethod
    def create(cls, **dct):
        return cls.obj_from(dct) if cls.insert(dct) else None # if failed, return None

    @classmethod
    def find(cls, key): # find one row by primarykey
        dct = Database.query("select * from "+cls.table_name+" where "+vg_join_fields({cls.primarykey:key})).fetchone()
        return cls.obj_from(dct) if dct else None # if not found, return None
