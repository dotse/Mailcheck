
import unittest

from engine.plugins.common import runTestPlugin
from engine.plugins.MXRecordDuplicate import *

class MXRecordDuplicateTest(unittest.TestCase):
	def setUp(self):
		self.domain = 'mydomain.com'
		self.p = MXRecordDuplicate()

	def testNoDuplicates(self):
		data = [
			{'prio': '10', 'host': 'test.com', 'ip': '192.168.1.2', 'connection_type': 'INET'},
			{'prio': '20', 'host': 'test2.com', 'ip': '192.168.1.3', 'connection_type': 'INET'},
			]
		self.p.setInput('MXRecord', {'mx_record': data})
		r = runTestPlugin(self.p, self.domain)
		status = r.getFinalStatus()

		self.assertEqual(status, Plugin.STATUS_OK)

	def testDuplicate(self):
		data = [
			{'prio': '10', 'host': 'test.com', 'ip': '192.168.1.2', 'connection_type': 'INET'},
			{'prio': '20', 'host': 'test2.com', 'ip': '192.168.1.2', 'connection_type': 'INET'},
			]
		self.p.setInput('MXRecord', {'mx_record': data})
		r = runTestPlugin(self.p, self.domain)
		status = r.getFinalStatus()

		self.assertEqual(status, Plugin.STATUS_WARNING)

	def testMultiDuplicate(self):
		data = [
			{'prio': '10', 'host': 'test.com', 'ip': '192.168.1.1', 'connection_type': 'INET'},
			{'prio': '20', 'host': 'test2.com', 'ip': '192.168.1.2', 'connection_type': 'INET'},
			{'prio': '20', 'host': 'test3.com', 'ip': '192.168.1.2', 'connection_type': 'INET'},
			{'prio': '20', 'host': 'test4.com', 'ip': '192.168.1.2', 'connection_type': 'INET'},
			]
		self.p.setInput('MXRecord', {'mx_record': data})
		r = runTestPlugin(self.p, self.domain)
		status = r.getFinalStatus()
	
		self.assertEqual(status, Plugin.STATUS_WARNING)

	def test2Duplicate(self):
		data = [
			{'prio': '10', 'host': 'test.com', 'ip': '192.168.1.2', 'connection_type': 'INET'},
			{'prio': '20', 'host': 'test2.com', 'ip': '192.168.1.3', 'connection_type': 'INET'},
			{'prio': '10', 'host': 'test3.com', 'ip': '192.168.1.2', 'connection_type': 'INET'},
			]
		self.p.setInput('MXRecord', {'mx_record': data})
		r = runTestPlugin(self.p, self.domain)
		status = r.getFinalStatus()

		self.assertEqual(status, Plugin.STATUS_WARNING)



if __name__ == '__main__':
	unittest.main()
