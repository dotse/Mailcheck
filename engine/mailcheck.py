import sys
import time
import getopt
from subprocess import Popen
from re import sub

from engine.log import create_logger, log_level_parser
from engine.config import Config
from engine.database import (Database,
							DatabaseException,
							DatabaseConnectionFailedException)
from engine.plugins.Plugin import LiveFeedback
from engine.util import traceback_as_str


class TestEngine(object):
	"""Handles running and saving of tests"""

	def __init__(self, logger, verbosity):
		self.running = False
		self.verbosity = verbosity
		self.logger = logger

		self.config = Config(logger=self.logger)

		self.logger.info('Starting engine...')

		try:
			self.db = Database()
			self.db.connect()
		except DatabaseConnectionFailedException, e:
			self.logger.error('Could not establish connection with the database (%s).' \
					'Shutting down...' % e)
			self.shutdown(1)
			return

		self.debug = self.config.getboolean('general', 'debug')
		self.livefeedback = LiveFeedback(self.db)
		self.runningTests = []

	def run(self):
		"""Run the test engine"""
		self.running = True

		self.logger.info('Engine started')
		interval = self.config.getint('testengine', 'queue_check_interval')
		webmail_interval_default = webmail_interval = self.config.getint(
													'testengine', 'webmail_check_interval')
		cleanup_interval = self.config.getint('testengine', 'cleanup_interval')

		concurrent_fast_tests = self.config.getint('testengine',
													'concurrent_fast_tests')
		concurrent_slow_tests = self.config.getint('testengine',
													'concurrent_slow_tests')
		last_cleanup = time.time()

		self.logger.info('Checking queue every %s seconds' % interval)
		while self.running:
			try:
				time.sleep(interval)
				webmail_interval = webmail_interval - interval
			except KeyboardInterrupt:
				print "Bye!"
				break

			# Update the list of running tests
			for t in self.runningTests:
				if t[1].poll() != None:
					self.runningTests.remove(t)
					tid = t[0]
					try:
						result = self.db.fetch('SELECT finished, fast_finished FROM test WHERE' \
							' id = %s LIMIT 1', [str(tid)])
						if result:
							if result[0][0] is None and result[0][1] is None:
								self.db.query("UPDATE test SET finished = now()," \
									" fast_finished = now(), status = 3 WHERE id = %s", [str(tid)])
					except Exception, e:
						self.logger.error('Could not update test %s as ended: %s' % (str(tid),
																						e))

			# Cleanup any old queued tests what are still waiting for user input
			if (time.time() - last_cleanup) >= cleanup_interval:
				try:
					last_cleanup = time.time()
					self.db.query("DELETE FROM queue WHERE waiting_input = 't' AND " \
						"start_time < now() - interval '12 hours'", [])
				except DatabaseException:
					self.logger.error('Failed to clear old queued test waiting for'
						'user input')

			if (webmail_interval <= 0) and self.debug is False:
				Popen(['/usr/bin/python', '/var/www/mailcheck/engine/imap.py'])
				Popen(['/usr/bin/python', '/var/www/mailcheck/engine/pop.py'])
				webmail_interval = webmail_interval_default

			# Check how many fast tests are running
			fastRunningCount = 0
			slowRunningCount = 0
			try:
				result = self.db.fetch("SELECT id, fast_finished, finished FROM test " \
						"WHERE fast_finished IS NULL OR finished IS NULL", [])
				for r in result:
					if r[1] is None:
						fastRunningCount += 1
					if r[1] is not None and r[2] is None:
						slowRunningCount += 1
				self.logger.debug("Fast: %i, Slow: %i" % (fastRunningCount,
															slowRunningCount))
			except Exception, e:
				self.logger.error('Failed to count running tests: %s (%s)' % (str(e),
																			traceback_as_str()))

			# Check if we are allowed to start any more tests at this moment
			if fastRunningCount >= concurrent_fast_tests or \
				slowRunningCount >= concurrent_slow_tests:
				continue

			# Get queued tests if we have any open spots
			queuedTest = self._get_queued_tests(
					concurrent_fast_tests - fastRunningCount)
			if queuedTest == None or len(queuedTest) == 0:
				continue

			for queued in queuedTest:
				# Start test
				domain = queued[0]
				queueId = queued[1]
				testId = queued[2]
				email = queued[3]
				ip = queued[4]
				extra = queued[5]
				start_time = queued[6]
				slow = queued[7]
				parent = queued[8]

				# Check if the test is already running
				for test in self.runningTests:
					if test[0] == testId:
						self.logger.info("Test with ID %i is already running" % testId)
						continue

				# Move test from queue
				try:
					self.db.begin()
					self.db.query_transaction("INSERT INTO test (id, domain, email," \
							"started, ip, queued, slow, parent) VALUES(%s, %s, %s, now(), %s, %s," \
							"%s, %s)", [str(testId), domain, email, ip, start_time, slow, parent])
					self.db.query_transaction("DELETE FROM queue WHERE id = %s", [queueId])
					self.db.commit()
				except DatabaseException:
					self.logger.error('Failed to move test #%s from queue' % str(testId))
				except Exception, e:
					self.logger.error('Unknown error occured: %s (%s)' % (e,
																		traceback_as_str()))

				self.livefeedback.message(testId, 'Starting test against %s', (domain))
				self.startTest(testId, extra)

		self.db.close()

	def startTest(self, testId, extra=''):
		"""Start a new test runner process that executes the test"""
		options = ["-v", str(self.verbosity), "-t", str(testId)]

		if extra != '':
			extra = sub('^', '-', extra)
			extra = sub(',', ' -', extra)
			extra = sub(':', ' ', extra)
			extra = extra.split(' ')
			for e in extra:
				options.append(e)

		try:
			testRunner = sys.path[0] + '/testrunner.py'
			tr = Popen(['/usr/bin/python', testRunner] + options)
			self.logger.info('Starting test #%s with %s %s' % (str(testId), testRunner,
																options))
			self.runningTests.append((testId, tr))
		except Exception, ee:
			self.logger.error('Failed to start test #%s. Reason: %s' % (str(testId),
																			ee))

	def shutdown(self, exitCode):
		"""Shutdown"""
		self.running = False
		sys.exit(exitCode)

	def _queue_test(self, domain):
		"""Insert a test into the queue. This should only be
		used when you don't want to starts tests with the web interface."""
		try:
			self.db.query('INSERT INTO queue (domain, email, test_id, waiting_input,' \
					'slow) VALUES(%s, %s, nextval(\'test_id_seq\'), false, false)',\
					[domain, 'mailcheck@' + domain])
		except:
			self.logger.error('Failed to queue test against domain "%s"' % domain)

	def _get_queued_tests(self, limit):
		"""Get a list with tests that are queued"""
		try:
			queuedTest = self.db.fetch("SELECT domain,id,test_id,email,ip,extra, "
					"start_time,slow,parent FROM queue WHERE waiting_input != 't' "
					"AND now() >= start_time LIMIT %i" % limit)
			return queuedTest
		except DatabaseException, e:
			self.logger.error("Exception while checking the queue: " + str(e))
		return None


def usage(argv):
	print "Usage: " + argv[0] + " [-h|--help] [-v verbosity] [-q domain]"
	print ""
	print "       -h, --help       Show this text"
	print "       -v [verbosity]   Set verbosity level"
	print "       -q [domain]      Queue a test before starting test engine"
	print ""


def main(argv):
	verbosity = ""
	try:
		opts, args = getopt.getopt(argv[1:], "hv:t:q:", ["help"])
	except getopt.GetoptError:
		usage(argv[1:])
		sys.exit()

	queueTest = False
	for o, a in opts:
		if o in ('-h', '--help'):
			usage(argv[1:])
			sys.exit()
		elif o == "-v":
			verbosity = log_level_parser(a)
		elif o == '-q':
			queueTest = a

	logger = create_logger('mailcheck.engine', verbosity)
	te = TestEngine(logger, verbosity)

	if queueTest != False:
		te._queue_test(queueTest)

	te.run()


if __name__ == "__main__":
	sys.exit(main(sys.argv))
