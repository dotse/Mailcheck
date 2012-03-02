
import unittest

from engine.plugins.common import runTestPlugin
from engine.plugins.MXRecordPublic import *

class MXRecordPublicTest(unittest.TestCase):
	def setUp(self):
		self.domain = 'mydomain.com'
		self.p = MXRecordPublic()

	def testOnePublic(self):
		data = [
			{'prio': '10', 'host': 'test.com', 'ip': '200.1.1.1', 'connection_type': 'INET'},
			]
		self.p.setInput('MXRecord', {'mx_record': data})
		r = runTestPlugin(self.p, self.domain)
		status = r.getFinalStatus()

		self.assertEqual(status, Plugin.STATUS_OK)

	def testOnePrivate(self):
		data = [
			{'prio': '10', 'host': 'test.com', 'ip': '192.168.23.31', 'connection_type': 'INET'},
			]
		self.p.setInput('MXRecord', {'mx_record': data})
		r = runTestPlugin(self.p, self.domain)
		status = r.getFinalStatus()
		
		self.assertEqual(status, Plugin.STATUS_ERROR)

	def testPrimaryPrivate(self):
		data = [
			{'prio': '10', 'host': 'test.com', 'ip': '192.168.23.31', 'connection_type': 'INET'},
			{'prio': '20', 'host': 'test.com', 'ip': '200.200.23.31', 'connection_type': 'INET'},
			]
		self.p.setInput('MXRecord', {'mx_record': data})
		r = runTestPlugin(self.p, self.domain)
		status = r.getFinalStatus()

		self.assertEqual(status, Plugin.STATUS_ERROR)

	
	def testTwoPrivatePrimaryPublic(self):
		data = [
			{'prio': '10', 'host': 'test.com', 'ip': '200.200.23.31', 'connection_type': 'INET'},
			{'prio': '20', 'host': 'test.com', 'ip': '192.168.23.31', 'connection_type': 'INET'},
			{'prio': '30', 'host': 'test.com', 'ip': '192.168.24.31', 'connection_type': 'INET'},
			]
		self.p.setInput('MXRecord', {'mx_record': data})
		r = runTestPlugin(self.p, self.domain)
		status = r.getFinalStatus()
		self.assertEqual(status, Plugin.STATUS_WARNING)


	def testPublicIPV6(self):
		data = [
			{'prio': '10', 'host': 'test.com', 'ip': '2001:0db8:85a3:08d3:1319:8a2e:0370:7348', 'connection_type': 'INET6'},
			]
		self.p.setInput('MXRecord', {'mx_record': data})
		r = runTestPlugin(self.p, self.domain)
		status = r.getFinalStatus()

		self.assertEqual(status, Plugin.STATUS_OK)


	def testPrivateIPV6(self):
		data = [
			{'prio': '10', 'host': 'test.com', 'ip': 'fc00:0db8:85a3:08d3:1319:8a2e:0370:7348', 'connection_type': 'INET6'},
			]
		self.p.setInput('MXRecord', {'mx_record': data})
		r = runTestPlugin(self.p, self.domain)
		status = r.getFinalStatus()

		self.assertEqual(status, Plugin.STATUS_ERROR)

	
	def testMixedIP(self):
		data = [
			{'prio': '10', 'host': 'test.com', 'ip': '2001:0db8:85a3:08d3:1319:8a2e:0370:7348', 'connection_type': 'INET6'},
			{'prio': '20', 'host': 'test.com', 'ip': '200.200.23.31', 'connection_type': 'INET'},
			{'prio': '30', 'host': 'test.com', 'ip': '10.10.23.31', 'connection_type': 'INET'},
			]
		self.p.setInput('MXRecord', {'mx_record': data})
		r = runTestPlugin(self.p, self.domain)
		status = r.getFinalStatus()

		self.assertEqual(status, Plugin.STATUS_WARNING)



if __name__ == '__main__':
	unittest.main()
