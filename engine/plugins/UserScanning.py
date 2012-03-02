import random
import socket
import re
import string

from engine.plugins.common import connect_to_host
from engine.plugins.Plugin import Plugin


class UserScanning(Plugin):
	"""
	Checks mailserver responds for VRFY commands, tries with a known user and a unknown user
	"""

	def __init__(self):
		Plugin.__init__(self)
		self.requiredInput = ['MXRecord']
		self.category = 'SMTP'

	def run(self):
		domain = self.getInput('domain')
		email = self.getInput('email')
		records = self.getInput('MXRecord')
		port = 25

		self.result.info('Started user scanning test')

		testResult = []
		for row in records['mx_record']:
			host = row['host']
			ip = row['ip']
			type = row['connection_type']

			try:
				s = connect_to_host(ip, port, type, self)
			except Exception:
				self.result.warning('Failed to connect to mail server %s (%s)', (host, ip))
				testResult.append(True)
				continue

			# Random email used in test
			rnd = ''
			rnd = ''.join(random.sample(string.ascii_lowercase + string.digits, 12))
			rnd += '@' + domain

			fqdn = socket.getfqdn()
			conversation = [
				[
					'HELO %s\r\n' % fqdn,
					'VRFY %s\r\n' % email,
					'VRFY %s\r\n' % rnd
				],
				[
					'250.*',
					'25[0-2].*',
					'25[1-2].*|55[0,4].*',
				],
				[
					'252.*'
				]
			]

			# Scan for users
			testlog = ''
			error = False
			counter252 = 0
			for i in range(len(conversation[0])):
				send = conversation[0][i]
				recv = conversation[1][i]

				testlog = ''
				if i == 0:
					data = s.recv(1024)
					testlog += "<<< %s" % data

					if not re.search('220.*', data):
						self.result.info('%s', testlog)
						self.result.warning("No standard greeting on %s (%s)", (host, ip))
						testResult.append(True)
						continue

				s.send(send)
				testlog += ">>> %s" % send

				data = ''
				try:
					data = s.recv(1024)
				except socket.timeout:
					self.result.warning('Connection timed out')
					error = True
					break

				testlog += "<<< %s" % data
				self.result.info('%s', testlog)

				if not re.search(recv, data):
					error = True
					break

				if re.search(conversation[2][0], data):
					counter252 += 1

			testResult.append(error)

			if counter252 == 2:
				self.result.goldstar("%s (%s) answering \"252\" which is good for avoiding spam, see http://cr.yp.to/smtp/vrfy.html for more information.", (host, ip))

			if error:
				self.result.warning("User scanning %s (%s) failed\n%s", (host,ip,testlog))
			else:
				self.result.info('User scanning %s (%s) completed', (host,ip))


		self.result.extra('more info user scanning', type='adv')

		self.result.info('Finished user scanning test')

		code = Plugin.STATUS_OK
		if True in testResult:
			code = Plugin.STATUS_WARNING

		self.result.setTestStatus(code)
