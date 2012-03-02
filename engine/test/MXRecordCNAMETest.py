
import unittest

from engine.plugins.common import runTestPlugin
from engine.plugins.MXRecordCNAME import *

class MXRecordCNAMETest(unittest.TestCase):
	def setUp(self):
		self.domain = 'sunet.com'
		self.p = MXRecordCNAME()

	def testCNAME(self):
		data = [
			{'prio': '10', 'host': 'njord.sunet.se', 'ip': '192.36.125.194', 'connection_type': 'INET'},
			]
		self.p.setInput('MXRecord', {'mx_record': data})
		r = runTestPlugin(self.p, self.domain)
		status = r.getFinalStatus()
		self.assertEqual(status, Plugin.STATUS_OK)


if __name__ == '__main__':
	unittest.main()

