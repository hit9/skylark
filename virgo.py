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


    def _expr(op):
        def e(self, r):
            if isinstance(r, Expr): # if r is a expr
                self.expstr = self.expstr+" "+op+" "+r.expstr
                return self
            return False
        return e

    __and__ = _expr("and")

    __or__ = _expr("or")



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

    def _expr(op): # function generator
        def e(self, r):
            if isinstance(r, Field):
                s = r.fullname
            else :
                s = "'"+str(r)+"'"
            return Expr(self.fullname+op+s)
        return e

    __eq__ = _expr(" = ")

    __lt__ = _expr(" < ")

    __le__ = _expr(" <= ")

    __gt__ = _expr(" > ")

    __ge__ = _expr(" >= ")

    __ne__ = _expr(" <> ") 
    

class PrimaryKey(Field):

    def __init__(self):
        self.primarykey = True


class QueryRuntime(object): # store Single SQL Runtime information
    
    def __init__(self, table_name, primarykey):
        self.table = table_name
        self.primarykey = primarykey # primarykey instance
        self.ks = (
            "where",  # runtime.where  => expr 
            "set",  # set  => data dct to set into db
            "orderby", # (field, desc) tuple , desc => bool
            "select" # fields lst to select from db
        )
        self.reset()
    

    def reset(self):
        self.__dict__.update({}.fromkeys(self.ks, None))

    @property
    def _orderby(self):
        restr = ""
        a = self.orderby
        if a:
            restr =  " order by "+a[0].fullname
            if a[1]:
                restr = restr+" desc "
        return restr

    @property
    def _set(self): # make set string
        dct = self.set
        kn = self.primarykey.name
        setstr = ""
        if dct: # pop primarykey, it can not be set
            if kn in dct.keys():
                dct.pop(kn)
            setstr = " set " + ", ".join([self.table+"."+x+" = '"+MySQLdb.escape_string(str(y))+"'" for x, y in dct.iteritems() if y])
        return setstr

    @property
    def _select(self):#make select fields str
        flst = self.select
        if flst:
            fnlst = []
            pk = None
            for f in flst:
                if f is self.primarykey:
                    pk = f
                fnlst.append(f.name)
            if not pk:#if no primarykey in flst
                fnlst.append(self.primarykey.name)

            fstr = ", ".join(fnlst)
        else:
            fstr = "*"
        return fstr

    @property
    def _where(self):
        if self.where:
            return  " where "+self.where.expstr
        return ""

    def makeSQL(self, type = None):
        if type == 1: #insert
            SQL = "insert into "+self.table+" "+self._set
        elif type == 2:#update
            SQL = "update "+self.table+" "+self._set+self._where
        elif type == 3:#select
            SQL = "select "+self._select+" from "+self.table+self._where+self._orderby
        elif type == 4:#delete
            SQL = "delete from "+self.table+self._where
        print SQL
        return SQL
    

class Query(object): # one Model  => one Query instance

    def __init__(self, model):
        self.model = model 
        self.runtime = QueryRuntime(model._info.table_name, model._info.primarykey) # make  an empty runtime

    def set_set(self, dct):
        self.runtime.set = dct

    def set_where(self, expr):
        self.runtime.where = expr

    def set_orderby(self, field):
        self.runtime.orderby = field

    def set_select(self, fields):
        self.runtime.select = fields

    def _Q(type): 
        def func(self):
            re = None
            SQL = self.runtime.makeSQL(type = type)
            cursor = Database.execute(SQL)
            if type in (2, 4):# if update or delete, return success or failure
                re = cursor.re
            elif type is 1:# if insert , return lastrowid
                re = cursor.lastrowid if  cursor.re else None
            elif type is 3:# if select
                re = cursor # return cursor obj
            self.runtime.reset() # reset runtime
            return re
        return func

    insert = _Q(1)

    update = _Q(2)

    select = _Q(3)

    delete = _Q(4)

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
        self._data.update(data)
        self._cache = self._data.copy()

    @property
    def _primarykey(self):
        return self._info.primarykey.name

    @property
    def _id(self):
        return self._data[self._primarykey]

    def set_id(self, _id):
        self._data[self._primarykey] = _id

    def save(self):
        model = self.__class__
        if not self._id:
            model._query.set_set(self._data)
            id = model._query.insert()
            if id:
                self.set_id(id)
                self._cache = self._data.copy() # sync cache after save
                return True
        else:
            model._query.set_where(model._info.primarykey ==  self._id)
            dct = dict(set(self._data.items()) - set(self._cache.items())) # only update changed data
            model._query.set_set(dct)
            re = model._query.update()
            if re:
                self._cache = self._data.copy() # sync cache after save
                return True
        return False


    @classmethod
    def create(cls, **data):
        cls._query.set_set(data)
        id = cls._query.insert() # insert return id
        if id:
            data[cls._info.primarykey.name] = id # add id to data dct
            return cls(**data)
        return None

    @classmethod
    def where(cls, expr):
        cls._query.set_where(expr)
        return cls

    @classmethod
    def orderby(cls, field, desc = False):
        cls._query.set_orderby((field, desc))
        return cls

    @classmethod
    def select(cls, *flst):
        cls._query.set_select(flst)
        cur = cls._query.select()
        for dct in cur.fetchall():
            yield cls(**dct)

    @classmethod
    def find(cls, key):
        cls._query.set_where(cls._info.primarykey == key)
        cur = cls._query.select()
        return cls(**cur.fetchone())

    @classmethod
    def delete(cls):
        return cls._query.delete()
