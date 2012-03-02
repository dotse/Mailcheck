
import os
import sys
import getpass
import ConfigParser
from os.path import dirname


class Config(ConfigParser.ConfigParser):
	__shared_state = {}

	def __init__(self, file=None, logger=None):
		self.__dict__ = self.__shared_state
		if len(self.__shared_state) > 0:
			return

		self.logger = logger

		ConfigParser.ConfigParser.__init__(self)

		path = dirname(sys.path[0]) + '/config'
		stdFile = path + '/config.ini'

		if file is not None:
			stdFile = file

		if self.logger:
			self.logger.debug('Loading standard config file "config.ini"')

		self.read(stdFile)

		# Load user specific config file, if it exists
		user = getpass.getuser()
		userFile = "%s/%s.config.ini" % (path, user)
		if os.path.exists(userFile):
			self.read(userFile)
			if self.logger:
				self.logger.debug('Loading user config file "%s.config.ini"' % user)


if __name__ == '__main__':
	c = Config()
	print c.get('general', 'debug')
