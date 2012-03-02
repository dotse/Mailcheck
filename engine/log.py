
import sys
import syslog
import logging

LEVELS = {
	'debug': logging.DEBUG,
	'info': logging.INFO,
	'warning': logging.WARNING,
	'error': logging.ERROR,
	'critical': logging.CRITICAL
}

NODATE_FORMAT = ('(%(name)-14s) %(levelname)s: %(message)s ' \
					'(%(filename)s:%(lineno)d)')
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def create_logger(name, level):
	logger = logging.getLogger(name)
	logger.setLevel(LEVELS.get(level, logging.NOTSET))

	sysl = SyslogHandler(syslog.LOG_USER)
	formatter = logging.Formatter(NODATE_FORMAT, DATE_FORMAT)
	sysl.setFormatter(formatter)

	logger.addHandler(sysl)
	return logger


def log_level_parser(level):
	if level not in LEVELS.keys():
		return 'info'
	return level


class SyslogHandler(logging.Handler):
	prios = {
		10: syslog.LOG_DEBUG,
		20: syslog.LOG_INFO,
		30: syslog.LOG_WARNING,
		40: syslog.LOG_ERR,
		50: syslog.LOG_CRIT,
		0: syslog.LOG_NOTICE
	}

	def __init__(self, facility=syslog.LOG_USER):
		self.facility = facility
		logging.Handler.__init__(self)
		syslog.openlog("%s" % (sys.argv[0]), syslog.LOG_PID, self.facility)

	def emit(self, record):
		msg = self.format(record)
		if isinstance(msg, unicode):
			msg = msg.encode('utf-8')
		syslog.syslog(self.facility | self.prios[record.levelno], msg)
