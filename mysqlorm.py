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

	"""flag of connection"""
	conn = None #rethink about the mark of connection's open

	"""this function will be called when a class based on Model is defined"""
	def __init__(cls, name, bases, attrs):
		if cls.__base__ is not BaseModel:
			cls.connect()
		

	"""config global Model"""
	@classmethod
	def config(cls, **configs):
		cls.configs.update(configs)
	
	"""connect to mysql via singleton"""
	@classmethod
	def connect(cls):
		if not BaseModel.conn or not BaseModel.conn.open: # if not connected, new one, else use the exist
			BaseModel.conn = MySQLdb.connect(**cls.configs) 
		return BaseModel.conn

	"""close connection"""
	@classmethod
	def close(cls):
		BaseModel.conn.close()


class Model(BaseModel):
	__metaclass__ = BaseModel
