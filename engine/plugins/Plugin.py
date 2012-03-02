
from types import *


class Plugin(object):
	"""Base class for plugins"""
	STATUS_OK 			= 1
	STATUS_WARNING 		= 2
	STATUS_ERROR		= 3
	STATUS_UNKNOWN 		= 4

	requiredInput = []

	def __init__(self):
		self.input = {}
		self.result = None
		self.logger = None
		self.isChild = 0

	def setLogger(self, logger):
		self.logger = logger

	def setInput(self, key, value):
		"""Set input needed during the test (ex. domain)"""
		self.input[key] = value

	def getInput(self, key):
		"""Get input"""
		return self.input[key]

	def run(self):
		pass

	def hasRequiredInput(self):
		if len(self.requiredInput) > 0:
			return True
		return False

	def getRequiredInput(self):
		return self.requiredInput

	def getResult(self):
		return self.result

	def setResult(self, result):
		self.result = result


class PluginException(Exception):
	pass


class PluginConfig(object):
	"""Convenience class for getting plugin settings from the database"""

	def __init__(self, db):
		self.db = db

		self.values = {}
		result = self.db.fetch('SELECT key, value FROM plugin_config')
		if result:
			for r in result:
				self.values[r[0]] = r[1]

	def get(self, key, default=''):
		if key in self.values:
			return self.values[key]
		else:
			return default

	def _get(self, key):
		"""Get values from the database. Key can be a list of keys or a string."""
		keys = []
		if type(key) == type([]):
			for k in key:
				keys.append(k)
		else:
			keys.append(key)

		sql = '('
		for i in range(len(keys)):
			sql += '%s,'
		sql = sql[0:-1] + ')'

		out = {}
		result = self.db.fetch('SELECT key, value FROM plugin_config WHERE key in ' \
				+ sql, keys)
		if result:
			for r in result:
				out[r[0]] = r[1]

		return out


class PluginSockets(object):
	"""
	Storage for sockets that the plugins can use
	"""
	def __init__(self, logger=None):
		self.pluginSockets = []
		self.logger = logger

	def retr_sock(self):
		return self.pluginSockets

	def save_sock(self, pluginSockets):
		self.pluginSockets += pluginSockets
		return self.pluginSockets

	def close_all(self):
		"""
		Close all open sockets
		"""
		for i in self.pluginSockets:
			try:
				i.close()
			except Exception, e:
				if self.logger:
					self.logger.error('Failed to close socket: %s' % e)


class PluginResult(object):
	def __init__(self, db, logger=None):
		self.db = db
		self.logger = logger

	def load(self, plugin, domain, key, testId):
		"""
		Load saved output from a previous plugin.
		@param plugin:	Name of plugin
		@param domain:	Domain that got tested
		@param key:		Key used to save the output data
		@param testId:	ID of the test we want output from
		@return:		None if nothing if found. Dict with the result, if one is found.
		"""
		where = ''
		params = [domain, plugin, key]

		if testId is not None:
			where = " AND pr.test_id = %s"
			params.append(str(testId))

		rows = {}
		child_ids = []
		# Load first level items
		sql = "SELECT pr.name, pr.value_text, pr.value_numeric, pr.table_id, " \
				"pr.child_table_id FROM plugin_result pr, test t WHERE pr.test_id = t.id "\
				"AND t.domain = %s AND pr.plugin = %s AND pr.name = %s " + where
		result = self.db.fetch(sql, params, fetch_assoc=True)

		if len(result) == 0:
			return None

		for row in result:
			if 'child_table_id' in row and row['child_table_id'] is not None:
				child_ids.append(str(row['child_table_id']))
				if row['child_table_id'] not in rows:
					rows[row['child_table_id']] = {'data': []}
				rows[row['child_table_id']]['row'] = row
			else:
				rows = {row['name']: row['value_text']}
				return rows

		# Load second level items (child tables)
		sql = "SELECT pr.name, pr.value_text, pr.value_numeric, pr.table_id, " \
				"pr.child_table_id FROM plugin_result pr WHERE pr.table_id IN (" + \
				",".join(child_ids) + ")"
		result = self.db.fetch(sql, [], fetch_assoc=True)
		for row in result:
			rows[row['table_id']]['data'].append(row)

		out = {}
		for table_id in rows:
			name = rows[table_id]['row']['name']

			dict = {}
			for row in rows[table_id]['data']:
				if name not in out:
					out[name] = []

				dict[row['name']] = row['value_text']
			out[name].append(dict)

		return out

	def save(self, testId, pluginName, host, data):
		"""
		Save output from a plugin in the database.
		@param testId:		Test that is saving result
		@param pluginName:	Name of the executed plugin
		@param host:		Domain name we are testing
		@param data:		Dict with data
		"""
		# TODO:
		# * Saving and loading only support only "level" (child table)
		# * Numeric column is not used to save numeric values

		try:
			self.db.begin()
			for key in data:
				data_row = data[key]

				if type(data_row) == ListType:
					for row in data_row:
						sql = "INSERT INTO plugin_result (test_id, plugin, \"name\", table_id," \
								"child_table_id) VALUES(%s,%s,%s, nextval('table_id_seq'::regclass)," \
								" nextval('table_id_seq'::regclass)) RETURNING child_table_id"
						params = [str(testId), pluginName, key]
						child_table_id = self.db.fetch_transaction(sql, params)
						child_table_id = child_table_id[0][0]

						for value in row:
							sql = "INSERT INTO plugin_result (test_id, plugin, \"name\", " \
								"value_text, table_id) VALUES(%s,%s,%s,%s,%s)"
							params = [str(testId), pluginName, value, str(row[value]),
									str(child_table_id)]
							self.db.query(sql, params)
				else:
					sql = "INSERT INTO plugin_result (test_id, plugin, \"name\", value_text,"\
							" table_id) VALUES(%s,%s,%s,%s, nextval('table_id_seq'::regclass))"
					params = [str(testId), pluginName, key, data_row]
					self.db.query_transaction(sql, params)

		except Exception, e:
			self.db.rollback()
			if self.logger:
				self.logger('Failed to save PluginResult. Reason: %s' % e)
			return False

		self.db.commit()
		return True

	def verify_cert_load(self, plugin, host):
		sql = "SELECT DISTINCT ON (pr.value_text) EXTRACT(EPOCH FROM pr.created) " \
				"as unixtime, pr.value_text FROM plugin_result AS pr, test AS t WHERE " \
				"t.id = pr.test_id AND t.domain = %s AND pr.plugin = %s AND pr.name = %s"\
				" ORDER BY pr.value_text,created"
		params = [host, plugin, "ssl_serial"]
		result = []
		try:
			result = self.db.fetch(sql, params)
		except Exception, e:
			if self.logger:
				self.logger.error("Failed to fetch old cert from DB: %s" % e)

		rows = {}
		for row in result:
			rows[row[0]] = row[1]

		return rows


class Result:
	"""
	Stores and saves the result from a plugin.
	"""

	def __init__(self, plugin):
		self.plugin = plugin
		self.messages = []
		self.output = None
		self.result = None
		self.goldStarCount = 0
		self.finalStatus = None
		self.persist = False
		self.started = self.ended = None

	def getPluginName(self):
		"""
		Get the unique name of the plugin the result comes from
		"""
		return self.plugin.name

	def info(self, message, params=None, type='adv'):
		"""
		Store information text.
		@param message:		Key in the translation files
		@param params:		Tuple with paramters for the translation
		@param type:		Type of result (basic, adv or all). Selects which tab in the
							interface that shows the result. 'all' shows the message on both.
		"""
		self._addMessage(message, params, None, type)

	def warning(self, message, params=None, type='all'):
		"""
		Add a warning to the result.
		@param message:		Key in the translation files
		@param params:		Tuple with paramters for the translation, if needed. Default
		@param type:		Type of result (basic, adv or all). Selects which tab in the
							interface that shows the result. 'all' shows the message on both.
		"""
		self._addMessage(message, params, Plugin.STATUS_WARNING, type)

	def extra(self, message, params=None, type='all'):
		"""
		Add a extra text that appear in relation to the last info/warning/error.
		@param message:		URL
		@param type:		Type of result (basic, adv or all). Selects which tab in the
							interface that shows the result. 'all' shows the message on both.
		"""
		self._addMessage(message, params, -4, type)

	def extra_link(self, link, type='all'):
		"""
		Add a link that is automatically hyperlinked.
		@param link:		URL
		@param type:		Type of result (basic, adv or all). Selects which tab in the
							interface that shows the result. 'all' shows the message on both.
		"""
		self._addMessage(link, None, -3, type)

	def error(self, message, params=None, type='all'):
		"""
		Add an error message to the result.
		@param message:		Key in the translation files
		@param params:		Tuple with paramters for the translation, if needed. Default
		@param type:		Type of result (basic, adv or all). Selects which tab in the
							interface that shows the result. 'all' shows the message on both.
		"""
		self._addMessage(message, params, Plugin.STATUS_ERROR, type)

	def recommendation(self, message, params=None, type='all'):
		"""
		Add a recommendation to the end of a plugin result. Note that only one
		recommendation will be displayed by the view.

		@param message:		Key in the translation files
		@param params:		Tuple with paramters for the translation, if needed. Default
		@param type:		Type of result (basic, adv or all). Selects which tab in the
							interface that shows the result. 'all' shows the message on both.
		"""
		self._addMessage(message, params, -2, type)

	def goldstar(self, message, params=None):
		"""
		Add a gold star to the plugin result.

		@param message:		Key in the translation files
		@param params:		Tuple with paramters for the translation, if needed.
		"""
		self._addMessage(message, params, -1, 'all', goldstar=1)
		self.goldStarCount += 1

	def message(self, message, params=None, code=None, type='basic'):
		"""
		@deprecated	Use specific methods like, error,warning and info
		"""
		self._addMessage(message, params, code, type)

	def _addMessage(self, message, params=None, status=None, extra="basic",
					goldstar=0):
		if params is not None and type(params) is not type(()):
			params = (params,)
		if status is None:
			status = 0
		self.messages.append({'message': message, 'params': params, 'status': \
							status, 'type': extra, 'gold': goldstar})

	def setOutput(self, data, persist=True):
		self.output = data
		if persist:
			self.persist = True

	def getOutput(self):
		return self.output

	def setTestStatus(self, status=None):
		if status == None:
			status = Plugin.STATUS_OK

		self.finalStatus = status

	def getFinalStatus(self):
		return self.finalStatus

	def getGoldStarCount(self):
		return self.goldStarCount

	def setStartTime(self, started):
		self.started = started

	def setEndTime(self, ended):
		self.ended = ended

	def getRawMessages(self):
		return self.messages

	def __repr__(self):
		out = ''
		for m in self.messages:
			out += "M: %s, Params: %s, Code: %s, Type: %s\n" % (str(m['message']), \
					str(m['params']), str(m['status']), str(m['type']))
		if self.result != None:
			out += 'Test status: %s' % str(self.finalStatus)
		return out

	def save(self, db, testId):
		"""
		Saves plugin text and data output to the database.
		@param db:		Database adapter used to save data
		@param testId:	ID of the current test
		"""

		pluginName = self.plugin.__class__.__name__
		category = self.plugin.category

		db.begin()

		# Save the plugin result
		sql = "INSERT INTO plugin (test_id, plugin, status, category, started, " \
				"ended) VALUES(%s,%s,%s,%s,%s,%s) RETURNING id"
		params = [str(testId), pluginName, str(self.finalStatus), category,
				self.started, self.ended]
		plugin_id = db.fetch_transaction(sql, params)
		plugin_id = plugin_id[0][0]

		# Save text messags
		for m in self.messages:
			params = []
			value_text = m['message']
			value_numeric = m['status']
			extra = m['type']

			if m['gold'] > 0:
				name = "goldstar"
				value_numeric = m['gold']
			else:
				name = "output_text"
			# If we don't have any paramters, save a single row
			if m['params'] is None:
				sql = "INSERT INTO plugin_result (test_id, plugin, \"name\", value_text," \
						"value_numeric, table_id, extra) VALUES(%s, %s, %s, %s, %s, " \
						"nextval('table_id_seq'::regclass), %s)"
				params = [str(testId), pluginName, name, value_text, value_numeric, extra]
				db.query_transaction(sql, params)
			else:  # If we have parameters, save a new "table" with the rows
				sql = "INSERT INTO plugin_result (test_id, plugin, \"name\", value_text," \
						"value_numeric, table_id, child_table_id, extra) VALUES(%s, %s, %s, %s,"\
						"%s, nextval('table_id_seq'::regclass), " \
						"nextval('table_id_seq'::regclass),%s) RETURNING child_table_id"
				params = [str(testId), pluginName, name, value_text, value_numeric, extra]
				child_table_id = db.fetch_transaction(sql, params)
				child_table_id = child_table_id[0][0]

				for p in m['params']:
					sql = "INSERT INTO plugin_result (test_id, plugin, \"name\", value_text,"\
							"table_id) VALUES(%s,%s,%s,%s,%s)"
					params = [str(testId), pluginName, "param", p, str(child_table_id)]
					db.query_transaction(sql, params)

		db.commit()

		# Save output from plugin to database if we are supposed to
		if self.persist is True and type(self.output) == DictType:
			try:
				self.plugin.pluginResult.save(testId, pluginName,
											self.plugin.getInput('domain'), self.output)
			except Exception, e:
				if self.db.logger:
					self.db.logger("Failed to save plugin output to database. Reason: %s" % e)


class ResultException(Exception):
	pass


class LiveFeedback:
	"""
	Save live feedback information about the running test.
	"""
	def __init__(self, db=None, logger=None):
		self.db = db
		self.logger = logger

	def message(self, testId, message, params):
		"""
		Save a message about the current progress of the test.

		@param testId:		Id of the current test
		@param message:		Text message
		@param params:		Tuple with data that is part of the message
		"""
		if self.db == None:
			return

		a, v, args = parseExtraArgs(params)
		params = [str(message), int(testId)]
		for val in args:
			params.append(val)

		try:
			self.db.query('INSERT INTO live_feedback (message, test_id' + a + ') ' \
					'VALUES(%s, %i' + v + ')', params)
		except Exception, e:
			if self.logger:
				self.logger.error("Failed to insert live feedback data. %s" % e)


def parseExtraArgs(params):
	args = ()
	if params != None:
		if type(params) == type([]) or \
				type(params) == type(()):
			count = len(params)
			if count > 10:
				count = 10
			args = params[:count]
		else:
			args = tuple([params])
	a = v = ''
	retArgs = []
	for i in range(len(args)):
		a += ',arg' + str(i)
		v += ',%s'
		retArgs.append(str(args[i]))

	return a, v, retArgs


if __name__ == "__main__":
	import sys
	from os.path import dirname
	sys.path.append(dirname(sys.path[0]) + '/')
	from database import Database
	d = Database(configFile=dirname(dirname(sys.path[0])) + '/config/config.ini')
	d.connect()

	d = PluginResult(d)

	data = {'mx_record': [
			{'prio': 10, 'ip': '10.20.30.40', 'host': 'test.com'}
		]
	}

	data = {'test': 'testing stuff here', 'test2': 'testing2'}

	a = d.load("VerifyCert", "gatorhole.com", "ssl_serial", 11580)
	print a
