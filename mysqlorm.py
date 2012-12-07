"""
test code so far:

------------------- ------------------ ---------------

from mysqlorm import *

BaseModel.config(db = "mydb", user = "root", passwd = "123456", charset = "utf8") # db & table: mydb.user:

class Model(BaseModel): # connect to mysql when this class was defined
	__metaclass__ = BaseModel

class User(Model):pass

print User.__dict__

------------------- ------------------ ---------------


"""

import MySQLdb

class BaseModel(type):

	"""configs default"""
	configs = {
		'host' : 'localhost' , # mysql host
		'port' : 3306 , # mysql port
		'db' : "" , # database name
		'user' : "" ,  # mysql user
		'passwd' : "" , # mysql passwd for user
		'charset' : "utf8" # mysql connection charset, default set as utf8
	}

	conn = None

	def __init__(cls, name, bases, attrs):
		cls.connect() # connect to mysql

		if cls.__base__ is not BaseModel: # if this is not the direct subclass of BaseModel
			for cols in cls.get_columns_dict():
				setattr(cls, cols['Field'], None)

	@classmethod
	def config(cls, **configs):
		cls.configs.update(configs)
	
	"""connect to mysql # singleton"""
	@classmethod
	def connect(cls):
		if not BaseModel.conn or not BaseModel.conn.open: # if not connected, new one, else use the exist
			BaseModel.conn = MySQLdb.connect(**cls.configs) 
		return BaseModel.conn

	"""close connection to mysql"""
	@classmethod
	def close(cls):
		BaseModel.conn.close()

	"""exec_sql function."""
	# here need a function for all SQL query


	"""get table's columns dict"""
	@classmethod
	def get_columns_dict(cls):
		cursor = BaseModel.conn.cursor(cursorclass=MySQLdb.cursors.DictCursor) # get a dict cursor
		cursor.execute("show columns from "+cls.__name__.lower()) # use classname's lower case as table name
		return cursor.fetchall()

	"""create a record"""
	@classmethod 
	def create(cls, **fields):
		pass
