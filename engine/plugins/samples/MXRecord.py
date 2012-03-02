# import adns module used to lookup MX records
import adns

# import necessary classes and functions from mailcheck framework (mailcheck folder must be on PYTHONPATH or similar)
from engine import log
from engine.plugins.common import *
from engine.plugins.Plugin import Plugin, Result, PluginSockets

# Add plugins should extend the base Plugin class. It provides support for handling  
# result and input/output from the plugin.
class MXRecord(Plugin):
	"""Checks a domain for MX records
	
	Input: domain
	Output: MX records
	"""

	def __init__(self):
		# Make sure base class __init__ is called to correctly setup the plugin
		Plugin.__init__(self)
		
		# Set category to a uid which is to be translated and then as a category on the result page in the frontend.
		self.category = "DNS"
	
	def run(self):
		"""
		Called by the test runner script to start execution of the test.
		"""
		# Get the domain we are testing so we can lookup MX records
		domain = self.getInput('domain')

		# Log a default info message which will turn up under advanced in the frontend. The string is a uid which
		# will be translated and each %s will be replaced with the values from second argument that should be a tuple.
		self.result.info('Starting MX record lookup against %s', (domain))

		# Initialize the adns module
		dns = adns.init()

		# lookup MX records for the domain
		mxRecords = dns.synchronous(domain, adns.rr.MX)

		# Create a list for the MX records
		records = []
		if (len(mxRecords[3]) >= 1):
		
			# if any MX-record was found, loop through each record
			for i in mxRecords[3]:
				prio = str(i[0])
				host = i[1][0]
				ipv = get_ipv_type(host)
				if self.logger:
					self.log.info("Host: %s, Prio: %s, IPv: %s" % (host, prio, ipv))

				# Add the found records to the list with records. We save priority, host, IP and IP version (INET or INET6)
				records.append({'prio': prio, 'host': ipv[0], 'ip': ipv[2], 'connection_type': ipv[1]})

				# Add a line to the frontend informing the user about the record we found
				self.result.info('Found host %s (%s), priority %s', (host, ipv[2], prio) )

				# if record type is IPv6 also obtain IPv4 address if possible
				if (ipv[1] == "INET6"):
					ipv = get_ipv_type(host, "INET")
					if (ipv[2] != None):
						records.append({'prio': prio, 'host': ipv[0], 'ip': ipv[2], 'connection_type': ipv[1]})
						self.result.info('Found host %s (%s), priority %s', (host, ipv[2], prio) )
		else:
			# If no MX record was found, we try to use the A record instead
			# Set prio to -1 to symbolise that no MX-record is available and only hostname is used
			prio="-1"
			host=domain

			ip=get_arecord(domain)
			ipv=get_ipv_type(host)

			# If a A record is set use that one for further tests instead of MXRecord
			if len(ipv) != 0:
				records.append({'prio': prio, 'host': ipv[0], 'ip': ipv[2], 'connection_type': ipv[1]})
				self.result.info('Found host %s (%s), priority %s', (host, ipv[2], prio) )
				# If the hostname has a AAAA-record also check if a A-record exists
				if (ipv[1] == "INET6"):
					ipv = get_ipv_type(host, "INET")
					if (ipv[2] != None):
						records.append({'prio': prio, 'host': ipv[0], 'ip': ipv[2], 'connection_type': ipv[1]})
						self.result.info('Found no MX-record, using host %s (%s)', (host, ipv[2]) )

		# Set final status code and message
		message = ""
		code = Plugin.STATUS_OK
		if len(records) == 0: 
			message = 'No records found'
			code = Plugin.STATUS_ERROR
			self.result.error(message)
		elif len(records) == 1 and records[0]['prio'] == "-1" and self.isChild != 0:
			message = 'No MX-records found, using A/AAAA-record'
			code = Plugin.STATUS_OK
			self.result.info(message)
		elif len(records) == 1 and records[0]['prio'] == "-1" and self.isChild == 0:
			message = 'No MX-records found, using A/AAAA-record'
			code = Plugin.STATUS_WARNING
			self.result.warning(message)
		elif len(records) == 1 and records[0]['connection_type'] == "INET6" and self.isChild == 0:
			message = 'Only IPv6 addresses found, this might cause delivery problems'
			code = Plugin.STATUS_WARNING
			self.result.warning(message)
		elif len(records) == 1 and self.isChild == 0:
			message = 'Only one record found, two or more is recommended'
			code = Plugin.STATUS_OK
			self.result.info(message)
		else:
			message = 'Multiple MX-records found'
			code = Plugin.STATUS_OK
			self.result.info(message)

		# Print final message to advanced output
		self.result.info('Finished MX record lookup against %s', (domain))

		if len(records) == 0:
			# If we didn't find any records at all, output from this plugin should be None
			self.result.setOutput(None)
		else:
			# Create the final output dict and mark it with the persist flag. That will
			# cause the result to be automatically saved to the database.
			self.result.setOutput({'mx_record': records}, persist=True)
	
		# Set the final test status for this plugin (shown in UI)
		self.result.setTestStatus(code)
		

if __name__ == '__main__':
	pass
