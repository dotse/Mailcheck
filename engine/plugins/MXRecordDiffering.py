
import dns.resolver

from engine import log
from engine.plugins.common import *
from engine.plugins.Plugin import Plugin, Result


class MXRecordDiffering(Plugin):
	"""
	Check if any of MX-Records is different between our dns and the servers dns-server
	"""
	
	def __init__(self):
		Plugin.__init__(self)
		
		self.category = "DNS"
		self.requiredInput = ['MXRecord']

	def run(self):
		domain = self.getInput('domain')
		records = self.getInput('MXRecord')
		
		self.result.info('Starting differing MX records test')

		nameservers = get_name_servers(domain)
		
		code = Plugin.STATUS_OK
		nsResult = {}
		for ns in nameservers:
			nsHost = ns[0]
			nsIP = ns[1]
			
			for row in records['mx_record']:
				mxHost = row['host']
				mxIp = row['ip']
				mxType = row['connection_type']
				a = ipv_type_to_a_type(mxType)

				if not mxHost in nsResult:
					nsResult[mxHost] = {}

				nsResult[mxHost][nsIP] = []
				aRecord = get_arecord(mxHost, mxType, [nsIP])
				if len(aRecord) > 0:	
					self.result.info('Getting %s record from name server %s (%s) for MX record %s', (a, nsHost, nsIP, mxHost))
				else:
					self.result.warning('Could not get %s record for MX record %s from name server %s (%s)', (a, mxHost, nsHost, nsIP))
					code = Plugin.STATUS_WARNING
					del nsResult[mxHost][nsIP]
					continue;

				for adr in aRecord:
					nsResult[mxHost][nsIP].append( adr )

				nsResult[mxHost][nsIP].sort()

				ips = ', '.join(nsResult[mxHost][nsIP])
				if len(nsResult[mxHost][nsIP]) > 1:
					self.result.info('Name server %s (%s) reported the following %s records %s for MX record %s', (nsHost, nsIP, a, ips, mxHost))
				else:
					self.result.info('Name server %s (%s) reported the following %s record %s for MX record %s', (nsHost, nsIP, a, ips, mxHost))

		"""Compare result from name servers"""
		for mx in nsResult:
			lastNS = None
			
			for ns in nsResult[mx]:
				if lastNS == None:
					lastNS = ns
					continue

				if nsResult[mx][ns] == nsResult[mx][lastNS]:
					pass
				else:
					self.result.warning("Name servers %s and %s reports different records for MX record %s", (ns, lastNS, mx))
					code = Plugin.STATUS_WARNING
				lastNS = ns
			
		self.result.info('Finished differing MX records test')
		self.result.setTestStatus(code)
