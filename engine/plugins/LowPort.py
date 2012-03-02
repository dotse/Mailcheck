
import socket
import random

from engine.plugins.Plugin import Plugin


class LowPort(Plugin):
	"""
	Check if mail servers are able to responde to low port connections
	"""

	def __init__(self):
		Plugin.__init__(self)
		self.requiredInput = ['MXRecord']
		self.category = "SMTP"

	def run(self):
		records = self.getInput('MXRecord')

		self.result.info('Starting low port test')

		testResult = []
		for row in records['mx_record']:
			host = row['host']
			ip = row['ip']
			type = row['connection_type']

			success = False
			again = True
			while again:  # loop until we find a port that isn't used
				port = random.randrange(1, 1023)
				c = self._connect(ip, port, type)
				again = c[0]
				success = c[1]

			testResult.append(success)
			if success:
				self.result.info('Connection against %s (%s) successful from port %s', (host, ip, port))
			else:
				self.result.warning('Connection against %s (%s) failed from port %s', (host,ip, port))

				self.result.extra('more info low port', type='adv')

		self.result.info('Finished low port test')

		# Final result
		code = Plugin.STATUS_OK
		if False in testResult:
			code = Plugin.STATUS_WARNING

		self.result.setTestStatus(code)

	def _connect(self, ip, port, type):
		"""Return: first bool = keep testing conneciton second bool = connection successful"""
		try:
			if type == 'INET6':
				s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
			else:
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.bind(('', port))
			s.settimeout(30)
			s.connect((ip, 25))

			s.close()
		except socket.error, e:
			# 98 = address in use
			if e[0] == 98:
				return (True, False)
			else:
				return (False, False)
		return (False, True)
