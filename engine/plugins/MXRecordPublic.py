
from IPy import IP

from engine.plugins.common import *
from engine.plugins.Plugin import Plugin


class MXRecordPublic(Plugin):
	"""
	Check for MX records with private IPs
	"""

	def __init__(self):
		Plugin.__init__(self)
		self.requiredInput = ['MXRecord']
		self.category = "DNS"

	def run(self):
		records = self.getInput('MXRecord')

		self.result.info('Starting public MX record test')

		testResults = {}
		totalRecords = len(records['mx_record'])
		totalInternal = 0
		highestPriority = 100000
		for record in records['mx_record']:
			prio = int(record['prio'])
			host = record['host']
			type = record['connection_type']

			self.result.info('Checking %s (%s)', (host, record['ip']))

			if prio < highestPriority:
				highestPriority = prio

			externalIP = True
			try:
				ip = IP(record['ip'])

				private = False
				if type == 'INET':
					if ip.iptype() == 'PRIVATE':
						private = True
				else:
					# IPv6 private ips
					privateIps = IP('fc00::/7')
					if ip in privateIps:
						private = True

				if private == True:
					externalIP = False
					totalInternal += 1
					self.result.warning('%s is a private IP', record['ip'])
				else:
					self.result.info('%s is a public IP address', record['ip'])
			except Exception, e:
				pass

			if prio in testResults:
				testResults[prio].append(externalIP)
			else:
				testResults[prio] = [externalIP]


		# Time to figure out the final status
		message = ''
		code = Plugin.STATUS_OK
		# All internal == ERROR
		if totalInternal == totalRecords:
			code = Plugin.STATUS_ERROR
			self.result.error('All IP addresses are private')
		# Just a few internal == WARNING
		elif totalInternal > 0 and totalInternal < totalRecords:
			if totalInternal == 1:
				message = "%s IP address is private"
			else:
				message = "%s IP addresses are private"
			code = Plugin.STATUS_WARNING
			self.result.warning(message, str(totalInternal))
		# Highest priority record internal == ERROR
		if highestPriority > 0 and highestPriority in testResults:
			for t in testResults[highestPriority]:
				if t == False:
					code = Plugin.STATUS_ERROR
					self.result.error("Primary MX record is private")
					break

		self.result.extra('more info public mx record', type='adv')
		self.result.info('Finished public MX record test')
		self.result.setTestStatus(code)
