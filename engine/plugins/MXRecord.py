
"""
MXRecord plugin
"""

import adns
from engine.plugins.common import get_ipv_type
from engine.plugins.Plugin import Plugin


class MXRecord(Plugin):
	"""Checks a domain for MX records

	Input: domain
	Output: MX records
	"""

	def __init__(self):
		Plugin.__init__(self)
		self.category = "DNS"

	def run(self):
		domain = self.getInput('domain')

		self.result.info('Starting MX record lookup against %s', (domain))
		dns = adns.init()
		mxRecords = dns.synchronous(domain, adns.rr.MX)
		records = []
		if (len(mxRecords[3]) >= 1):

			for i in mxRecords[3]:
				prio = str(i[0])
				host = i[1][0]
				ipv = get_ipv_type(host)
				if len(ipv) <= 2:
					if self.logger:
						self.logger.debug("Failed to find IPv type for host \"%s\"" % host)
					continue
				if self.logger:
					self.logger.debug("Host: %s, Prio: %s, IPv: %s" % (host, prio, ipv))

				records.append({'prio': prio, 'host': ipv[0], 'ip': ipv[2], \
						'connection_type': ipv[1]})
				self.result.info('Found host %s (%s), priority %s', (host, ipv[2], prio))
				if (ipv[1] == "INET6"):
					ipv = get_ipv_type(host, "INET")
					if (ipv[2] != None):
						records.append({'prio': prio, 'host': ipv[0], 'ip': ipv[2], \
							'connection_type': ipv[1]})
						self.result.info('Found host %s (%s), priority %s', (host, ipv[2], prio))
		else:
			prio = "-1"
			host = domain
			ipv = get_ipv_type(host)
			if len(ipv) != 0:
				records.append({'prio': prio, 'host': ipv[0], 'ip': ipv[2], \
					'connection_type': ipv[1]})
				self.result.info('Found host %s (%s), priority %s', (host, ipv[2], prio))
				if (ipv[1] == "INET6"):
					ipv = get_ipv_type(host, "INET")
					if (ipv[2] != None):
						records.append({'prio': prio, 'host': ipv[0], 'ip': ipv[2], \
							'connection_type': ipv[1]})
						self.result.info('Found no MX-record, using host %s (%s)', \
								(host, ipv[2]))

		message = ""
		code = Plugin.STATUS_OK
		if len(records) == 0:
			message = 'No records found'
			code = Plugin.STATUS_ERROR
			self.result.error(message)
		elif len(records) == 1 and records[0]['prio'] == "-1" and self.isChild != 0:
			message = 'No MX-records found, using A/AAAA-record'
			code = Plugin.STATUS_OK
			self.result.info(message)
		elif len(records) == 1 and records[0]['prio'] == "-1" and self.isChild == 0:
			message = 'No MX-records found, using A/AAAA-record'
			code = Plugin.STATUS_WARNING
			self.result.warning(message)
		elif len(records) == 1 and records[0]['connection_type'] == "INET6" \
				and self.isChild == 0:
			message = 'Only IPv6 addresses found, this might cause delivery problems'
			code = Plugin.STATUS_WARNING
			self.result.warning(message)
		elif len(records) == 1 and self.isChild == 0:
			message = 'Only one record found, two or more is recommended'
			code = Plugin.STATUS_OK
			self.result.info(message)
		else:
			message = 'Multiple MX-records found'
			code = Plugin.STATUS_OK
			self.result.info(message)

		self.result.extra('more info mx record', type='adv')

		self.result.info('Finished MX record lookup against %s', (domain))

		# Output
		if len(records) == 0:
			self.result.setOutput(None)
		else:
			self.result.setOutput({'mx_record': records}, persist=True)

		self.result.setTestStatus(code)


if __name__ == '__main__':
	from engine.plugins.common import runTestPlugin

	plugin = MXRecord()
	db, result = runTestPlugin(plugin, 'gatorhole.com')
