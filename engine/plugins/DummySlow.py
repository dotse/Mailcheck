
import time
from common import *
from Plugin import Plugin, Result

class DummySlow(Plugin):
	"""
	Sample plugin for slow tests, sleeps for 60 seconds
	"""
	def __init__(self):
		Plugin.__init__(self)
	
		self.category = "SLOW"
	
	def run(self):
		self.result.info('Starting Slow test')
		
		self.result.info('Dumdidummy')
		time.sleep(60)
		self.result.info('Dumdidummyx2')
		
	
		self.result.info('Finished Slow test');

		# Output
		self.result.setOutput(None)
		
		self.result.setTestStatus(Plugin.STATUS_WARNING)
		

if __name__ == '__main__':
	pass
