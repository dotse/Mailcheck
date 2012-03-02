
import unittest

from engine.plugins.common import runTestPlugin
from engine.plugins.UserScanning import *

class UserScanningTest(unittest.TestCase):
	def setUp(self):
		self.domain = 'gatorhole.com'
		self.p = UserScanning()

	def testSuccessful(self):
		data = {'mx_record': [{'connection_type': 'INET', 'ip': '109.228.153.253', 'host': 'maple.lonn.org', 'prio': '10'}]}
		self.p.setInput('MXRecord', data)
		self.email = 'postmaster@gatorhole.com'
		r = runTestPlugin(self.p, self.domain, self.email)
		status = r.getFinalStatus()

		self.assertEqual(status, Plugin.STATUS_OK)


	def testFailiure(self):
		data = {'mx_record': [{'connection_type': 'INET', 'ip': '109.228.153.253', 'host': 'maple.lonn.org', 'prio': '10'}]}
		self.p.setInput('MXRecord', data)
		self.email = 'jskdk@gatorhole.com'
		r = runTestPlugin(self.p, self.domain, self.email)
		status = r.getFinalStatus()

		self.assertEqual(status, Plugin.STATUS_WARNING)


if __name__ == '__main__':
	unittest.main()
