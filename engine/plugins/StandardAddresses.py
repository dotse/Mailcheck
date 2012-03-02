import socket
import re
import string
from common import connect_to_host
from Plugin import Plugin, Result
import dns.resolver

class StandardAddresses(Plugin):
	"""
	Check for SOA and standard email addresses
	"""
	
	def __init__(self):
		Plugin.__init__(self)
		self.requiredInput = ['MXRecord']
		self.category = 'SMTP'

	def run(self):
		domain = self.getInput('domain')
		email = self.getInput('email')
		records = self.getInput('MXRecord')
		port = 25

		self.result.info('Started standard addresses test')

		testResult = []
		for row in records['mx_record']:
			host = row['host']
			ip = row['ip']
			type = row['connection_type']

			try:
				s = connect_to_host(ip, port, type, self)
                        except Exception, e:
				self.result.warning('Failed to connect to mail server %s (%s)', (host, ip))
				continue


				data = s.recv(1024)

			except Exception, e:
				self.result.warning('Failed to connect to %s (%s)', (host,ip))
				continue

			try:
				"""lookup SOA record and replace first dot with @t"""
				mail_record=dns.resolver.query(domain, "SOA").rrset[0].to_text().split()[1][0:-1]
				soa_mail=re.sub('\.', '@', mail_record, 1)
			except:
				soa_mail=''
				pass
			mailfrom='MAIL FROM: mailcheck@%s\r\n' % socket.getfqdn()

			conversation = [
				[
					'EHLO %s\r\n' % socket.getfqdn(),
					mailfrom,
					'RCPT TO: postmaster@%s\r\n' % domain,
					'RSET\r\n',
					mailfrom,
					'RCPT TO: hostmaster@%s\r\n' % domain,
					'RSET\r\n',
					mailfrom,
					'RCPT TO: abuse@%s\r\n' % domain,
					'RSET\r\n',
					mailfrom,
					'RCPT TO: %s\r\n' % soa_mail,
					'RSET\r\n',
				],
				[
					'.*',
					'250.*',
					'250.*',
					'250.*',
					'250.*',
					'250.*',
					'250.*',
					'250.*',
					'250.*',
					'250.*',
					'250.*',
					'250.*',
					'250.*',
				],
				[
					'252.*|50[0-4].*'
				]
			]

			# Scan for users
			testlog = ''
			error = False
			counter250 = 0
			for i in range(len(conversation[0])):
				send = conversation[0][i]
				recv = conversation[1][i]
				testlog = ''
				
				if i == 0:
					data = s.recv(1024)
					testlog += "<<< %s" % data

				s.send(send)
				testlog += ">>> %s" % send

				data = s.recv(1024)
				testlog += "<<< %s" % data
				self.result.info('%s', testlog)

				if not re.search(recv, data):
					self.result.warning("Standard addresses on %s (%s) failed\n%s", (host,ip,testlog))
					error = True
					pass

				if re.search(conversation[2][0], data):
					counter250 += 1

			#s.close()
			testResult.append(error)

			if counter250 == 12:
				self.result.goldstar("%s (%s) answering \"250\".", (host, ip))

			if error:
				#self.result.warning("Standard addresses on %s (%s) failed\n%s", (host,ip,testlog))
				gurka=""
			else:
				self.result.info('Standard addresses on %s (%s) completed.', (host,ip))


		self.result.info('Finished standard addresses test')
		
		code = Plugin.STATUS_OK
		if True in testResult:
			code = Plugin.STATUS_WARNING
		
		self.result.setTestStatus(code)
