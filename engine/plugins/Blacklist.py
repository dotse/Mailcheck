import adns
from re import match, compile, sub

from engine.plugins.common import *
from engine.plugins.Plugin import Plugin


class Blacklist(Plugin):
	"""
	Check if you're on any blacklist
	"""

	def __init__(self):
		Plugin.__init__(self)
		self.requiredInput = ['MXRecord']
		self.category = 'DNS'

	def run(self):
		testId = self.getInput('testId')
		records = self.getInput('MXRecord')
		pluginName = self.__class__.__name__
		ipregexp = compile(r'^([0-9]*).([0-9]*).([0-9]*).([0-9]*)$')

		res = adns.init()

		blacklist = []
		blacklist.append(("multi.uribl.com", "http://uribl.com"))
		blacklist.append(("dsn.rfc-ignorant.org", "http://rfc-ignorant.org"))
		blacklist.append(("dul.dnsbl.sorbs.net", "http://www.au.sorbs.net"))
		blacklist.append(("sbl-xbl.spamhaus.org", "http://spamhaus.org"))
		blacklist.append(("bl.spamcop.net", "http://spamcop.net"))
		blacklist.append(("dnsbl.sorbs.net", "http://www.au.sorbs.net"))
		blacklist.append(("cbl.abuseat.org", "http://abuseat.org"))
		blacklist.append(("ix.dnsbl.manitu.net", "http://www.dnsbl.manitu.net"))
		blacklist.append(("combined.rbl.msrbl.net", "http://msrbl.net"))
		blacklist.append(("rabl.nuclearelephant.com", "http://nuclearelephant.com"))

		self.result.info('Starting Blacklist-test')

		if len(records['mx_record']) <= 0:
			result.error('Test could not be executed')

		results = []
		statusCounts = {Plugin.STATUS_OK: 0, Plugin.STATUS_WARNING: 0, Plugin.STATUS_ERROR: 0}

		for record in records['mx_record']:
			host = record['host']
			ip = record['ip']
			blacklistip = sub(ipregexp, r'\4.\3.\2.\1', ip)

			code = Plugin.STATUS_OK
			reply_code = reply_msg = None
			try:
				for cbl in blacklist:
					url = cbl[1]
					cbl = cbl[0]

					cblhost = str(blacklistip + "." + cbl)
					self.livefeedback.message(testId, "%s, subtest: %s in %s?", (pluginName, ip, cbl))
					try:
						addr = res.synchronous(cblhost, adns.rr.A)
						reply_code = addr[3][0]
						msg = res.synchronous(cblhost, adns.rr.TXT)
						reply_msg = msg[3][0][0]
					except:
						pass

					# Add status message
					if(match(ipregexp, str(reply_code))):
						self.result.warning('%s (%s) is listed on blacklist %s, result: %s, text: %s.', (ip, host, cbl, reply_code, reply_msg))
						self.result.extra('<a href="%s" target="_blank">%s</a>' % (url, url), type='all')
					else:
						self.result.info('%s (%s) is not listed on blacklist %s.', (ip, host, cbl))
						self.result.extra('<a href="%s" target="_blank">%s</a>' % (url, url), type='adv')

					results.append([host, ip, cblhost, reply_code, reply_msg])
					statusCounts[code] += 1
			except:
				pass

		# Figure the final status of the test
		code = Plugin.STATUS_OK
		if statusCounts[Plugin.STATUS_WARNING] > 0 and statusCounts[Plugin.STATUS_WARNING] == len(results):
			code = Plugin.STATUS_ERROR
			self.result.error('All Blacklist-tests failed!')

		self.result.extra('more info blacklists', type='adv')
		self.result.info('Finished Blacklist-test')
		self.result.setTestStatus(code)

