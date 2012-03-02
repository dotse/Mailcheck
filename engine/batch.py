
import os
import sys
import csv
import time
import json
import getopt
import datetime
import threading


from engine.log import create_logger, log_level_parser
from engine.util import traceback_as_str
from engine.database import Database, DatabaseConnectionFailedException
from engine.plugins.Plugin import (Plugin,
                                    PluginConfig,
                                    PluginResult,
                                    LiveFeedback,
                                    PluginSockets,
                                    Result,
                                    )


def plugin_status_to_text(status):
    if status == Plugin.STATUS_OK:
        return 'ok'
    elif status == Plugin.STATUS_WARNING:
        return 'warning'
    elif status == Plugin.STATUS_ERROR:
        return 'error'
    elif status == Plugin.STATUS_UNKNOWN:
        return 'unknown'


class BatchRunner(object):
    def __init__(self, processes=None):
        # Number of concurrent tests we run
        self.total_processes = processes or 5

        self.running_tests = []

    def start(self):
        pass


class TestRunner(object):
    def __init__(self, filename, output, concurrent_tests, post_test_sleep, logger):
        self.db = None
        self.output = output
        self.logger = logger
        self.results = {}

        self.concurrent_tests = concurrent_tests or 5

        # Sleep after a test to slow down testing a bit
        self.post_test_sleep = post_test_sleep or 0

        try:
            c = CSV(filename)
            self.domains = c.get_data()
        except CSV, e:
            self.logger.error("Failed to get domains from CSV file: %s" % e)
            raise Exception("Failed to get domains from CSV file: " % e)

        if len(self.domains) == 0:
            raise Exception('Need at least one email address to test')

        self.summary = {
            'start_time': datetime.datetime.utcnow().isoformat(),
            'end_time': 0,

            'gold_star_count': 0,
            'gold_stars': {},

            'status': {
                plugin_status_to_text(Plugin.STATUS_OK): 0,
                plugin_status_to_text(Plugin.STATUS_WARNING): 0,
                plugin_status_to_text(Plugin.STATUS_ERROR): 0,
                plugin_status_to_text(Plugin.STATUS_UNKNOWN): 0,
             },

            'subtests': {
                'status': {
                    plugin_status_to_text(Plugin.STATUS_OK): 0,
                    plugin_status_to_text(Plugin.STATUS_WARNING): 0,
                    plugin_status_to_text(Plugin.STATUS_ERROR): 0,
                    plugin_status_to_text(Plugin.STATUS_UNKNOWN): 0,
                 },
            }
        }

        self.default_fast_plugins = [
            'MXRecord',
            'MXRecordPublic',
            'MXRecordDuplicate',
            'MXRecordCNAME',
            'MXRecordDiffering',
            'MXRecordPTR',
            'Blacklist',
            'Connection',
            'UserScanning',
            'HostnameGreeting',
            'LowPort',
            'StartTLS',
            'SPF',
        ]
        self.plugin_list = self.default_fast_plugins

        self.__init_db()

        self.pluginConfig = PluginConfig(self.db)
        self.pluginResult = PluginResult(self.db, self.logger)
        # None disabled persistance of the messages
        self.livefeedback = LiveFeedback(None, self.logger)
        self.pluginSockets = PluginSockets(self.logger)

    def start(self):
        sys.path.append(sys.path[0] + '/plugins/')

        self.logger.info('Starting batch run of %s domains, running %s concurrently' \
                        % (len(self.domains), self.concurrent_tests))

        summaryLock = threading.Lock()
        runningTests = []
        while True:
            if len(self.domains) == 0:
                # Wait for all running tests to finish before we exit
                running_status = [x.isAlive() for x in runningTests]
                if True not in running_status:
                    break
                else:
                    # Sleep and lets try again
                    time.sleep(1)
                    continue

            # Check if we can start tests
            free_spaces = self.concurrent_tests - len(runningTests)
            if free_spaces > 0:
                email, domain = self.domains.pop()
                t = threading.Thread(target=self.run, args=(domain, email,
                    summaryLock))
                t.start()
                runningTests.append(t)

            tmp = [x for x in runningTests if x.isAlive()]
            runningTests = tmp

            time.sleep(1)

        # end of test
        self.summary['end_time'] = datetime.datetime.utcnow().isoformat()

        j = None
        try:
            j = json.dumps(self.summary)
        except Exception, e:
            self.logger.error('Failed to create JSON: %s' % e)
            print "Failed to create JSON output."
            sys.exit(1)

        if self.output is not None:
            try:
                with open(self.output, 'w') as h:
                    h.write(j)
            except:
                print "Failed to write result to file."
                print j
                sys.exit(1)
        else:
            print j

    # @threaded
    def run(self, domain, email, lock):
        testStatus = 0

        pluginConfig = PluginConfig(self.db)
        pluginResult = PluginResult(self.db, self.logger)
        # None disabled persistance of the messages
        livefeedback = LiveFeedback(None, self.logger)
        pluginSockets = PluginSockets(self.logger)

        self.logger.info('Stating test of "%s"' % domain)
        for plugin in self.plugin_list:
            # Create plugin
            mod = __import__(plugin, None, None, [plugin])
            p = getattr(mod, plugin)()
            pluginName = p.__class__.__name__

            p.pluginConfig = pluginConfig
            p.pluginResult = pluginResult
            p.livefeedback = livefeedback
            p.pluginSockets = pluginSockets
            p.isChild = 0

            # Handle input dependencies
            skipPlugin = False
            if p.hasRequiredInput():
                for inp in p.getRequiredInput():
                    if inp in self.results:
                        if self.results[inp]:
                            p.setInput(inp, self.results[inp])
                    else:
                        self.logger.info('"%s": Dependency condition "%s" ' \
                                'for plugin "%s" not met..skipping plugin'
                                % (domain, inp, plugin))
                        skipPlugin = True
                        break

            if skipPlugin:
                continue

            result = self._execute_plugin(domain, email, p, lock)

            if result is not None:
                status = result.getFinalStatus()
                if status > testStatus and status != Plugin.STATUS_UNKNOWN:
                    testStatus = status

                with lock:
                    if status is not None:
                        gold = [x['message'] for x in result.getRawMessages() if x['gold'] == 1]
                        for x in gold:
                            if x not in self.summary['gold_stars']:
                                self.summary['gold_stars'][x] = 0
                            self.summary['gold_stars'][x] += 1

                        self.summary['gold_star_count'] += result.getGoldStarCount()
                        self.summary['subtests']['status'] \
                                [plugin_status_to_text(status)] += 1

                    output = result.getOutput()
                    if output is not None:
                        self.results[pluginName] = output

        # Save final test status
        with lock:
            self.summary['status'][plugin_status_to_text(testStatus)] += 1

        pluginSockets.close_all()

        self.logger.info('Finished test of "%s"' % domain)
        if self.post_test_sleep > 0:
            time.sleep(self.post_test_sleep)

    def _execute_plugin(self, domain, email, plugin, lock):
        pluginName = plugin.__class__.__name__
        self.logger.info("\"%s\": Running subtest %s" % (domain, pluginName))

        plugin.setLogger(self.logger)

        # Set standard input to all plugins
        plugin.setInput('domain', domain)
        plugin.setInput('email', email)
        plugin.setInput('testId', 0)

        plugin.setResult(Result(plugin))

        result = None
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
            self.logger.error("\"%s\": Failed to run plugin %s: %s (%s)" \
                    % (domain, pluginName, str(e), traceback_as_str()))

        return result

    def __init_db(self):
        try:
            self.db = Database()
            self.db.connect()
        except DatabaseConnectionFailedException, ee:
            self.logger.error("Failed to connect to database: " % str(ee))
            self.shutdown()
        except Exception, ee:
            self.logger.error("Unknown error: %s (%s)" % \
                    (str(ee), traceback_as_str()))
            self.shutdown()


class CSVException(Exception):
    pass


class CSV(object):
    def __init__(self, filename, delimiter=','):
        self.filename = filename
        self.data = []

        try:
            reader = csv.reader(open(filename, 'rb'), delimiter=delimiter)
            for row in reader:
                if len(row) >= 1:
                    try:
                        name, domain = row[0].split('@')
                        self.data.append((row[0], domain))
                    except ValueError:
                        pass
        except CSV.Error, e:
            raise CSVException(e)

    def get_data(self):
        return self.data


def usage():
    print """Usage %s [options] filename

      -h, --help     Show this text
      -v <verbosity> Set verbosity (info, warning, debug)
      -o <file>      File result JSON should be outputted to.
        Defaults to stdout if not specified.
      --post-test-sleep  Extra wait time afte a test has finished. Defaults 0.

""" % sys.argv[0]


def main():
    output = None
    filename = None
    verbosity = "info"
    concurrent_tests = None
    post_test_sleep = None

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hv:o:n:", ["help",
            "post-test-sleep="])
        for o, a in opts:
            if o in ('-h', '--help'):
                usage()
                sys.exit()
            elif o == '-v':
                verbosity = log_level_parser(a)
            elif o == '-o':
                output = a
            elif o == '-n':
                concurrent_tests = int(a)
            elif o == '--post-test-sleep':
                post_test_sleep = int(a)

    except getopt.GetoptError:
        usage()
        sys.exit(1)

    if len(args) <= 0 or os.path.exists(args[0]) is False:
        print "Missing CSV file!"
        usage()
        sys.exit(1)
    else:
        filename = args[0]

    logger = create_logger('mailcheck.batch', verbosity)
    try:
        t = TestRunner(filename, output, concurrent_tests, post_test_sleep, logger)
        t.start()
    except Exception, e:
        print e
        sys.exit(1)


if __name__ == "__main__":
    main()

