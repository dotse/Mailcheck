
import socket
import time as tt

from engine.plugins.Plugin import Plugin
from engine.plugins.common import connect_to_host


class Connection(Plugin):
	"""
	Checks if connection can be established and connection time
	"""

	def __init__(self):
		Plugin.__init__(self)
		self.requiredInput = ['MXRecord']
		self.category = 'SMTP'

	def run(self):
		records = self.getInput('MXRecord')
		port = 25
		# Get settings
		max_connection_time = int(self.pluginConfig.get('connection_warning_length'))

		self.result.info('Starting connection test')

		if len(records['mx_record']) <= 0:
			self.result.error('Test could not be executed')

		results = []
		slowConnections = 0
		failedConnections = 0
		out = {'connection_time': []}
		statusCounts = {Plugin.STATUS_OK: 0, Plugin.STATUS_WARNING: 0, Plugin.STATUS_ERROR: 0}
		for ip in records['mx_record']:
			prio = ip['prio']
			host = ip['host']
			type = ip['connection_type']
			ip = ip['ip']

			code = Plugin.STATUS_OK
			error = ""
			end = None
			try:
				#s.settimeout(20.0)
				#c = s.connect( (ip, 25) )
				#s.close()
				start = end = 0
				try:
					start = tt.time()
					s = connect_to_host(ip, port, type, self)
					end = tt.time()
				except Exception, e:
					self.result.warning('Failed to connect to mail server %s (%s)', (host, ip))
					continue

				ftime = end - start
				time = "%0.6f" % (ftime)

				out['connection_time'].append({'time': time, 'host': host, 'ip': ip})
				s.recv(1024)
			except socket.error, e:
				self.logger.debug('Host: %s (%s), Connection plugin error: %s' \
						% (host, ip, e))

				failedConnections += 1
				code = Plugin.STATUS_WARNING
				if e[0] == 101:
					error = "network unreachable"
				elif e[0] == 111:
					error = "connection refused"
				elif e[0] == 110 or e[0] == 'timed out' or e == 'timed out':
					error = "connection timed out"
				else:
					error = "unable to connect"

			# Add status message
			if error != '':
				self.result.warning('Connection to %s (%s) could not be established', (host, ip))
				code = Plugin.STATUS_WARNING
			elif end != None and ftime >= max_connection_time:
				self.result.warning('Connection time to %s above %s second (%ss)', (host, max_connection_time, time))
				code = Plugin.STATUS_WARNING
				slowConnections += 1
			else:
				self.result.info('Connection test against %s (%s) successful in %ss', (host, ip, time))

			results.append([prio, host, ip, type, time])
			statusCounts[code] += 1

		# Figure the final status of the test
		code = Plugin.STATUS_OK
		if failedConnections == len(results):
			code = Plugin.STATUS_ERROR
			self.result.error('Could not establish connection with any server')
		elif slowConnections == len(results):
			code = Plugin.STATUS_WARNING
			self.result.warning('All connection times are above %s second', max_connection_time)
		elif statusCounts[Plugin.STATUS_WARNING] > 0:
			code = Plugin.STATUS_WARNING

		self.result.extra('more info connection time', type='adv')

		self.result.info('Finished connection test')
		self.result.setTestStatus(code)

		# output
		if code == Plugin.STATUS_ERROR:
			out = None
		self.result.setOutput(out, persist=True)
