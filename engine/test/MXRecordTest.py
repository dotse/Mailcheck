
import unittest

from engine.plugins.MXRecord import *
from engine.plugins.common import runTestPlugin

class MXRecordTest(unittest.TestCase):
	def setUp(self):
		self.domain = 'gatorhole.com'
		self.p = MXRecord()

	def test(self):
		r = runTestPlugin(self.p, self.domain)
		status = r.getFinalStatus()
		self.assertEqual(status, Plugin.STATUS_OK)



if __name__ == '__main__':
	unittest.main()
