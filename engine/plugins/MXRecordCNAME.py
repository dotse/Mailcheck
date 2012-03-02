import dns.resolver

from engine import log
from engine.plugins.Plugin import Plugin, Result


class MXRecordCNAME(Plugin):
	"""
	Check if any of the MX-records obtained by the MXRecords plugin is a CNAME
	"""

	def __init__(self):
		Plugin.__init__(self)
		self.requiredInput = ['MXRecord']
		self.category = 'DNS'

	def run(self):
		domain = self.getInput('domain')
		records = self.getInput('MXRecord')

		self.result.info('Starting CNAME test')
		testResult = []
		for r in records['mx_record']:
			host = r['host']
			ip = r['ip']

			cname = ''
			try:
				cname = dns.resolver.query(host, 'cname')
				cname = cname.rrset[0]
				cname = cname.to_text()[0:-1]
			except:
				pass

			if cname != '':
				testResult.append(Plugin.STATUS_WARNING)
				self.result.warning('%s (%s) is a CNAME', (host, ip))
			else:
				self.result.info('%s (%s) is not a CNAME', (host, ip))

		code = Plugin.STATUS_OK
		if len(testResult) > 0:
			code = Plugin.STATUS_WARNING

		self.result.extra('more info cname mx record', type='adv')

		self.result.info('Finished CNAME test')
		self.result.setTestStatus(code)
