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
#   E-mail : nz2324@126.com
#
#   URL : http://hit9.org
#   Licence : BSD
#   
#   Permission to use, copy, modify, and distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.
#

import re
import MySQLdb
import MySQLdb.cursors


vg_cursor_matched_re = re.compile(r'Rows matched: (\d+)')


class Database:
    
    #
    # api:
    # None Database.config(**configs)
    # cursor Database.execute(sql)
    # int Database.query_times  # count for query times


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

    debug = True # if under debug

    query_times = 0

    @classmethod
    def config(cls, debug = True, **configs):
        cls.configs.update(configs)
        cls.debug = debug

    @classmethod
    def connect(cls):
        if not cls.conn or not cls.conn.open: # if not connected, new one, else use the exist
            cls.conn = MySQLdb.connect(cursorclass=MySQLdb.cursors.DictCursor, **cls.configs) 
        return cls.conn

    @classmethod
    def execute(cls, sql): # execute SQL
        cursor = Database.connect().cursor()
        try:
            cursor.execute(sql)
        except: # report SQL be made
            if cls.debug:
                raise SQLSyntaxError, sql
        cls.query_times = cls.query_times+1
        # add attribute 're' to cursor:store query matched rows number
        cursor.re = int(vg_cursor_matched_re.search(cursor._info).group(1)) if cursor._info else cursor.rowcount
        return cursor
    # About this cursor:
    # cursor.re  =>  matched rows number
    # cursor.lastrowid  => record primarykey value of row last insert 


class SQLSyntaxError(Exception):pass

class Expr(object):

    #
    # api:
    # str expr._tostr
    #


    def __init__(self, left, right, op, exprstr = None):
        self.left = left # the left field
        self.right = right # the right , field or string
        self.op = op # the operator string
        self.exprstr = exprstr

    
    @property
    def _tostr(self): # singleton get exprstr
        if not self.exprstr:
            self.exprstr =  self.left.fullname+self.op+self._str(self.right)
        return self.exprstr

    def _str(self, side) :# turn some side to str in SQL
        if isinstance(side, Field):
            return side.fullname
        else:
            return "'"+MySQLdb.escape_string(str(side))+"'" # escape_string

    
    def _expr(op):
        def e(self, r_expr): # return expr instance
            if isinstance(r_expr, Expr):#if r_expr is Expr instance
                self.exprstr =  self._tostr+" "+op+" "+r_expr._tostr
                return self
            return None
        return e

    __and__ = _expr("and")

    __or__ = _expr("or")


class EqExpr(Expr): # eq expr
    #
    # api:
    # (fieldname, valuestring) eqexpr._toitem 
    #
    
    def __init__(self, left, right, exprstr = None):
        self.op = " = "
        self.left = left
        self.right = right
        self.exprstr = None

    @property
    def _toitem(self): # User.name == "name" => ("name", "name")
        return (self.left.name, str(self.right))


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
        def e(self, r): # return Expr instance
            return Expr(left = self, right = r, op = op)
        return e

    def __eq__(self, r):
        return EqExpr(left = self, right = r)

    __lt__ = _expr(" < ")

    __le__ = _expr(" <= ")

    __gt__ = _expr(" > ")

    __ge__ = _expr(" >= ")

    __ne__ = _expr(" <> ")


class PrimaryKey(Field):

    def __init__(self):
        self.primarykey = True


class SelectResult(object): # wrap select result

    def __init__(self, model):
        self.model = model
        self.cursor = None


    def fetchall(self):# fetchall result
        for dct in self.cursor.fetchall():
            yield self.model(**dct)

    def fetchone(self):# fetchone a time
        dct = self.cursor.fetchone()
        return self.model(**dct) if dct else None

    @property
    def to_tuple(self):
        return self.cursor.fetchall()


class Query(object):

    def __init__(self, model = None):

        self.model = model
        self.runtime = ( # record infomation in single query,
                "_where", 
                "_set", 
                "_orderby", 
                "_select" 
                )
        self.reset_runtime()
        self.select_result = SelectResult(model)


    def reset_runtime(self):
        self.__dict__.update({}.fromkeys(self.runtime, ""))


    @property
    def _primarykey(self): # primarykey
        return self.model._info.primarykey

    @property
    def _table(self):
        return self.model._info.table_name

    def set_orderby(self, t): # t => (Field instance, True of False)
        s = " order by "+t[0].fullname
        if t[1]:
            s = s+" desc "
        self._orderby = s

    def set_select(self, flst): # flst => Field instance list
        if flst:
            fnlst = []
            pk = None
            for f in flst:
                if f is self._primarykey:
                    pk = f
                fnlst.append(f.name)
            if not pk:#if no primarykey in flst
                fnlst.append(self._primarykey.name)

            fstr = ", ".join(fnlst)
        else:
            fstr = "*"
        self._select = fstr

    def set_where(self, lst, dct):
        lst = list(lst)
        fields = self.model._info.fields
        lst.extend([fields[k] == v for k, v in dct.iteritems()])
        self._where = " where "+" and ".join([expr._tostr for expr in lst])


    def set_set(self, lst, dct):
        lst = list(lst) # cast to list type
        fields = self.model._info.fields
        primarykey = self._primarykey
        lst.extend([fields[k] == v for k, v in dct.iteritems() if fields[k] is not primarykey])
        self._set = " set " + ", ".join([expr._tostr for expr in lst])
 
    def _G(name, default):
        @property
        def g(self):
            if self.__dict__[name]:
                return self.__dict__[name]
            return default
        return g

    get_orderby = _G("_orderby", "")

    get_select = _G("_select", "*")

    get_set = _G("_set", "")

    get_where = _G("_where", "")

    def makeSQL(self, type = None):
        table = self._table
        if type == 1: #insert
            SQL = "insert into "+table+" "+self.get_set
        elif type == 2:#update
            SQL = "update "+table+" "+self.get_set+self.get_where
        elif type == 3:#select
            SQL = "select "+self.get_select+" from "+table+self.get_where+self.get_orderby
        elif type == 4:#delete
            SQL = "delete from "+table+self.get_where
        return SQL   

    def _Q(type): # function generator for CURD
        def func(self):
            re = None
            SQL = self.makeSQL(type = type)
            cursor = Database.execute(SQL)
            if type in (2, 4):# if update or delete, return success or failure
                re = cursor.re
            elif type is 1:# if insert , return lastrowid
                re = cursor.lastrowid if cursor.re else None
            elif type is 3:# if select
                self.select_result.cursor = cursor # reset select_result's cursor
                re = self.select_result
            self.reset_runtime() # reset runtime
            return re
        return func

    #generate CURD Functions

    insert = _Q(1)

    update = _Q(2)

    select = _Q(3)

    delete = _Q(4)


class ModelInfo(object): # one Model => one ModelInfo instance .store info of Model Class

    def __init__(self,
            table_name = None, # Model class 's table name
            primarykey = None, # PrimaryKey instance
            fields = None # dict {name:field}
            ):
        self.table_name = table_name
        self.primarykey = primarykey
        self.fields = fields # name fields pairs dict


class MetaModel(type):

    def __init__(cls, name, bases , attrs):

        table_name = cls.__name__.lower()
        fields = {} # name <=> fields pairs
        primarykey = None

        for name, attr in cls.__dict__.iteritems():
            if isinstance(attr, Field):
                attr.describe(name, cls) # describe attr
                fields[name] = attr
                if attr.primarykey:
                    primarykey = attr

        if primarykey is None: # default primarykey is id
            primarykey = PrimaryKey()
            primarykey.describe('id', cls)
            fields['id'] = primarykey

        # set attributes for Model Class
        cls._info = ModelInfo(
                table_name = table_name,
                primarykey = primarykey,
                fields = fields
                )

        cls.query = Query(cls) # instance a Query for Model cls

    @property
    def _primarykey(self):
        return self._info.primarykey


class Model(object):

    __metaclass__ = MetaModel


    def __init__(self, *lst, **dct):
        fields = self._info.fields
        self._data = {}.fromkeys(fields.keys(), None) # init self._data
        self._data.update(dict(x._toitem for x in lst)) # update _data by expr lst
        self._data.update(dct)
        self._cache = self._data.copy()

    @property
    def to_dict(self):
        return self._data

    @property
    def _primarykey(self):
        return self._info.primarykey

    @property 
    def _id(self):
        return self._data[self._primarykey.name]

    def set_id(self, _id):
        self._data[self._primarykey.name] = _id

    def save(self):
        model = self.__class__
        if not self._id: # insert one record
            model.query.set_set([], self._data)
            id = model.query.insert()
            if id:
                self.set_id(id)
                self._cache = self._data.copy() # sync cache after save
                return id
        else:
            model.where(model._primarykey == self._id)
            dct = dict(set(self._data.items()) - set(self._cache.items())) # only update changed data
            if not dct:
                return 1 # data not change
            model.query.set_set([], dct)
            re = model.query.update()
            if re:
                self._cache = self._data.copy() # sync cache after save
                return re #success update
        return 0

    def destroy(self):
        if self._id:
            model = self.__class__
            model.where(model._info.primarykey == self._id)
            return model.query.delete()
        return 0

    @classmethod
    def create(cls, *lst, **dct):
        cls.query.set_set(lst, dct)
        id = cls.query.insert()
        if id:
            dct[cls._primarykey.name] = id  # add id to dct
            return cls(*lst, **dct)
        return None

    @classmethod
    def where(cls, *lst, **dct):
        cls.query.set_where(lst, dct)
        return cls

    @classmethod
    def at(cls, _id):# find by id
        cls.where(cls._primarykey == _id)
        return cls

    @classmethod
    def orderby(cls, field, desc = False):
        cls.query.set_orderby((field, desc))
        return cls

    @classmethod
    def select(cls, *flst): 
        cls.query.set_select(flst)
        return cls.query.select()

    @classmethod
    def delete(cls):
        return cls.query.delete()

    @classmethod
    def update(cls, *lst, **dct):
        cls.query.set_set(lst, dct)
        return  cls.query.update()
