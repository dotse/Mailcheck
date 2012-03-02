import adns
from re import match

from engine.plugins.common import *
from engine.plugins.Plugin import Plugin, Result, LiveFeedback

#
# NOTE: This test is both buggy and not up to date
#
class OpenRelay(Plugin):
	"""
	Checks if it's possible to relay on host
	"""

	def __init__(self):
		Plugin.__init__(self)
		self.requiredInput.append('MXRecord')
		self.category = 'SMTP'
	
	def run(self):
		pluginName = self.__class__.__name__
		testId = self.getInput('testId')
		email = self.getInput('email')
		mx = self.getInput('MXRecord')
		dns = adns.init()
		
		records = []
		raw = []
		resolves = []
		highestPrio = 0

		port = 25

		self.result.info('Started open relay test')

		failedTests = {}
		myhostname = socket.getfqdn()

		relayTestsCount = 0
		testnr = 1;
		nrMXRecords = len(mx[1]);
		for row in mx[1]:
			host = row[1]
			ip = row[2]
			type = row[3]

			failedTests[host] = []
			try:
				s = connect_to_host(host,port, type)
				data = s.recv(1024)
			except Exception, e:
				self.result.warning('Failed to connect to %s (%s)', (host,ip))
				continue
			
			self.result.info('Starting open relay tests against %s', host)
			
			mailfrom=[]
			mailrcpt=[]

			mailfrom.append("<spamtest@" + myhostname + ">")
			mailrcpt.append("<relaytest@" + myhostname + ">")
			mailfrom.append("<spamtest@" + myhostname + ">")
			mailrcpt.append("relaytest@" + myhostname + "")
			mailfrom.append("<spamtest>")
			mailrcpt.append("<relaytest@" + myhostname + ">")
			mailfrom.append("<>")
			mailrcpt.append("<relaytest@" + myhostname + ">")
			mailfrom.append("<spamtest@" + host + ">")
			mailrcpt.append("<relaytest@" + myhostname + ">")
			mailfrom.append("<spamtest@[" + ip + "]>")
			mailrcpt.append("<relaytest@" + myhostname + ">")
			mailfrom.append("<spamtest@" + host + ">")
			mailrcpt.append("<relaytest%" + myhostname + "@" + host + ">")
			mailfrom.append("<spamtest@" + host + ">")
			mailrcpt.append("<relaytest%" + myhostname + "@[" + ip + "]>")
			mailfrom.append("<spamtest@" + host + ">")
			mailrcpt.append("<\"relaytest@" + myhostname + "\">")
			mailfrom.append("<spamtest@" + host + ">")
			mailrcpt.append("<\"relaytest%" + myhostname + "\">")
			mailfrom.append("<spamtest@" + host + ">")
			mailrcpt.append("<relaytest@" + myhostname + "@" + host + ">")
			mailfrom.append("<spamtest@" + host + ">")
			mailrcpt.append("<\"relaytest@" + myhostname + "\"@" + host + ">")
			mailfrom.append("<spamtest@" + host + ">")
			mailrcpt.append("<relaytest@" + myhostname + "@[" + ip + "]>")
			mailfrom.append("<spamtest@" + host + ">")
			mailrcpt.append("<@" + host + ":relaytest@" + myhostname + ">")
			mailfrom.append("<spamtest@" + host + ">")
			mailrcpt.append("<@[" + ip + "]:relaytest@" + myhostname + ">")
			mailfrom.append("<spamtest@" + host + ">")
			mailrcpt.append("<" + myhostname + "!relaytest>")
			mailfrom.append("<spamtest@" + host + ">")
			mailrcpt.append("<" + myhostname + "!relaytest@" + host + ">")
			mailfrom.append("<spamtest@" + host + ">")
			mailrcpt.append("<" + myhostname + "!relaytest@[" + ip + "]>")
			mailfrom.append("<spamtest@" + host + ">")
			mailrcpt.append("<relaytest%[" + myhostname + "]@>")
			mailfrom.append("<spamtest@" + host + ">")
			mailrcpt.append("<relaytest@[" + myhostname + "]@>")
			relayTestsCount = len(mailfrom)

			try:
				result
			except:
				result=[]

			for testno in range(len(mailfrom)):
				self.livefeedback.message(testId, '%s, running subtest %s of %s on server %s (%s/%s)', (pluginName, (testno + 1), len(mailfrom), host, testnr, nrMXRecords))
				test=[
					[
						'HELO ' + host + '\r\n',
						'RSET\r\n',
						'MAIL FROM: ' + mailfrom[testno] + '\r\n',
						'RCPT TO: ' + mailrcpt[testno] + '\r\n'
					], [
						'250',
						'250 2.0.0 Ok|250 2.1.5 Flushed.*',
						'250 2.1.0 Ok',
						'250 2.1.0 Ok'
					], [
						'554.*|501.*|503.*|553.*|550.*|555.*|401.*|454.*'
					]
				]

				testlog=""

				for row in range(len(test[1])):
					exit_code=int()
					send=test[0][row]
					recv=test[1][row]
					
					try:		
						s.send(send)
					except Exception, e:
						if e[0] == 104:
							self.result.info("Warning connection reset by peer..")
						if e[0] == 32:
							self.result.info("Warning broken pipe, aborting subtest..")
							s = connect_to_host(host, port, type)
							#continue
					testlog += ">>> " + send

					try:		
						data = s.recv(1024)
					except Exception, e:
						if e[0] == 104:
							self.result.info("Warning connection reset by peer..")
						if e[0] == 32:
							#self.result.info("Warning broken pipe, aborting subtest..")
							s = connect_to_host(host, port, type)
							#continue

					testlog += "<<< " + data

					if not match(recv, data):
						if not match(test[2][0], data):
							exit_code=1
					elif row == (len(test[0]) - 1):
						exit_code=0

		
					if exit_code == 0 and row == (len(test[0]) - 1):
						self.result.info('Test %s on host %s:\n%s', ((testno + 1), host, testlog))
					elif exit_code == 1 and row == (len(test[0]) - 1):
						self.result.warning('Test %s FAILED on %s:\n%s', ((testno + 1), host, testlog), 'adv')
						failedTests[host].append(testno+1)
						failed=1
			testnr = (testnr+1);

			self.result.info('Finished open relay testing on %s', host)

		# Figure out final plugin status
		code = Plugin.STATUS_OK
		for h in failedTests:
			l = len(failedTests[h])
			if l == relayTestsCount:
				code = Plugin.STATUS_ERROR
				self.result.error('All %s open relay tests against %s failed', (relayTestsCount, h))
			elif l > 0:
				if code < Plugin.STATUS_WARNING:
					code = Plugin.STATUS_WARNING
				if l == 1:
					self.result.warning('One of %s open relay test against %s failed', (relayTestsCount, h))
				else:
					self.result.warning('%s of %s open relay tests against %s failed', (l, relayTestsCount, h))
		
		self.result.info('Finished open relay test')
		
		# Set final status
		self.result.setOutput([])
		self.result.setTestStatus(code)
		


def test():
	data = [
		['20', 'lonn.org', '213.136.43.225', 'INET'],
	]
	a = OpenRelay()
	a.setInput('email', 'email@gatorhole.com')
	a.setInput('MXRecord', data)
	r = runTestPlugin(a, 'gatorhole.com')
	print r


if __name__ == '__main__':
	test()
