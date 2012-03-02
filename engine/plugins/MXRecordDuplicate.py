
from engine.plugins.Plugin import Plugin


class MXRecordDuplicate(Plugin):
	"""
	Check for duplicate IPs for MX records for duplicate IPs
	"""

	def __init__(self):
		Plugin.__init__(self)
		self.requiredInput = ['MXRecord']
		self.category = 'DNS'

	def run(self):
		records = self.getInput('MXRecord')

		self.result.info('Starting duplicate IP for MX record test')
		duplicateIps = {}
		for row in records['mx_record']:
			host = row['host']
			ip = row['ip']
			count = 0

			for row in records['mx_record']:
				if row['ip'] == ip:
					count += 1

			if count > 1:
				if ip in duplicateIps:
					duplicateIps[ip].append((host, count))
				else:
					duplicateIps[ip] = [(host, count)]

		# Remove original record
		for ip in duplicateIps:
			if len(duplicateIps[ip]) > 1:
				duplicateIps[ip].pop(0)

		for ip in duplicateIps:
			for h in duplicateIps[ip]:
				self.result.warning('Duplicate IP for MX record %s (%s) found', (h[0], ip))
		if len(duplicateIps) == 0:
			self.result.info('No duplicate IP for MX records found')

		self.result.extra('more info duplicate mx record', type='adv')

		self.result.info('Finished duplicate IP for MX record test')

		# Results
		code = Plugin.STATUS_OK
		if len(duplicateIps) > 0:
			code = Plugin.STATUS_WARNING

		self.result.setTestStatus(code)
