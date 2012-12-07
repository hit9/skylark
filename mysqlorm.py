""""
test code so far:


from mysqlorm import *

Database.config(db = "mydb", user = 'root', passwd = "123456", charset = "utf8")

class Model(BaseModel):
	__metaclass__ = MetaModel

class User(Model):pass

class Post(Model):pass

print User().__dict__


"""

import MySQLdb

class Database:
	"""class to manage Database connection"""

	configs = { # default configs for connection
		'host' : 'localhost' , # mysql host
		'port' : 3306 , # mysql port
		'db' : "" , # database name
		'user' : "" ,  # mysql user
		'passwd' : "" , # mysql passwd for user
		'charset' : "utf8"  # mysql connection charset, default set as utf8
	}

	conn = None # connection object of MySQLdb
	
	@classmethod
	def config(cls, **configs):
		"""update configs for  Database connection.
default configs:
	configs = {
		'host' : 'localhost' , # mysql host
		'port' : 3306 , # mysql port
		'db' : "" , # database name
		'user' : "" ,  # mysql user
		'passwd' : "" , # mysql passwd for user
		'charset' : "utf8" # mysql connection charset, default set as utf8
	}"""
		cls.configs.update(configs)
	
	@classmethod
	def connect(cls):
		"""connect to mysql (singleton)"""
		if not cls.conn or not cls.conn.open: # if not connected, new one, else use the exist
			cls.conn = MySQLdb.connect(**cls.configs) 
		return cls.conn

	@classmethod
	def close(cls):
		"""close connection to mysql"""
		cls.conn.close()


class MetaModel(type):
	"""Any Model's  MetaClass"""

	def __init__(cls, name, bases , attrs):
		if cls.__base__ is not BaseModel: # if the class is not the direct subclass of BaseModel
			cls.table_name = cls.__name__.lower() # set table name


class BaseModel(object):
	"""Any Model based on this Class"""
	fields = [] # cache table fields
	primarykey = 'id' # default primary key for Model

	def __init__(self):
		"""Model init will update its attributes"""
		self.__dict__.update({}.fromkeys(self.get_fields(), None))

	def save(self):
		"""write data from model object into database"""
		pass

	@classmethod
	def get_fields(cls):
		"""get table's fields list."""
		if not cls.fields: # if cls.fields is [], get it from database, else use cls.fields
			cursor = Database.connect().cursor(cursorclass=MySQLdb.cursors.DictCursor) # get a dict cursor
			cursor.execute("show columns from "+cls.table_name) # use classname's lower case as table name
			d = cursor.fetchall() # fields dict
			cls.fields = [x['Field'] for x in d]
		return cls.fields
