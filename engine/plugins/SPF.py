
import spf
import socket

from engine.plugins.Plugin import Plugin


class SPF(Plugin):
	"""
	Verify SPF records
	"""

	def __init__(self):
		Plugin.__init__(self)
		# Set the reqired input to the output from the MXRecord plugin.
		self.requiredInput = ['MXRecord']
		# Set the category this plugin belongs to
		self.category = 'DNS'

	def run(self):
		# Get standard input 'email'
		email = self.getInput('email')
		# Get input from the execution of the MXRecord plugin
		records = self.getInput('MXRecord')

		# First information messages to say test is underway
		self.result.info('Starting SPF-test')

		results = []
		statusCounts = {Plugin.STATUS_OK: 0, Plugin.STATUS_WARNING: 0, Plugin.STATUS_ERROR: 0}
		star = False

		# Loop through all MX records and perform the SPF test
		for record in records['mx_record']:
			host = record['host']
			ip = record['ip']

			passCode = 250
			code = Plugin.STATUS_OK
			error = ""
			try:
				# Perform the actual SPF control using the spf module
				spf_res_ret, spf_res_code, spf_res_desc = spf.check(ip, email, host)

				# Check if the returned code is 250 and up the warning counter if it's not
				if spf_res_code != passCode:
					statusCounts[Plugin.STATUS_WARNING] += 1
				#
				elif spf_res_code == 250 and spf_res_ret != 'none' and star == False:
					star = True
			except socket.error, e:
				code = Plugin.STATUS_WARNING
				if e[0] == 101:
					error = "network unreachable"
				elif e[0] == 111:
					error = "connection refused"
				elif e[0] == 110 or e[0] == 'timed out' or e == 'timed out':
					error = "connection timed out"
				else:
					error = "unable to connect"

			# Add information message if the test failed for this MX. We only see SPF
			# as a bonus feature, that's why we don't add a warning here
			if error != '':
				self.result.info('SPF-test failed for %s (%s)', (host, ip))
			# We add a warning here bacause SPF exists but is not configured correctly
			elif spf_res_code != passCode:
				self.result.warning('SPF-test returned: %s (%s), %s for %s (%s), email: %s', (spf_res_ret, spf_res_code, spf_res_desc, host, ip, email))
			else:
				self.result.info('SPF-test returned: %s (%s), %s for %s (%s), email: %s', (spf_res_ret, spf_res_code, spf_res_desc, host, ip, email))

			# Add this test to the result from the SPF plugin
			results.append([host, ip, email, spf_res_ret, spf_res_code, spf_res_desc])
			statusCounts[code] += 1

		# Check if this test should receive a gold star
		if star == True:
			if self.isChild != 0:
				goldstar_text = "SPF is valid from the server you use to send emails"
			else:
				goldstar_text = "SPF is enabled for domain"
			self.result.goldstar(goldstar_text)

		# Figure the final status of the test
		code = Plugin.STATUS_OK
		if statusCounts[Plugin.STATUS_WARNING] > 0 and statusCounts[Plugin.STATUS_WARNING] == len(results):
			code = Plugin.STATUS_ERROR
			self.result.error('All SPF tests failed!')

		self.result.extra('more info spf', type='adv')

		self.result.info('Finished SPF-test')
		# Set the final status for the plugin
		self.result.setTestStatus(code)


def test():
	from engine.plugins.common import runTestPlugin
	#data = [['10', 'lonn.org', '213.136.43.225', 'INET']]	
	data = [{'prio': '10', 'host': 'lonn.org', 'ip': '192.168.3.2', 'connection_type': 'INET'}]
	email = 'alex@gatorhole.com'

	s = SPF()
	s.isChild = 0
	s.setInput('MXRecord', {'mx_record': data})

	s.setInput('email', email)
	r = runTestPlugin(s, 'gatorhole.com')
	print r

if __name__ == '__main__':
	test()
