
import socket
import re

from engine.plugins.common import get_ipv_type, connect_to_host
from engine.plugins.Plugin import Plugin


class HostnameGreeting(Plugin):
	"""
	Check if greeting message contains a valid hostname
	"""

	def __init__(self):
		Plugin.__init__(self)

		self.requiredInput = ['MXRecord']
		self.category = 'SMTP'

	def run(self):
		port = 25
		records = self.getInput('MXRecord')

		self.result.info('Starting hostname greeting test')
		testResult = []
		for row in records['mx_record']:
			host = row['host']
			ip = row['ip']
			type = row['connection_type']

			try:
				s = connect_to_host(ip, port, type, self)
			except Exception, e:
				self.result.warning('Failed to connect to mail server %s (%s)', (host, ip))
				continue

			try:
				s.send("HELO " + str(socket.getfqdn()) + "\n")
				data = s.recv(1024)

				regex = re.compile(r'^[0-9]*\s(.*?)\s')
				match = regex.match(data)
				if match:
					mailhost = match.group(1)

					ipv = get_ipv_type(mailhost)

					if len(ipv) < 2:
						if ip != ipv[2]:
							self.result.warning("IP of hostname (%s) in greeting message doesn't match mail server IP (%s)", (ip, ipv[2]))
					else:
						self.result.info('Valid hostname (%s) found in greeting message', mailhost)
						testResult.append(True)
				else:
					self.result.warning('Hostname is missing in greeting line:\n%s', data)
			except Exception, e:
				self.result.warning('Failed to resolve hostname (%s) in greeting message on %s', (mailhost, host))

		self.result.extra('more info hostname greeting', type='adv')

		self.result.info('Finished hostname greeting test')

		# Final result
		code = Plugin.STATUS_OK
		if len(testResult) != len(records['mx_record']):
			code = Plugin.STATUS_WARNING

		self.result.setTestStatus(code)
