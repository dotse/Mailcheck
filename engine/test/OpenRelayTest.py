
import unittest

from engine.plugins.OpenRelay import *
from engine.plugins.common import runTestPlugin

class OpenRelayTest(unittest.TestCase):
	def setUp(self):
		self.domain = 'gatorhole.com'
		self.p = OpenRelay()

	def testOpenRelay(self):
		data = [
			['10', 'lonn.org', '213.136.43.225', 'INET'],
			]
		self.p.setInput('MXRecord', data)
		self.p.setInput('email', 'mailcheck@gatorhole.com')
		r = runTestPlugin(self.p, self.domain)
		status = r.getFinalStatus()[2]
		print r
		self.assertEqual(status, Plugin.STATUS_OK)



if __name__ == '__main__':
	unittest.main()

