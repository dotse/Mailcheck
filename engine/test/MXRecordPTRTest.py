
import unittest

from engine.plugins.MXRecordPTR import *
from engine.plugins.common import runTestPlugin

class MXRecordPTRTest(unittest.TestCase):
	def setUp(self):
		self.domain = 'sunet.se'
		self.p = MXRecordPTR()

	def test(self):
		data = [
			{'prio': '10', 'host': 'njord.sunet.se', 'ip': '192.36.125.194', 'connection_type': 'INET'},
			]
		self.p.setInput('MXRecord', {'mx_record': data})
		r = runTestPlugin(self.p, self.domain)
		status = r.getFinalStatus()
		
		self.assertEqual(status, Plugin.STATUS_OK)



if __name__ == '__main__':
	unittest.main()
