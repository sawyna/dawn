import MySQLdb as mysql

class DB(object):
	def __init__(self, host, port, user, password, db_name):
		self.host = host
		self.port = port
		self.user = user
		self.password = password
		self.db_name = db_name
		self.db = mysql.connect(host, user, password, db_name, port)
		self.cursor = self.db.cursor()

	def reconnect(self):
		self.db = mysql.connect(self.host, self.user, self.password, self.db_name, self.port)
		self.cursor = self.db.cursor()

	def get(self, sqlQuery):
		self.reconnect()
		print sqlQuery
		self.cursor.execute(sqlQuery)
		val = self.cursor.fetchone()
		self.close()
		print val
		return val

	def execute(self, sqlQuery):
		self.reconnect()
		print sqlQuery
		try:
			self.cursor.execute(sqlQuery)
			self.db.commit()
			print "Succesfully inserted data into db"
			return True
		except:
			self.db.rollback()
			print "Failed to insert data into db"
			return False
		self.close()

	def close(self):
		self.db.close()
		print "Db connection closed"