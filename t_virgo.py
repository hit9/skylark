#
# ++ @  @ ++  ++++++++
#  ++    ++   ++
#   ++  ++    ++  ++++
#    ++++     ++     +
#     ++      ++++++++
#              
#
#   LOW LEVEL & SIMPLE & LIGHTWEIGHT
#
#   E-mail:nz2324@126.com
#
#   URL:http://hit9.org

import re
import MySQLdb
import MySQLdb.cursors


vg_cursor_matched_re = re.compile(r'Rows matched: (\d+)')


class Database:
    """class to manage Database connection"""

    configs = { # default configs for connection
            'host' : 'localhost' , 
            'port' : 3306 , 
            'db' : "" , 
            'user' : "" , 
            'passwd' : "" ,
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
    def execute(cls, sql): # execute SQL
        cursor = Database.connect().cursor()
        cursor.execute(sql)

        # add attribute 're' to cursor:store query matched rows number
        cursor.re = int(vg_cursor_matched_re.search(cursor._info).group(1)) if cursor._info else cursor.rowcount
        return cursor
    # About this cursor:
    # cursor.re  =>  matched rows number
    # cursor.lastrowid  => record primarykey value of row last insert 


class Expr(object):

    def __init__(self, expstr):
        self.expstr = expstr


class FieldDescriptor(object): # descriptor for Field objs

    def __init__(self, field):
        self.name = field.name # field name
        self.field = field # field object

    def __get__(self, instance, type = None):
        if instance:
            return instance._data[self.name]
        return self.field
    def __set__(self, instance, value):
        instance._data[self.name] = value

    

class Field(object): # Field Object

    name = None 
    model = None # Model Class
    primarykey = False # if primarykey

    def describe(self, name, model): # describe attr by FieldDescriptor
        self.name = name
        self.model = model
        setattr(model, name, FieldDescriptor(self))

    @property
    def fullname(self):
        return self.model._info.table_name+"."+self.name

    def _expr(op):
        def e(self, r):
            if isinstance(r, Field):
                s = r.fullname
            else :
                s = "'"+str(r)+"'"
            return Expr(self.fullname+op+s)
        return e

    __eq__ = _expr(" = ")
    

class PrimaryKey(Field):

    def __init__(self):
        self.primarykey = True


class Query(object): # one Model  => one Query instance

    def __init__(self, model):
        self.model = model
        self._where = None 

    @property
    def _table(self):# get Model's table name
        return self.model._info.table_name


    def join_f_v(self, dct): # join {fields:value} dict into "field = 'value', ..." if value
        return ", ".join([self._table+"."+x+" = '"+MySQLdb.escape_string(str(y))+"'" for x, y in dct.iteritems() if y])

    def insert(self, dct):
        SQL = "insert into "+self._table+" set "+self.join_f_v(dct)
        return Database.execute(SQL)  # return a cursor
    """
    def update(self, dct):
        where = self._where if self._where else ""
        SQL = "update "+self._table+" set "+self.join_f_v(dct)+where
        return Database.execute(SQL)

    def where(self, where):
        self._where = where
        return self"""

class ModelInfo(object): # one Model => one  ModelInfo instance .store info of Model Class

    def __init__(self, 
            table_name = None, # Model class 's table name
            primarykey = None, # PrimaryKey instance
            fields  = None     # fields name dct
            ):
        self.table_name = table_name
        self.primarykey = primarykey
        self.fields = fields



class MetaModel(type):

    def __init__(cls, name, bases , attrs):

        table_name = cls.__name__.lower()  
        fields = [] 
        primarykey = None 
        
        for name, attr in cls.__dict__.iteritems():
            if isinstance(attr, Field):
                attr.describe(name, cls) # describe attr
                fields.append(name)
                if attr.primarykey:
                    primarykey = attr

        if primarykey is None: # default primarykey is id
            primarykey = PrimaryKey()
            primarykey.describe('id', cls)
            fields.append('id')

        # set attributes for Model Class
        cls._info = ModelInfo(
                table_name = table_name, 
                primarykey = primarykey, 
                fields = fields
                )       

        cls._query = Query(cls) # instance a Query for Model cls


class Model(object):

    __metaclass__ = MetaModel

    def __init__(self, **data):

        self._data = {}.fromkeys(self._info.fields, None)
        if data: 
            self._data.update(data) 
        self._data.update(data)
        self._cache = self._data.copy()
        self._db = False # if this a stored in db obj

    @property
    def _primarykey(self):
        return self._info.primarykey.name

    @property
    def _id(self):
        return self._data[self._primarykey]

    def save(self):
        model = self.__class__
        if not self._db:
            cur = model._query.insert(self._data)
            if cur.re:
                self._db = True 
                self._data[self._primarykey] = cur.lastrowid
                self._cache = self._data.copy() # sync cache after save
                return True
        else:pass
        return False

    @classmethod
    def obj_fromdb(cls, data): # make an instance by data_dct, which _db = True
        obj = cls(**data)
        obj._db = True
        return obj

    @classmethod
    def create(cls, **data):
        cur = cls._query.insert(data)
        if cur.re:
            data[cls._info.primarykey.name] = cur.lastrowid # add id to data dct
            return cls.obj_fromdb(data)
        return None
