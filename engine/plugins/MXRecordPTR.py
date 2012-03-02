
import dns.resolver
import dns.reversename

from engine.plugins.common import get_ipv_type, get_arecord, ipv_type_to_a_type
from engine.plugins.Plugin import Plugin, Result


class MXRecordPTR(Plugin):
	"""
	Check if servers obtained by MXRecord plugin has a PTR record which resolvs
	to the same IP
	"""

	def __init__(self):
		Plugin.__init__(self)
		self.requiredInput = ['MXRecord']
		self.category = 'DNS'

	def run(self):
		records = self.getInput('MXRecord')

		self.result.info('Starting test')

		testResult = []
		for row in records['mx_record']:
			mxHost = row['host']
			mxType = row['connection_type']

			a = ipv_type_to_a_type(mxType)

			# Find A record for MX record
			arecord = get_arecord(mxHost, mxType)

			if not len(arecord):
				self.result.warning('Could not find %s record for MX record %s', (a, mxHost))
				continue

			# TODO: multiple here?
			arecordIP = arecord[0]
			arecordReverse = dns.reversename.from_address(arecordIP)
			arecordReverse = arecordReverse.to_text()

			# Find PTR record from reverse A record
			ptr = ''
			try:
				ptr = dns.resolver.query(arecordReverse, 'PTR')
				ptr = ptr.rrset[0]
				ptr = ptr.to_text()[0:-1]
			except:
				pass

			if ptr == '':
				self.result.warning('Could not find PTR record for %s', (arecordReverse))
				continue

			# TODO: multiple here?
			ptrHost = ptr

			# Resolve PTR
			resolvedIP = get_ipv_type(ptrHost, mxType)
			if len(resolvedIP) < 3:
				self.result.warning('Could not resolve PTR record %s', (ptrHost))
				continue

			if resolvedIP[2] == arecordIP:
				self.result.info('PTR record (%s) matches the %s record (%s)', \
						(ptrHost, a, arecordIP))
			else:
				testResult.append(arecordIP)
				self.result.warning('PTR record does not match the %s record (%s)', (a, arecordIP))

		code = Plugin.STATUS_OK
		if len(testResult) > 0:
			code = Plugin.STATUS_WARNING

		self.result.extra('more info ptr mx record', type='adv')

		self.result.info('Finished test')
		self.result.setTestStatus(code)
