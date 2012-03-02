import os
import sys
import datetime
import getopt
from socket import getfqdn

from engine.log import create_logger, log_level_parser
from engine.config import Config
from engine.database import (Database,
							DatabaseException,
							DatabaseConnectionFailedException)
from engine.plugins.Plugin import (PluginConfig,
									PluginResult,
									PluginException,
									PluginSockets,
									LiveFeedback,
									Result,
									ResultException)
from engine.util import traceback_as_str


class TestRunner(object):
	"""Loads and runs a specific test"""

	def __init__(self, logger, options=None):
		self.results = {}
		self.running = False
		self.logger = logger
		self.options = options or []

		self.pluginTotal = 0  # total plugins to be executed
		self.pluginNumber = 0  # number of executed plugins

		self.testStatus = 0
		self.testGoldCount = 0

		# list of all possible tests we can run
		self.availableFastPlugins = [
			'MXRecord',
			'MXRecordPublic',
			'MXRecordDuplicate',
			'MXRecordCNAME',
			'MXRecordDiffering',
			'MXRecordPTR',
			'Blacklist',
			'Connection',
			#'OpenRelay',
			'UserScanning',
			#'StandardAddresses',
			'HostnameGreeting',
			'LowPort',
			'StartTLS',
			'VerifyCert',
			'SPF',
			]

		self.availableSlowPlugins = [
#			'DummySlow',
			]

		self.fast_plugins = self.availableFastPlugins[:]
		self.slow_plugins = self.availableSlowPlugins[:]

		# Disabled by default
		#self.fast_plugins.remove('OpenRelay')

		# Add any plugins specified in extra parameter
		for d in options['delete']:
			if d in self.availableFastPlugins and d in self.fast_plugins:
				self.fast_plugins.remove(d)
			if d in self.availableSlowPlugins and d in self.slow_plugins:
				self.slow_plugins.remove(d)

		for e in options['extra']:
			if e in self.availableFastPlugins and e not in self.fast_plugins:
				self.fast_plugins.append(e)
			if e in self.availableSlowPlugins and e not in self.slow_plugins:
				self.slow_plugins.append(e)

		try:
			self.db = Database()
			self.db.connect()
		except DatabaseConnectionFailedException, ee:
			self.logger.error("Failed to connect to database: " % str(ee))
			self.shutdown()
		except Exception, ee:
			self.logger.error("Unknown error: %s (%s)" % (str(ee), traceback_as_str()))
			self.shutdown()

		# TODO: shouldnt really be done this way
		self.pluginConfig = PluginConfig(self.db)
		self.pluginResult = PluginResult(self.db, self.logger)
		self.livefeedback = LiveFeedback(self.db, self.logger)
		self.pluginSockets = PluginSockets(self.logger)

	def _execute_plugin(self, testId, domain, email, plugin):
		"""Run a single plugin and save the result"""
		pluginName = plugin.__class__.__name__
		self.logger.info("#%i: Running %s subtest \"%s\"" % (testId, pluginName,
															domain))
		result = None

		# Setup logger
		plugin.setLogger(self.logger)

		# Set standard input to all plugins
		plugin.setInput('domain', domain)
		plugin.setInput('email', email)
		plugin.setInput('testId', testId)

		# Create a Result that the plugin should use
		plugin.setResult(Result(plugin))

		started = ended = None
		try:
			started = datetime.datetime.now()
			plugin.run()
			ended = datetime.datetime.now()

			# Get plugin result
			result = plugin.getResult()
			result.setStartTime(started)
			result.setEndTime(ended)

		except Exception, e:
			ended = datetime.datetime.now()
			self.logger.error("Failed to run plugin \"%s\": %s (%s)" % (pluginName,
																	str(e), traceback_as_str()))

		# Get information status and gold stars
		if result is not None:
			self.testGoldCount += result.getGoldStarCount()
			status = result.getFinalStatus()

			if status is None:
				raise PluginException('Final status is missing')

			if status > self.testStatus and status != 4:
				self.testStatus = status
		else:
			raise PluginException("Invalid result from plugin %s during test %s" \
									% (pluginName, str(testId)))

		try:
			result.save(self.db, testId)
		except ResultException, ee:
			raise PluginException('Failed to save test result for test "%s".' \
					'Reason: %s (%s)' % (pluginName, str(ee), traceback_as_str()))

		except Exception, e:
			self.logger.error('Unknown exception occured when saving "%s" results. ' \
					'Reason: %s (%s)' % (pluginName, str(e), traceback_as_str()))

		output = result.getOutput()
		if output is not None:
			self.results[plugin.__class__.__name__] = output

	def run(self, testId):
		"""
		Run all plugins invloved in the test.
		@param testId:		ID of the test
		"""
		self.running = True
		sys.path.append(sys.path[0] + '/plugins/')

		test = self._get_test(testId)
		domain = test[0]
		email = test[1]
		slow = test[2]
		isChild = int(self.db.fetch("SELECT DISTINCT COUNT(parent) FROM test WHERE "\
									"id = %s", [testId])[0][0])

		if test == False or domain == '' or domain == None:
			self.logger.error('Trying to start invalid test with ID "%i"' % testId)
			self.shutdown(1)
			return

		self.logger.info("#%i: Starting test against \"%s\"" % (testId, domain))

		if slow:
			self.pluginTotal = len(self.fast_plugins) + len(self.slow_plugins)
		else:
			self.pluginTotal = len(self.fast_plugins)

		# Run all fast tests
		self.run_plugins(testId, domain, email, self.fast_plugins, isChild)

		try:
			self.db.query("UPDATE test SET fast_finished = now(), status = 20 WHERE" \
						" id = %s", [str(testId)])
		except DatabaseException, e:
			self.logger.error('Could not update test %s as ended: %s' % (str(testId),
																		e))

		# Run slow tests, if we should
		if slow:
			self.run_plugins(testId, domain, email, self.slow_plugins, isChild)

		try:
			self.db.query("UPDATE test SET finished = now(), status = %s WHERE" \
					" id = %s", [str(self.testStatus), str(testId)])
		except DatabaseException, e:
			self.logger.error('Could not update test %s as ended: %s', (str(testId), e))

		# Send we're done email for slow tests
		if slow and (isChild == 0):
			self.send_finished_email(testId)

		self.logger.info("#%i: Finished test against \"%s\"" % (testId, domain))

	def send_finished_email(self, testId):
		"""
		Send email when the test is finished
		@param testId:	ID of the test
		@TODO:			Move away from here
		"""

		result = self.db.fetch("SELECT domain, email, slow, started, finished," \
				"extract(epoch from queued)::integer as timeid FROM test WHERE id = %s " \
				"LIMIT 1", [str(testId)])
		if not result:
			return False
		result = result[0]

		config = Config(logger=self.logger)

		gs = ''
		if self.testGoldCount > 0:
			gs = 'Gold stars: %s' % str(self.testGoldCount)

		statuses = {0: 'Unknown', 1: 'OK', 2: 'Warning', 3: 'Error'}
		email = result[1]
		if config.getboolean('general', 'debug'):
			email = config.get('general', 'debug_problem_email')
		body = """\
Hello,

Your test of "%s" finished with status: %s

%s
Started: %s
Finished: %s

Click here to view the test results:

http://mailcheck.iis.se/result/%s-%s
""" % (result[0], statuses[self.testStatus], gs, result[3][:19], \
		result[4][:19], result[5], str(testId))
		message = """\
From: %s
To: %s
Subject: %s

%s
""" % ('mailcheck@' + getfqdn(), email, "MailCheck test finished", body)
		SENDMAIL = "/usr/sbin/sendmail"
		p = os.popen("%s -t -i" % SENDMAIL, "w")
		p.write(message)
		p.close()

	def run_plugins(self, testId, domain, email, plugin_list, isChild):
		"""
		Run a specific list of plugins
		@param testId:			ID of the test
		@param domain:			Domain being tested
		@param email:			Email that started the test
		@param plugin_list:		List with plugins that should be run
		@param isChild:
		"""
		for plugin in plugin_list:
			self.pluginNumber += 1

			# Create plugin
			mod = __import__(plugin, None, None, [plugin])
			p = getattr(mod, plugin)()

			# TODO: this should not really be done this way
			p.pluginConfig = self.pluginConfig
			p.pluginResult = self.pluginResult
			p.livefeedback = self.livefeedback
			p.pluginSockets = self.pluginSockets
			p.isChild = isChild

			# Handle input dependencies
			skipPlugin = False
			if p.hasRequiredInput():
				for inp in p.getRequiredInput():
					if inp in self.results:
						if self.results[inp]:
							p.setInput(inp, self.results[inp])
					else:
						self.logger.info('#%i: Dependency condition "%s" for plugin "%s"' \
								' not met..skipping plugin' % (testId, inp, plugin))
						skipPlugin = True
						break

			if skipPlugin:
				continue

			pluginName = p.__class__.__name__
			self.livefeedback.message(testId, '%s, %s of %s',
					(pluginName, self.pluginNumber, self.pluginTotal))

			# Execute plugin
			try:
				self._execute_plugin(testId, domain, email, p)
			except PluginException, ee:
				self.logger.error("#%i: Subtest \"%s\" failed. Reason: %s (%s)" %
						(testId, plugin, str(ee), traceback_as_str()))
			except Exception, e:
				self.logger.error('Unknown exception: %s (%s)' % (str(e),
																traceback_as_str()))

		self.pluginSockets.close_all()

		return True

	def shutdown(self, exitCode=0):
		"""
		Shutdown the running test
		@param exitCode:	Exit code. Defaults to 0
		"""
		self.running = False
		sys.exit(exitCode)

	def _get_test(self, testId):
		result = self.db.fetch("SELECT domain, email, slow FROM test WHERE" \
				" id = %s LIMIT 1", [str(testId)])
		if len(result) == 1:
			return result[0]
		return False


def usage():
	print "Usage: %s -t testId [-h|--help] [-v verbosity] [-e string]" % \
	sys.argv[0]
	print ""
	print "        -h, --help      Show this text"
	print "        -v verbosity    Set verbosity level"
	print "        -t test id      Start test with id x"
	print "        -e string       Extra parameters"
	print ""


def main(argv):
	verbosity = ""
	testId = 0
	extra = []
	delete = []

	try:
		opts, args = getopt.getopt(argv[1:], "hv:t:e:d:", ["help"])
		for o, a in opts:
			if o in ('-h', '--help'):
				usage()
				sys.exit()
			elif o == '-v':
				verbosity = log_level_parser(a)
			elif o == '-t':
				testId = int(a)
			elif o == '-e':
				extra = a.split(';')
			elif o == '-d':
				delete = a.split(';')

	except getopt.GetoptError:
		usage()
		sys.exit()

	if testId == 0:
		usage()
		sys.exit()

	options = {'extra': extra, 'delete': delete}

	logger = create_logger('mailcheck.testrunner', verbosity)

	t = TestRunner(logger, options)
	t.run(testId)
	logger.info('Exiting test #%i exiting test runner' % testId)

if __name__ == "__main__":
	sys.exit(main(sys.argv))
