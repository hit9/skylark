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

class ProgrammingError(Exception): pass # exception 


class Database:

    """class to manage database connection"""

    # api:
    # return func
    # None Database.config(**configs)
    # cursor Database.execute(SQLstring)
    # int Database.query_times

    configs = { # default configs
            "host":"localhost" ,
            "port":3306, # int
            "db":"", # required
            "user":"", # required
            "passwd":"", # required
            "charset":"utf8"
            }
    conn = None # connection object for MySQLdb

    debug = True # debug as default

    query_times = 0

    SQL = None # SQL last time executed

    @classmethod
    def config(cls, debug = True,**configs):
        cls.configs.update(configs)
        cls.debug = debug

    @classmethod
    def connect(cls):
        if not cls.conn or not cls.conn.open: # if not connected, new one, else use the exist
            cls.conn = MySQLdb.connect(cursorclass=MySQLdb.cursors.DictCursor, **cls.configs)
        return cls.conn

    @classmethod
    def execute(cls, SQL): # execute SQL
        cursor = Database.connect().cursor()
        try:
            cursor.execute(SQL)
        except: # report SQL be made
            if cls.debug:
                raise ProgrammingError, "SQL be made:"+SQL
        cls.query_times = cls.query_times+1
        cls.SQL = SQL
        # add attribute 're' to cursor:store query matched rows number
        cursor.re = int(vg_cursor_matched_re.search(cursor._info).group(1)) if cursor._info else cursor.rowcount
        return cursor


class Leaf(object):

    def _expr(op):
        def _e(self, r):
            return Expr(left = self, right = r, op = op)
        return _e

    __lt__ = _expr(" < ")

    __le__ = _expr(" <= ")

    __gt__ = _expr(" > ")

    __ge__ = _expr(" >= ")

    __ne__ = _expr(" <> ")

    __eq__ = _expr(" = ")

    __and__ = _expr(" and ")

    __or__ = _expr(" or ")


class Expr(Leaf):

    # api
    # return func
    # str expr._tostr

    def __init__(self, left, right, op):
        self.left = left # the left 
        self.right = right # the right 
        self.op = op # the operator string

        self.exprstr = None # record exprstr
    
    @property
    def _tostr(self): # singleton get exprstr, set exprstr when needed
        if not self.exprstr:
            self.exprstr = self._str(self.left)+self.op+self._str(self.right)
        return self.exprstr

    def _str(self, side) :# turn some side to str in SQL
        if isinstance(side, Field):
            return side.fullname # return fullname if it's Field
        elif isinstance(side, Expr):
            return side._tostr
        else:
            return "'"+MySQLdb.escape_string(str(side))+"'" # escape_string
    

class EqExpr(Expr): # eq expr
    #
    # api:
    # (fieldname, valuestring) eqexpr._toitem
    #
    
    def __init__(self, left, right):
        super(EqExpr, self).__init__(left, right, " = ")

    @property
    def _toitem(self): # User.name == "name" => ("name", "name")
        return (self.left.name, str(self.right))


class FieldDescriptor(object): # descriptor for Field objs

    def __init__(self, field):
        self.name = field.name # field name
        self.field = field # field instance

    def __get__(self, instance, type = None):
        if instance: # if instance, return data
            return instance._data[self.name]
        return self.field # Model.field_name will return Field instance

    def __set__(self, instance, value):
        instance._data[self.name] = value


class Field(Leaf): # Field Class

    def __init__(self):

        self.primarykey = False # as default, Field instance not a primarykey

    def describe(self, name, model): # describe attr by FieldDescriptor
        self.name = name # field name(without table)
        self.model = model # model belongto
        self.fullname = self.model.table_name+"."+self.name # fullname, for quick get
        setattr(model, name, FieldDescriptor(self)) # add Descriptor

    def __eq__(self, r): # overload Leaf __eq__.return  EqExpr instance
        return EqExpr(left = self, right = r)


class PrimaryKey(Field):

    def __init__(self):
        self.primarykey = True 


class SelectResult(object): # wrap select result

    def __init__(self, model):
        self.model = model
        self.cursor = None
        self.flst = None

    
    @property
    def nfdct(self):# result data dict key <=> field instance pairs dict
        dct = {}
        for f in self.flst:
            if not dct.has_key(f.name):
                dct[f.name] = f
            else:
                dct[f.fullname] = f
        return dct

    def mddct(self, dct, nfdct): # model data_dict pasirs dict
        mlst = self.model.models
        b = dict((m, {}) for m in mlst)
        for k, v in dct.iteritems():
            field = nfdct[k]
            data_dct = b[field.model]
            data_dct[field.name] = v
        return b

    def fetchone(self):# fetchone a time
        dct = self.cursor.fetchone()

        if self.model.single:
            return self.model(**dct) if dct else None
        else:
            nfdct = self.nfdct
            b = self.mddct(dct, nfdct)
            return (m(**b[m]) for m in self.model.models)

    def fetchall(self):# fetchall result
        
        data = self.cursor.fetchall()

        if self.model.single:
            for dct in data:
                yield self.model(**dct)
        else:
            nfdct = self.nfdct

            for dct in data:
                b = self.mddct(dct, nfdct)
                yield (m(**(b[m])) for m in self.model.models)


class Query(object):# Runtime Query
    
    def __init__(self, model = None):

        self.model = model
        self.runtime = ( # infomation in single query => type:string
                "_where",
                "_set",
                "_orderby",
                "_select"
                )
        self.reset_runtime() # reset, to init runtime as attrs
        self.select_result = SelectResult(model) # store select result

    def reset_runtime(self):
        self.__dict__.update({}.fromkeys(self.runtime, "")) 

    def set_orderby(self, t): # t => (Field instance, True of False)
        s = " order by "+t[0].fullname
        if t[1]:
            s = s+" desc "
        self._orderby = s
    
    def set_select(self, flst): # flst => Field instance list
        primarykey = self.model.primarykey
        flst = list(flst) 
        if flst: # if no field figured out, select all as default
            if self.model.single:
                flst.append(primarykey) # add primarykey to select
            else:
                flst.extend(primarykey)
            flst = list(set(flst)) # remove duplicates
        else:  
            flst = self.model.get_field_lst()
        self.select_result.flst = flst # set select field list
        fstr = ", ".join([f.fullname for f in flst])
        self._select = fstr

    def set_where(self, lst, dct):
        lst = list(lst) # cast to list
        if self.model.single:
            fields = self.model.fields
            lst.extend([fields[k] == v for k, v in dct.iteritems()]) # for Model only, not JoinModel
        self._where = " where "+" and ".join([expr._tostr for expr in lst])


    def set_set(self, lst, dct):
        lst = list(lst) 
        if self.model.single:
            fields = self.model.fields
            primarykey = self.model.primarykey
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
        table = self.model.table_name
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

            if type in (2, 4):# update or delete, return 0/1
                re = cursor.re
            elif type is 1:# insert , return lastrowid
                re = cursor.lastrowid if cursor.re else None
            elif type is 3:
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


class MetaModel(type): # metaclass for 'single Model' Class

    def __init__(cls, name, bases , attrs):

        cls.table_name = cls.__name__.lower()

        fields = {} # name <=> fields pairs
        primarykey = None
        
        for name, attr in cls.__dict__.iteritems():
            if isinstance(attr, Field):
                attr.describe(name, cls) # describe attr
                fields[name] = attr
                if attr.primarykey:
                    primarykey = attr

        if primarykey is None: # default primarykey => 'id'
            primarykey = PrimaryKey()
            primarykey.describe('id', cls)
            fields['id'] = primarykey

        cls.fields = fields
        cls.primarykey = primarykey
        cls.query = Query(cls) # instance a Query for Model cls

    def __and__(self, m):
        if m.single:
            return JoinModel(self, m)
        else:
            m.models.insert(0, self)
            return m


class Model(object):

    __metaclass__ = MetaModel
    single = True # if joinModel

    def __init__(self, *lst, **dct):
        self._data = {}.fromkeys(self.fields.keys(), None) # init self._data
        self._data.update(dict(x._toitem for x in lst)) # update _data by expr lst
        self._data.update(dct)
        self._cache = self._data.copy()

    @property
    def data(self):
        return self._data

    @property
    def _id(self):
        return self._data[self.primarykey.name]

    @classmethod
    def get_field_lst(cls):
        return cls.fields.values()

    def set_id(self, _id):
        self._data[self.primarykey.name] = _id

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
            dct = dict(set(self._data.items()) - set(self._cache.items())) # only update changed data
            if not dct:
                return 1 # data not change
            re = model.at(self._id).update(**dct)
            if re:
                self._cache = self._data.copy() # sync cache after save
                return re #success update
        return 0

    def destroy(self):
        if self._id:
            model = self.__class__
            return model.at(self._id).delete()
        return 0

    @classmethod
    def select(cls, *flst):
        cls.query.set_select(flst)
        return cls.query.select()
    
    @classmethod
    def create(cls, *lst, **dct):
        cls.query.set_set(lst, dct)
        id = cls.query.insert()
        if id:
            dct[cls.primarykey.name] = id # add id to dct
            return cls(*lst, **dct)
        return None

    @classmethod
    def delete(cls):
        return cls.query.delete()

    @classmethod
    def update(cls, *lst, **dct):
        cls.query.set_set(lst, dct)
        return cls.query.update()

    @classmethod
    def where(cls, *lst, **dct):
        cls.query.set_where(lst, dct)
        return cls

    @classmethod
    def at(cls, _id):# find by id
        cls.where(cls.primarykey == _id)
        return cls

    @classmethod
    def orderby(cls, field, desc = False):
        cls.query.set_orderby((field, desc))
        return cls


class JoinModel(object):

    def __init__(self, *models):
        self.models = list(models) # cast to list
        self.single = False
        self.query = Query(self)

    def __and__(self, m):
        if m.single:# if  a Model, append to models
            self.models.append(m)
        else: # if JoinModel
            self.models.extend(m.models)
        return self

    @property
    def table_name(self):
        return ", ".join([m.table_name for m in self.models])

    @property
    def primarykey(self):
        return [m.primarykey for m in self.models]

    def get_field_lst(self):
        fls = []
        lst = [m.get_field_lst() for m in self.models]
        return sum(lst, [])

    def where(self, *lst):
        self.query.set_where(lst, {})
        return self

    def select(self, *lst):
        self.query.set_select(lst)
        return self.query.select()

    def update(self, *lst):
        self.query.set_set(lst, {})
        return self.query.update()

    def orderby(self, field, desc = False):
        self.query.set_orderby((field, desc))
        return self
