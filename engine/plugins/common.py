
import socket
import dns.resolver


def get_ipv_type(host, type="INET6"):
	"""
	Resolve host into IPv4/v6 address
	@param host:	Hostname
	@param type:	'INET' for IPv4 or 'INET6' for IPv6 address.
	@return:		Tuple with format "([host, type, ip])". Empty list is returned if no server is found.
	"""
	ipaddr=None
	try:
		if type == "INET6":
			addr=socket.getaddrinfo(host, None, socket.AF_INET6)
			ipaddr = addr[0][4][0]
		else:
			try:
				addr=socket.getaddrinfo(host, None, socket.AF_INET)
				ipaddr = addr[0][4][0]
			except:
				pass
		ret = ([host, type, ipaddr])

	except socket.error, e :
		try:
			addr=socket.getaddrinfo(host, None, socket.AF_INET)
			ret = ([host, "INET", addr[0][4][0]])
		except socket.error, e :
			ret = []
        
	return ret


def get_name_servers(domain):
	"""
	Get name servers for a domain
	@param domain:		Domain to query for name servers.
	@return:			List with name servers.
	"""
	nameservers = None
	try:
		nameservers = dns.resolver.query(domain, 'ns')
	except:
		pass

	servers = []
	if nameservers == None:
		return servers

	for n in nameservers.rrset:
		nsHost = n.to_text()[0:-1]
		ipv4 = resolveHost(nsHost, 'INET')
		ipv6 = resolveHost(nsHost, 'INET6')

		if ipv4 != None:
			servers.append( (nsHost, ipv4, 'INET') )
		if ipv6 != None:
			servers.append( (nsHost, ipv6, 'INET6') )
	return servers


def resolveHost(host, type='INET'):
	"""
	Resolve a host into a IPv4 or IPv6 address
	@param host:	Host to resolve
	@param type:	'INET' for IPv4 or 'INET6' for IPv6 address.
	@return:		IPv address.
	"""
	addr = None
	stype = socket.AF_INET

	if type.lower() != 'inet':
		stype = socket.AF_INET6

	try:
		addr = socket.getaddrinfo(host, None, stype)
		addr = addr[0][4][0]
	except:
		return None
	return addr

def ipv_type_to_a_type(type):
	"""
	Get A or AAAA depending on the IPv-type
	@param type:	'INET' for IPv4 or 'INET6' for IPv6 address.
	@return:		String 'A' or 'AAAA'
	"""
	if type.lower() == 'inet':
		return 'A'
	return 'AAAA'


def get_arecord(host, type='INET', nameservers=None):
	"""
	Get the A or AAAA record for the provided host
	@param host:		Host to query
	@param type:		'INET' for IPv4 or 'INET6' for IPv6 address.
	@param nameservers: List with IP to a name server for direct query.
	@return:			List with A/AAAA records
	"""

	a = ipv_type_to_a_type(type)

	resolve = dns.resolver.Resolver()
	if nameservers is not None:
		resolve.nameservers = nameservers
	
	records = []
	try:
		answers = resolve.query(host, a)
		for a in answers.rrset:
			records.append(a.address)
	except:
		pass

	return records


def connect_to_host(host, port, type, plugin):
	"""
	Connect to a host using the simple connection pool
	@param host:	Target
	@param port:	Port we're connecting to
	@param type:	'INET' for IPv4 or 'INET6' for IPv6 address.
	@param plugin:	Plugin opening the connection
	@return:		Socket with the connection
	@raise Exception:	Raised if connection failed.
	"""

	s = None
	for i in plugin.pluginSockets.retr_sock():
		string=(host, port)
		if ((host, port) == i.getpeername()):
			return i
	try:
		if type == 'INET6':
			s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
		else:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.settimeout(15)
		s.connect((host, port))
	except Exception, e:
		raise Exception(e)
	return s



def runTestPlugin(plugin, domain, email=None):
	"""
	Function for testing plugins. A fake testing environment is setup to allow plugins to run
	without the testrunner.
	@param plugin:		Plugin instance to test
	@param domain:		Domain invloved in the test
	@param email:		Email starting the test
	@return:			Plugin result
	"""
	import sys
	from os.path import dirname
	from engine.database import Database
	from engine.plugins.Plugin import PluginConfig, PluginResult, Result, LiveFeedback, PluginSockets 

	d = Database(configFile=dirname(sys.path[0]) + "/../config/config.ini")
	d.connect()
	pc = PluginConfig(d)
	pr = PluginResult(d)
	lf = LiveFeedback(None)
	ps = PluginSockets()

	if email != None:
		plugin.setInput('email', email)
	
	plugin.setInput('domain', domain)
	plugin.setInput('testId', 1337)
	plugin.pluginConfig = pc
	plugin.pluginResult = pr
	plugin.livefeedback = lf
	plugin.pluginSockets = ps
	
	plugin.setResult( Result(plugin) )
	plugin.run()
	return plugin.getResult()
	#return (d, plugin.getResult())
