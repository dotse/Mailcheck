import random
import socket
import re
import string

from engine.plugins.common import connect_to_host
from engine.plugins.Plugin import Plugin, Result

class UserScanning(Plugin):
	"""
	Checks mailserver responds for VRFY commands, tries with a known user and a unknown user
	"""
	
	def __init__(self):
		Plugin.__init__(self)
		# Sets the required input for this plugin to be the output from the MXRecord-plugin. So, for this plugin
		# to execute at least one MX or A record must have been found.
		self.requiredInput = ['MXRecord']

		# Set the category this test belongs to
		self.category = 'SMTP'

	def run(self):
		port = 25

		# Get default input that all plugins receive (domain, name and testId)
		domain = self.getInput('domain')
		email = self.getInput('email')

		# Get the output from the MXRecord-plugin	
		records = self.getInput('MXRecord')

		self.result.info('Started user scanning test')

		testResult = []
		for row in records['mx_record']:
			host = row['host']
			ip = row['ip']
			type = row['connection_type']

			try:
				s = connect_to_host(ip, port, type, self)
			except Exception, e:
				self.result.warning('Failed to connect to mail server %s (%s)', (host, ip))
				testResult.append(True)
				continue

			# Create a random email used in the test
			rnd = ''
			rnd = ''.join(random.sample(string.ascii_lowercase + string.digits, 12))
			rnd += '@' + domain
			
			fqdn = socket.getfqdn()
			# Conversation with email server divided in three parts: [ What to send ], [ what answers to excpect ], [ what answers is classed as errors ].
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

			# Run conversation
			testlog = ''
			error = False
			counter252 = 0
			for i in range(len(conversation[0])):
				send = conversation[0][i]
				recv = conversation[1][i]
			
				testlog = ''
				# Is this the first iteraction with the server?
				if i == 0:
					data = s.recv(1024)
					testlog += "<<< %s" % data
					
					# Make sure we get a 220 greeting message	
					if not re.search('220.*', data):
						self.result.info('%s', testlog)
						self.result.warning("No standard greeting on %s (%s)", (host,ip))
						testResult.append(True)
						continue
				
				# Send data to the server
				s.send(send)
				testlog += ">>> %s" % send

				# Get the answer from the server
				data = s.recv(1024)
				testlog += "<<< %s" % data
				self.result.info('%s', testlog)

				# if the reply isn't expected proceed with next server
				if not re.search(recv, data):
					error = True
					break

				# Set count number of 252 entries for server
				if re.search(conversation[2][0], data):
					counter252 += 1

			testResult.append(error)

			# if the server responds 252 on both set a goldstar
			if counter252 == 2:
				# Add a gold star to the test with a message explaining the reason behind it
				self.result.goldstar("%s (%s) answering \"252\" which is good for avoiding spam, see http://cr.yp.to/smtp/vrfy.html for more information.", (host, ip))

			if error:
				self.result.warning("User scanning %s (%s) failed\n%s", (host,ip,testlog))
			else:
				self.result.info('User scanning %s (%s) completed', (host,ip))


		self.result.info('Finished user scanning test')
	
		# Figure out the final status of this plugin	
		code = Plugin.STATUS_OK
		if True in testResult:
			code = Plugin.STATUS_WARNING
		self.result.setTestStatus(code)
