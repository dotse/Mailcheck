import os
import pgdb
import datetime

from engine.config import Config


class Database:
	"""
	PostgreSQL specific database adapter.
	"""
	def __init__(self, configFile=None, logger=None):
		self.configParser = Config(configFile, logger=logger)

		self.logger = logger
		self.downTime = None
		self.connection = None
		self.transaction_cursor = None

	def connect(self):
		"""
		Connection to database. Settings are loaded from config.ini

		@raise DatabaseConnectionFailedException Raised when conneciton to database failed.
		"""
		host = self.configParser.get('database', 'host')
		db = self.configParser.get('database', 'database')
		user = self.configParser.get('database', 'username')
		password = self.configParser.get('database', 'password')

		try:
			self.connection = pgdb.connect(dsn=host+":"+db, user=user, password=password)
		except pgdb.DatabaseError, e:
			raise DatabaseConnectionFailedException(e)

	def close(self):
		"""Close database connection"""
		if self.connection is not None:
			self.connection.close()

	def fetch(self, sql, params=[], fetch_assoc=False):
		"""
		Fetch rows from the database. Note: should only be used for SELECT queries.

		@param sql:		SQL query. Use %s, %i to insert paramters in the query.
		@param params:	List with paramters for the query.
		@return:		Returns result or None if nothing was found.
		@raise DatabaseException: Raised if fetch failed.
		"""
		try:
			if self.connection == None:
				self.connect()

			cursor = self.connection.cursor()
			result = cursor.execute(sql, params)

			rows = []
			result = cursor.fetchall()

			if fetch_assoc is True:
				for row in result:
					assoc = {}
					i = 0
					for x in row:
						assoc[cursor.description[i][0]] = x
						i += 1
					rows.append(assoc)
			else:
				for row in result:
					rows.append(row)

			cursor.close()
			self.connection.commit()
			return rows
		except pgdb.DatabaseError, e:
			if str(e).find("no connection to the server") != -1:
				if self.logger:
					self.logger.error("Connection to server lost, attempting to reconnect: %s" % e)
				self.reconnect()
			else:
				raise DatabaseException(e)
		except Exception, e:
			raise DatabaseException(e)
		return None

	def query(self, sql, params=[]):
		"""
		Send a query to the database. Note: Should not be used if query returns anything.

		@param sql:		SQL query. Use %s, %i to insert paramters in the query.
		@param params:	List with paramters for the query.
		@raise DatabaseException: Raised if query failed.
		"""
		try:
			cursor = self.connection.cursor()
			cursor.execute(sql, params)

			self.connection.commit()
			cursor.close()

		except pgdb.DatabaseError, e:
			if str(e).find("no connection to the server"):
				if self.logger:
					self.logger.error("Connection to server lost, attempting to reconnect" % e)
				self.reconnect()
			else:
				raise DatabaseException(e)
		except Exception, e:
			raise DatabaseException(e)

	def begin(self):
		"""
		Begin a transaction
		"""
		if self.connection is not None:
			self.transaction_cursor = self.connection.cursor()

	def query_transaction(self, sql, params=[]):
		"""
		Add a new query to the transaction.
		Note: Queries can't return any values, that means no SELECT and RETURNING.

		@param sql:		SQL query. Use %s, %i to insert paramters in the query.
		@param params:	List with paramters for the query.
		@raise DatabaseException: Raised if query failed or begin() haven't been called.
		"""
		if self.transaction_cursor is None:
			raise DatabaseException("A transaction must be initialized with begin() first!")

		try:
			self.transaction_cursor.execute(sql, params)
		except Exception, e:
			raise DatabaseException('Failed to execute query: %s' % e)

	def fetch_transaction(self, sql, params=[]):
		if self.transaction_cursor is None:
			raise DatabaseException("A transaction must be initialized with begin() first!")

		try:
			self.transaction_cursor.execute(sql, params)
			return self.transaction_cursor.fetchall()
		except Exception, e:
			raise DatabaseException('Failed to execute query: %s' % e)

	def commit(self):
		"""
		Commit the transation started with begin(). Does automatic rollback if exception occurs during
		commit. Throws DatabaseException if begin() haven't been called.
		"""
		if self.transaction_cursor is None:
			raise DatabaseException("A transaction must be initialized with begin() first!")

		try:
			self.connection.commit()
		except Exception, e:
			self.rollback()
			raise DatabaseException('Commit failed: %s' % e)
		finally:
			self.transaction_cursor.close()
			self.transaction_cursor = None

	def rollback(self):
		"""
		Rollback the connection.
		"""
		if self.transaction_cursor is None:
			raise DatabaseException("A transaction must be initialized with begin() first!")

		try:
			self.connection.rollback()
			self.transaction_cursor.close()
			self.transaction_cursor = None
		except Exception, e:
			raise DatabaseException("Rollback failed: %s" % e)

	def reconnect(self):
		"""Attempt to create a connection to the database"""
		try:
			self.connect()
			if self.logger:
				self.logger.info("Reconnection successful")
			self.downTime = None
		except DatabaseConnectionFailedException, e:
			if self.logger:
				self.logger.error("Reconnect failed: %s" % e)
			self._notifySupport()
			raise

	def _notifySupport(self):
		if self.downTime == None:
			self.downTime = datetime.datetime.today()

			if self.configParser.getboolean('general', 'debug'):
				email = self.configParser.get('general', 'debug_problem_email')
			else:
				email = self.configParser.get('general', 'problem_email')
			message = """\
From: %s
To: %s
Subject: %s

%s
""" % ('mailcheck', email, "Database problem", "Mailcheck testengine can't connect to the database");
			SENDMAIL = "/usr/sbin/sendmail"
			p = os.popen("%s -t -i" % SENDMAIL, "w")
			p.write(message)
			p.close()

		diff = datetime.datetime.today()
		if (diff - self.downTime).seconds >= 60:
			self.downTime = None


class DatabaseException(Exception):
	pass


class DatabaseConnectionFailedException(DatabaseException):
	pass


if __name__ == "__main__":
	db = Database()
	db.connect()

	try:
		db.begin()
		db.query_transaction("UPDATE test SET finished = now() WHERE id = 374628373")
		db.query_transaction("UPDATE test SET ended = 2827361 WHERE id = 374628373")
		db.commit()
	except:
		print "rollback"
		db.rollback()
