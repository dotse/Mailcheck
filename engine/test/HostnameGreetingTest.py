
import unittest

from engine.plugins.common import runTestPlugin
from engine.plugins.HostnameGreeting import *

class HostnameGreetingTest(unittest.TestCase):
	def setUp(self):
		self.domain = 'mydomain.com'
		self.p = HostnameGreeting()

	def test(self):
		data = {'mx_record': [{'connection_type': 'INET', 'ip': '109.228.153.253', 'host': 'maple.lonn.org', 'prio': '10'}]}
		self.p.setInput('MXRecord', data)
		r = runTestPlugin(self.p, self.domain)

		status = r.getFinalStatus()
		self.assertEqual(status, Plugin.STATUS_OK)


if __name__ == '__main__':
	unittest.main()
