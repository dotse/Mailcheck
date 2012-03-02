
import smtplib

from engine.plugins.common import *
from engine.plugins.Plugin import Plugin


class StartTLS(Plugin):
	"""
	Check if mailservers handles STARTTLS
	"""

	def __init__(self):
		Plugin.__init__(self)
		self.requiredInput = ['MXRecord', 'Connection']
		self.category = "SMTP"

	def run(self):
		records = self.getInput('MXRecord')

		self.result.info('Starting STARTTLS test')
		testResult = []
		goldstar = False
		ret = []
		for row in records['mx_record']:
			host = row['host']
			ip = row['ip']
			type = row['connection_type']

			success = False
			try:
				server = smtplib.SMTP(host)
				server.ehlo(host)
			except smtplib.SMTPServerDisconnected:
				self.result.warning("Server %s (%s) disconnected unexpectedly", (host, ip))
				continue
			except Exception:
				self.result.warning("Unable to connect to host %s (%s)", (host, ip))
				continue

			res = []
			try:
				res = server.starttls()
				if (res[0] == 220):
					success = res
			except smtplib.SMTPException:
				res.append("STARTTLS extension not supported by server.")
				res.append("")
			except:
				pass

			testResult.append(success)
			if success:
				if goldstar == False:
					self.result.goldstar('STARTTLS enabled')
					goldstar = True
				self.result.info('STARTTLS successful on host %s (%s), %s %s', (host, ip, str(res[0]), str(res[1])))
			else:
				self.result.info('STARTTLS failed on host %s (%s), %s %s', (host,ip,str(res[0]),str(res[1])))

			ret.append({'host': host, 'connection_type': type, 'ip': ip, 'starttls': success})

		self.result.extra('more info starttls', type='adv')

		self.result.info('Finished STARTTLS test')

		# Final result
		code = Plugin.STATUS_OK

		self.result.setTestStatus(code)
		self.result.setOutput({'starttls': ret}, persist=True)
