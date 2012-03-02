import OpenSSL
import datetime, time, re, subprocess

from engine.plugins.common import *
from engine.plugins.Plugin import Plugin


class VerifyCert(Plugin):
	"""
	Verify certificates
	"""

	def __init__(self):
		Plugin.__init__(self)
		self.requiredInput = ['StartTLS']
		self.category = 'SMTP'

	def run(self):
		testId = self.getInput('testId')
		pluginName = self.__class__.__name__

		try:
			records = self.getInput('StartTLS')
		except:
			self.result.error('Unable to obtain TLS enabled records')
			code = Plugin.STATUS_ERROR
			self.result.setTestStatus(code)
			self.result.setOutput('error')
			return

		min_ssl_cert_bits = int(self.pluginConfig.get('min_ssl_cert_bits'))
		max_ssl_cert_age = int(self.pluginConfig.get('max_ssl_cert_age'))
		port = 25
		myhostname = socket.getfqdn()

		day = 86400
		week = 604800
		month = 2592000
		year = 31536000
		statusCounts = 0

		self.result.info('Starting to verify certificates')

		if len(records['starttls']) <= 0:
			self.result.error('Test could not be executed')

		results = []
		statusCounts = {Plugin.STATUS_OK: 0, Plugin.STATUS_WARNING: 0, Plugin.STATUS_ERROR: 0}
		for record in records['starttls']:
			host = record['host']
			type = record['connection_type']
			ip = record['ip']
			tls_available = record['starttls']

			self.result.info("Starting test for host %s (%s)", (host, ip))
			if tls_available == False:
				self.result.info("NO TLS available for host %s", (host))
				continue

			code = Plugin.STATUS_OK
			reply_code = reply_msg = None
			try:
				s = connect_to_host(host, port, type, self)
				data = s.recv(1024)
			except Exception, e:
				self.result.warning('Failed to connect to host %s (%s)', (host,ip))
				statusCounts[Plugin.STATUS_WARNING] += 1
				continue
			cmd = [
				[
					'EHLO ' + myhostname + '\r\n',
					'STARTTLS\r\n'
				], [
					'250',
					'220 2.0.0.*'
				], [
					'554.*|501.*|503.*|553.*|550.*|555.*|401.*|454.*'
				]
			]

			testlog=""

			for row in range(len(cmd[1])):
				exit_code=int()
				send=cmd[0][row]
				recv=cmd[1][row]
				ssl_serial_last_time=time.time()
				try:
					s.send(send)
				except Exception, e:
					if e[0] == 104:
						self.result.info("Warning connection reset by peer..")
					if e[0] == 32:
						self.result.info("Warning broken pipe..")
						s = connect_to_host(host, port, type)
				testlog += ">>> " + send

				try:
					data = s.recv(1024)
				except Exception, e:
					if e[0] == 104:
						self.result.info("Warning connection reset by peer..")
					if e[0] == 32:
						self.result.info("Warning broken pipe..")
						s = connect_to_host(host, port, type)
					continue

				testlog += "<<< " + data

				if row == (len(cmd[0])-1):
					ssl_context=OpenSSL.SSL.Context(OpenSSL.SSL.SSLv23_METHOD)
					ssl_sock=OpenSSL.SSL.Connection(ssl_context, s)
					preverifyok=0
					ssl_context.set_verify(OpenSSL.SSL.VERIFY_PEER | OpenSSL.SSL.VERIFY_FAIL_IF_NO_PEER_CERT, lambda conn, ssl_sock, ssl_req,preverifyok: preverifyok)
					ssl_sock.set_connect_state()
					ssl_sock.setblocking(1)
					#ssl_sock.state_string()
					try:
						ssl_sock.do_handshake()
					except:
						self.result.warning("Unable to perform handshake on host %s (%s)", (host,ip))
						statusCounts[Plugin.STATUS_WARNING] += 1
						continue
					#ssl_sock.state_string()
					ssl_obj=ssl_sock.get_peer_certificate()
					ssl_subject=ssl_obj.get_subject()
					ssl_serial=ssl_obj.get_serial_number()
					ssl_cert_bits=ssl_obj.get_pubkey().bits()
					ssl_req=OpenSSL.crypto.X509Req()
					ssl_req.set_pubkey(ssl_obj.get_pubkey())
					ssl_pem=OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM,ssl_obj)
					res=""
					#retr = self.pluginResult.retr(pluginName, host, " DISTINCT ON (arg1) EXTRACT(EPOCH FROM created) as unixtime,arg1 ", "AND arg0 = 'serial' ORDER BY arg1,created")
					#cols = "DISTINCT ON (pr.value_text) EXTRACT(EPOCH FROM pr.created) as unixtime, pr.name, pr.value_text, pr.value_numeric, pr.table_id, pr.child_table_id"
					retr = self.pluginResult.verify_cert_load(pluginName, host)
					sorted_items = sorted(retr.items(), key=lambda x:x[1])
					for i in sorted_items:
						ssl_serial_last_time=i[0]
						ssl_serial_last_serial=i[1]
						res=i[1]
					if res and str(res) != str(ssl_serial):
						self.result.info("Last SSL serial (%s) does not match current (%s)",  (str(res),str(ssl_serial)))
					self.pluginResult.save(testId, pluginName, host, {"ssl_serial": ssl_serial })
					self.result.info("Serial: %s", str(ssl_serial))
					self.result.info("Bits: %s", str(ssl_cert_bits))
					self.result.info("Not Before: %s", str(self.conv_to_date(ssl_obj.get_notBefore())))
					self.result.info("Not After: %s", str(self.conv_to_date(ssl_obj.get_notAfter())))
					self.result.info("Country Name: %s",
							ssl_subject.countryName.encode('utf-8'))
					self.result.info("State Or Province Name: %s",
							ssl_subject.stateOrProvinceName.encode('utf-8'))
					self.result.info("Locality Name: %s",
							ssl_subject.localityName.encode('utf-8'))
					self.result.info("Organization Name: %s",
							ssl_subject.organizationName.encode('utf-8'))
					self.result.info("Organizational Unit Name: %s",
							ssl_subject.organizationalUnitName.encode('utf-8'))
					self.result.info("CommonName: %s",
							ssl_subject.commonName.encode('utf-8'))
					self.result.info("Email: %s",
							ssl_subject.emailAddress.encode('utf-8'))
					self.result.info("PEM:\n%s", ssl_pem)
					if ssl_serial_last_time <= (time.time() - max_ssl_cert_age):
						self.result.warning("Certificate on host %s (%s) has not been changed for over %s seconds", (host,ip,max_ssl_cert_age))
						statusCounts[Plugin.STATUS_WARNING] += 1
					if ssl_obj.has_expired() != 0:
						self.result.warning("Certificate on host %s (%s) has expired (%s)", (host,ip,self.conv_to_date(ssl_obj.get_notAfter())))
						statusCounts[Plugin.STATUS_WARNING] += 1
					elif time.time() >= (self.conv_to_unixtime(ssl_obj.get_notAfter()) - week):
						self.result.warning("Certificate on host %s (%s) expires within one week (%s)", (host,ip,self.conv_to_date(ssl_obj.get_notAfter())))
						statusCounts[Plugin.STATUS_WARNING] += 1
					elif time.time() >= (self.conv_to_unixtime(ssl_obj.get_notAfter()) - month):
						self.result.warning("Certificate on host %s (%s) expires within one month (%s)", (host,ip,self.conv_to_date(ssl_obj.get_notAfter())))
						statusCounts[Plugin.STATUS_WARNING] += 1
					elif time.time() <= self.conv_to_unixtime(ssl_obj.get_notBefore()):
						self.result.warning("Certificate on host %s (%s) is not valid before %s", (host,ip,self.conv_to_date(ssl_obj.get_notBefore())))
						statusCounts[Plugin.STATUS_WARNING] += 1
					elif ssl_cert_bits <= min_ssl_cert_bits:
						self.result.warning("Certificate on host %s (%s) is using few bits when encrypting (%s)", (host,ip,ssl_cert_bits))
						statusCounts[Plugin.STATUS_WARNING] += 1
					cmdarr1=["echo", ssl_pem] 
					p1=subprocess.Popen(cmdarr1, stdout=subprocess.PIPE)
					cmdarr2=["openssl", "verify"]
					p2=subprocess.Popen(cmdarr2, stdin=p1.stdout, stdout=subprocess.PIPE)
					output = p2.communicate()[0]
					output=re.sub("^stdin: ", "", output, 1)
					self.result.info("Certificate is valid:\n%s", (output))

				if row == (len(cmd[0]) - 1):
					exit_code=0

	
				if exit_code == 0 and row == (len(cmd[0]) - 1):
					self.result.info('Test on host %s:\n%s', (host, testlog))
				elif exit_code == 1 and row == (len(cmd[0]) - 1):
					self.result.warning('Test FAILED on %s:\n%s', (host, testlog), 'adv')
					statusCounts[Plugin.STATUS_WARNING] += 1
					failed=1
			self.result.info("Finished test for host %s (%s)", (host, ip))



		# Figure the final status of the test
		code = Plugin.STATUS_OK
		message = ''
		if statusCounts[Plugin.STATUS_WARNING] > 0 and statusCounts[Plugin.STATUS_WARNING] == len(results):
			code = Plugin.STATUS_ERROR
			self.result.error('All verifications of certificates failed!')
		elif statusCounts[Plugin.STATUS_WARNING] > 0 :
			code = Plugin.STATUS_WARNING

		self.result.extra('more info verifycert', type='adv')

		self.result.info('Finished certificates verification-test')
		self.result.setTestStatus(code)

	def conv_to_date(self,date):
		gentime = re.sub('Z$','', date)
		return datetime.datetime.fromtimestamp(time.mktime(time.strptime(gentime,"%Y%m%d%H%M%S")))

	def conv_to_unixtime(self, date):
		gentime = re.sub('Z$','', date)
		return time.mktime(time.strptime(gentime,"%Y%m%d%H%M%S"))
