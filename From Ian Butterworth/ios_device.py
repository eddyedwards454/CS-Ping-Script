# IOS device - ssh or telnet connection to IOS host
# v2.9 
# v2.8 11-07-2022	Interfaces, VLans updated. Added DHCPPools. Improved ip access-lists.
# v2.7 10-06-2022	Interface.Ports() fix for vlan interfaces. Added more interface abbrevs.
# v2.6 19-05-2022	OSPFNeighbors now moved to ios_router module. Replaced CDPNeighbors.
# v2.5 31-03-2022	Added OSPFNeighbors
# v2.4 24-09-2021	Added FileSystems
# v2.3 13-04-2021	Added generic components
# v2.2 03-03-2021	Updated for netmiko
# v2.1 04-06-2020	ShowEnable added
# v2.0 01-02-2019	Sub-classed from generic_device library, 

# Vz Libraries
import generic_device
from slice_split import Splitter
# standard libraries
import re, subprocess, os.path, datetime, time

class Feature(object):
	def __init__(self, name, cmd, sec = ''):										# Feature('OSPF', 'router ospf')   Feature('CME-SCCP', 'ip source-address', 'telephony-service')
		self.Name = name															# feature name
		self.Section = sec															# config section
		self.Command = cmd															# defining command (regex)
		
# end class

# IOS Features
IOSFeatures = [Feature('BGP', 'router bgp'), Feature('OSPF', 'router ospf'), Feature('EIGRP', 'router eigrp'), Feature('ISIS', 'router isis'), Feature('RIP', 'router rip'),
 Feature('CME-SCCP', 'ip source-address', 'telephony-service'), Feature('CME-SIP', 'source-address', 'voice register global'), Feature('SRST','ip source-address', 'call-manager-fallback'), Feature('SCCP', 'sccp '), Feature('MGCP', 'mgcp call-agent'),
 Feature('Gatekeeper', 'zone (local|remote|prefix)'), Feature('Wireless AP', 'dot11 ssid'), Feature('Bridge', 'bridge-group'), Feature('NAT', 'ip nat '), Feature('Voice Gateway', 'dial-peer voice'), Feature('CUBE','mode border-element', 'voice service voip')]

class IOSDevice(generic_device.GenericDevice):
	def __init__(self, host = '', user = '', pw = '', enablepw = '', ping = True, port = 22, entity = None, creduser = '', debug = False, logging = False, dummy = False):							# define an IOS Device
		generic_device.GenericDevice.__init__(self, host = host, user = user, pw = pw, enablepw = enablepw, ping = ping, port = port, entity = entity, creduser = creduser, debug = debug, logging = logging, dummy = dummy)
		# overridden parameters
		self.ResponseClass = IOSResponse
		self.standardcmds = dict(getInfo = 'show version', reload = 'reload', getConfig = 'show running', getItemConfig = 'show run | sec ', saveConfig = 'copy running startup', getInterfaces = 'show ip int brief',
			deleteInterface = 'no interface ')
		self.fails = ['Line has invalid autocommand', 'Invalid input', 'Permission denied', 'Authentication failed', 'Ambiguous command']			# list of failure responses
		self.DeviceType = 'cisco_ios'																	# netmiko device type
		
		# additional parameters
		self.ShowEnable = False																			# require Enable mode for show commands
		#  components
		self.Interfaces = IOSInterfaces(self)
		self.Configuration = IOSConfiguration(self)
		self.VLANs = VLANs(self)
		self.DeviceInfo = IOSDeviceInfo(self)
		self.Lines = Lines(self)																		# lines - con, aux, vty...
		self.Controllers = Controllers(self, 'E1')														# E1, T1 etc.
		self.Inventory = Inventory(self)	
		self.CDPNeighbors = CDPNeighbors(self)
		self.Licenses = Licenses(self)
		self.LogMessages = LogMessages(self)
		self.AccessLists = AccessLists(self)
		self.FileSystems = IOSFileSystems(self)
		self.IPAccessLists = IPAccessLists(self)
		# generic components - quickly added. May add more specific items later....
		#self.IPAccessLists = IOSComponentCollection(self, 'ip access-list', id = 'ip access-list \w+ (\S+)', itemtype = 'ip access-list (\w+)', reglist = [{'all':'Lines','reg':'(\d+) (\w+) (.*)'}])
		self.ClassMaps = IOSComponentCollection(self, 'class-map', id = 'class-map \S+ (\S+)', itemtype = 'class-map (\S+)')
		self.PolicyMaps = IOSComponentCollection(self, 'policy-map', id = 'policy-map (\S+)', itemtype = 'policy-map (\S+)')
		self.RoutingProtocols = IOSComponentCollection(self, 'router', id = 'router \S+ (\S+)', itemtype = 'router (\S+)')
		self.RouteMaps = IOSComponentCollection(self, 'route-map', id = 'route-map (\S+)')
		self.CryptoServices = IOSComponentCollection(self, 'crypto', id = 'crypto \S+ \S+ (\S+)', itemtype = 'crypto (\S+ \S+)')
		self.DHCPPools = IOSComponentCollection(self, 'ip dhcp pool', id = 'ip dhcp pool (\S+)', reglist = [{'attr':'domain-name','reg':'domain-name (\S+)'},{'attr':'network','reg':'network (\S+)'},{'attr':'mask','reg':'network \S+ (\S+)'},
			{'attr':'dns-server','reg':'dns-server (.*)'},{'attr':'lease','reg':'lease (\S+)'},{'attr':'default-router','reg':'default-router (\S+)'},{'all':'options','reg':'option (\d+) (.*)'}])
		# services - things like aaa,snmp-server,logging,ntp,ip route, etc...
		self.Services = Services(self)
		self.ROMMonitor = ROMMonitor(self)

	def Reload(self, option = '', time = ''):															# .Reload(), .Reload('at', '12:30'), .Reload('cancel'), .Reload(yesno = 'no')
		cmdtext = 'reload'
		if option in ['at', 'in', 'cancel']:
			cmdtext += ' ' + option
		if time:
			cmdtext += ' ' + time
			
		res = self.Command(cmdtext, enable = True, prompts = {'[confirm]':'y'}, ignoreexception = True if option == '' else False)
		if 'reload' in res.output:
			res.Status = True																			# override status if it actually reloads. Socket error will cause it to fail, but that is expected.
		
		return res.Status
		
# end class	

class IOSResponse(generic_device.GenericResponse):
	def __init__(self, dev, status = False, text = '', command = '', error = ''):
		generic_device.GenericResponse.__init__(self, dev = dev, status = status, text = text, command = command, error = error)
	
	def __repr__(self):
		return ('IOSResponse: Status:' + str(self.Status))

	def findFails(self):
		arr = self.output.splitlines()
		for i, line in enumerate(arr):
			if '% Invalid input' in line:							# if we find the % Invalid  or % Incomplete message
				if i >= 2:	
					failedline = arr[i - 2]
					self.FailedLines.append('%s: %s'%('Invalid', failedline.split('#')[1] if '#' in failedline else failedline ))						# save the line two above
					self.Status = False
			elif '% Incomplete ' in line:
				if i >= 1:
					failedline = arr[i - 1]
					self.FailedLines.append('%s: %s'%('Incomplete', failedline.split('#')[1] if '#' in failedline else failedline ))					# 'Incomplete: ip cef'
					self.Status = False
			elif '% Ambiguous command:' in line:
				self.FailedLines.append('%s: %s'%('Ambiguous', line.split(':')[1]))
				self.Status = False
			elif '% Bad' in line:
				self.FailedLines.append('%s: %s'%('Unknown', line))
				self.Status = False
# end class

class IOSDeviceInfo(generic_device.GenericDeviceInfo):											# class to hold ios verison information
	def __init__(self, vertext):
		generic_device.GenericDeviceInfo.__init__(self, vertext)

		# Cisco 877 (MPC8272) processor (revision 0x200) with 118784K/12288K bytes of memory.
		# Cisco 2851 (revision 53.51) with 512000K/12288K bytes of memory
		# Cisco C891F-K9 (revision 1.0) with 488524K/35763K bytes of memory.
		# cisco WS-C3850-12X48U (MIPS) processor with 4194304K bytes of physical memory.
		# Cisco CISCO3945-CHASSIS (revision 1.0) with C3900-SPE150/K9 with 980992K/67584K bytes of memory.
		# cisco AIR-AP1242AG-E-K9    (PowerPCElvis) processor (revision A0) with 24566K/8192K bytes of memory
		# cisco WS-C4900M (MPC8548) processor (revision 2) with 1048576K bytes of memory.
		# template {'attr':'','reg':''}
		self.reglist = [{'attr':'Hostname','reg':'(\S+) uptime is '},{'attr':'Uptime','reg':' uptime is (.*)\s'},{'attr':'Serial','reg':'Processor board ID (\S+)'},{'attr':'Confreg','reg':'Configuration register is (\S+)'},
					{'attr':'Reload','reg':'System returned to ROM by (\S+)'}, {'attr':'Version','reg':', Version ([^,\s]+)'}, {'attr':'Featureset','reg':'\((\S+)\),'},
					{'attr':'Model','reg':'[Cc]isco (\S+)\s+\S+ processor'}, {'attr':'Model','reg':'[Cc]isco (C?(ISCO)?\S+) \(revision'},{'attr':'Platform','reg':'Cisco IOS Software, (.*) Software'},
					{'attr':'Platform','reg':'Cisco IOS Software\s?(?:\[\w+\])?, (.*) Software'},{'attr':'Image','reg':'System image file is "(\S+)"'},
					{'attr':'CPU','reg':'[Cc]isco \S+\s+\((\S+)\) processor'},{'attr':'Revision','reg':'\(revision (\S+)\)'}, {'attr':'Bootstrap','reg':'Bootstrap, Version ([^, ]+)'},
					{'attr':'Flash', 'reg':'(\d+)K bytes of .*lash'}, {'attr':'Memory', 'reg':'with (\d+)K/?(\d+)?K? bytes'}, {'attr':'Nexus','reg':'(Cisco Nexus Operating System)'},
					{'all':'Interfaces','reg':'(\d+) (.*) interfaces'}]

# end class	

class IOSConfiguration(generic_device.GenericConfiguration):									# can be used as standalone class for parsing IOS config
	def __init__(self, dev = None, text = '', file = ''):
		generic_device.GenericConfiguration.__init__(self, dev)
		self.commands = dict(GetCommand = 'show configuration', GetItem = '', save = 'write memory')
		self.Features = []
		if file:
			self.Import(filename = file)
		
		if text:
			self.fromText(text)

	def fromText(self, text):
		# import, sanitise and filter a configuration													
		self.Text = re.sub(' --More--\s{9}', '', text)							# remove anything added by putty
		c = re.findall('\r\n', self.Text)
		if len(c) > 0:
			self.Text = self.Text.replace('\r\n','\n')							# try different line endings
		splits = re.split('!\n', self.Text)										# split config into sections - relies on ! being correct
		#self.Sections = filter(bool, splits)									
		self.Sections = [s for s in splits if len(s) > 0]						# filter out anything blank
	
	def Section(self, keyword):													# e.g conf.Section('dial-peer voice')
		# return section(s) of config matching keyword
		secs =  [s for s in self.Sections if s.startswith(keyword)]
		ret = []
		for s in secs:
			res = s.split('\n' + keyword)										# e.g \nvoice class  or 'line' sections (con, aux, vty)   --- IOS misses out !
			if len(res) > 1:
				for i, r in enumerate(res):
					if i:
						ret.append(keyword + r)									# split removes the keyword
					else:
						ret.append(r)											# except for first one
			else:
				ret.append(s)
		return ret
	
	def GetItems(self, itemname, filter = '', sp = 'tag', itemtype = ''):					# .GetItems('dial-peer', itemtype = '(pots|voip)')  .GetItems('interface', sp = 'interface (\S+)')
		coll = ComponentCollection(name = itemname, dev = self.Device, sp = 'Tag' if sp == 'tag' else 'Name')		# create a new collection linked to device     def __init__(self, name, dev = None, sp = 'Name'):	
		confs = self.Section(itemname)
		for conf in confs:
			if not filter or filter in conf:
				m1 = None
				if sp == 'tag':	
					m1 = re.search('(\d+)', conf)								# look for tag
				elif sp == 'name':
					m1 = re.search(itemname + ' (\S+)', conf)					# look for name e.g. .GetItems('interface', 'name')  =>  'interface Ethernet99' 
				else:
					m1 = re.search(sp, conf)									# e.g. .GetItems('controller, sp = 'controller [ET]1 (\S+)', itemtype = '([ET]1)')
				
				itype = ''														
				if m1 is not None:
					if itemtype:
						m2 = re.search(itemtype, conf)							# look for item type e.g. voip or pots for dial-peer
						if m2 is not None:
							itype = m2.group(1)
					#print(f'sp:{m1.group(1)} type:{itype}')
					newitem = coll.Add( m1.group(1), type = itype, config = conf)				# def Add(self, sp, type = '', config = '', unique = True):	
		
		# end for
		return coll
		
	def GetFeatures(self):											
		# look for a feature in the config
		for f in IOSFeatures:
			if f.Section:
				secs = self.Section(f.Section)						# get the section(s)
				for s in secs:
					m = re.search(f.Command, s)						# look for the command in the section
					if m is not None:
						self.Features.append(f.Name)
						break										# avoid multiple appends of the same feature		
			else:
				m = re.search(f.Command, self.Text)					# look for the command in full config
				if m is not None:
					self.Features.append(f.Name)
					
	def StartsWith(self, keyword):														# all lines starting with '<keyword>' or 'no <keyword>'
		pattern = f'^((?:no )?{keyword} .*)'											# (?:  - non-capture group 
		m = re.findall(pattern, self.Text, re.MULTILINE)		
		return m
		
	def ForceSections(self, starttext):													# forced sections - when sections are not delimited by ! 
		sections = []
		lines = self.Text.splitlines()
		matches = [(i,l) for (i,l) in enumerate(lines) if l.startswith(starttext)]		# index of lines starting ..... 
		i = 1
		for sti,txt in matches:															# (1387, 'ip access-list standard Cust_SNMP')
			s = [txt]
			while(1):
				nextline = lines[sti + i]
				if nextline.startswith(' '):											# ' 10 remark .....' ' 20 permit ......'
					s.append(nextline)
					i += 1
				else:
					sections.append('\n'.join(s))
					i = 1
					break
		return sections
		
# end class

class IOSInterfaces(generic_device.GenericInterfaces):
	def __init__(self, device):
		generic_device.GenericInterfaces.__init__(self, device)
		self.ComponentClass = IOSInterface
		#self.reglist = [{'attr':'Name','reg':'interface (.*)'}, {'attr':'AdminStatus','reg':'shutdown','res':True}, {'attr':'Description', 'reg':'description (.*)'}]
		self.reglist = [{'attr':'description','reg':'description (.*)'},{'attr':'cdp','reg':'((?:no )?cdp enable)'},{'attr':'shutdown','reg':'((?:no )?shutdown)'},{'all':'iphelpers','reg':'ip helper-address (\S+)'},{'all':'access-groups','reg':'ip access-group (\S+) (\S+)'},
			{'all':'switchport','reg':'((?:no )?switchport .*)'}, {'all':'spanning-tree','reg':'((?:no )?spanning-tree .*)'}]
		self.abbrevs = {'Se':'Serial','Te':'TenGigabitEthernet','Gi':'GigabitEthernet','Fa':'FastEthernet','Tw':'TwoGigabitEthernet', 'Tf':'TwentyFiveGigabitEthernet','TwentyFiveGigE':'TwentyFiveGigabitEthernet',
				'Fo':'FortyGigabitEthernet','Fi':'FiftyGigabitEthernet','Hu':'HundredGigabitEthernet','Th':'TwoHundredGigabitEthernet','Ap':'AppGigabitEthernet','Po':'Port-Channel', 'Eth':'Ethernet'}					# abbreviated interface names
	
	def Status(self):
		intresp = self.Device.Command('show ip interface brief')							# GigabitEthernet2       unassigned      YES NVRAM  administratively down down
		for line in intresp.output.splitlines():				
			arr = line.split()																# split into words			
			if len(arr) > 5:																# ignore any line with less than x words
				if arr[0] not in ['Interface','IP','show']:									# ignore the first line(s)
					name = self.abbrevs.get(arr[0], arr[0])									# get the full interface name
					newint = False
					intf = self.Add(arr[0])													# find the interface, or create new
					intf.Parameters['IP'] = arr[1]
					intf.Parameters['Method'] = arr[3]
					if len(arr) == 7:
						intf.Parameters['AdminStatus'] = arr[4] + ' ' + arr[5]
						intf.Parameters['OperStatus'] = arr[6]
					elif len(arr) == 6:
						intf.Parameters['OperStatus'] = arr[5]

		return len(self.Components)
		
	def Get(self):
		intconfs = self.Device.Configuration.Section('interface')
		for intf in intconfs:
			m = re.search('interface (\S+)', intf)
			if m is not None:
				i = self.Add(m.group(1), type = '', config = intf)							# add new, or retrieve existing!      def Add(self, sp, type = '', config = '', unique = True):		c = self.ComponentClass(self, sp, type, config)		
				
		return len(self.Components)
		
	def FullName(self, shortname):															# reconcile a short name to a full interface name
		m = re.match('(\w+)\s?([\d/\.]+)', shortname)
		if m is not None:
			fullname = self.abbrevs.get(m.group(1), None)									# lookup full name e.g. Tw => TwoGigabitEthernet
			if fullname is None:															# no change
				fullname = next((v for v in self.abbrevs.values() if v.startswith(m.group(1))), m.group(1))			# try a longer match e.g. Gig => GigabitEthernet
				
			if fullname is not None:
				return f'{fullname}{m.group(2)}'
			
		return shortname
# end class

class IOSInterface(generic_device.GenericInterface):														# Component.__init__(self, coll, sp = name, config = config)
	def __init__(self, coll, name, type = '', config = ''):
		generic_device.GenericInterface.__init__(self, coll = coll, name = name, config = config)
		# override parameters
		self.commands = dict(disable = 'shutdown', enable = 'no shutdown', remove = 'no interface %s', configure = 'interface %s\n')
		self.IPAddresses = []
		
	def parseName(self):
		vtypes = ['BDI','BVI','Dialer','Loopback','Null','NVI','Port-Channel','SVI','Tunnel','Vlan','VPN']		# virtual interface types
		
		m = re.match('(Dot11Radio|[a-zA-Z\-]+)(\S+)', self.SPValue)												# split name into type and port
		if m is not None:
			self.Parameters['Type'] = m.group(1)

			for k, v in self.Collection.abbrevs.items():
				if m.group(1) == k:
					self.Parameters['Type'] = v
					self.Parameters['Name'] = self.SPValue.replace(k, v)										# expand the abbreviation
					self.SPValue = self.Parameters['Name']
				
			if self.Param('Type') in vtypes or self.Param('Type').startswith('Virtual'):
				self.Parameters['Physical'] = False
			ps = m.group(2)														# port/slot/sub info
			self.Parameters['ID'] = ps
			if '.' in ps:														# sub-interface
				self.Parameters['SubInterface'] = ps.split('.')[1]
				ps = ps.split('.')[0]
				self.Parameters['Physical'] = False
			if ':' in ps:														# isdn B/D channel 	e.g. Serial0/0/1:15
				self.Parameters['Channel'] = ps.split(':')[1]
				ps = ps.split(':')[0]
				self.Parameters['Physical'] = False
			
			if '/' in ps:
				arr = ps.split('/')
				self.Parameters['Port'] = arr[-1]												# port is always the last	0/1/2, 0/1
				self.Parameters['Slot'] = arr[0]												# slot is always first		
				if len(arr) == 3:
					self.Parameters['SubSlot'] = arr[1]											# subslot in middle			e.g. 0/1/2
			elif ps.isdigit():
				self.Parameters['Port'] = ps													# just digits, no port/slots   e.g. ATM0		
		
	def GetIPAddresses(self):		
		matches = re.findall('ip address (\S+) ?(\S+)? ?(\w+)?', self.Config)					# find all ip addresses - list of tuples
		for m in matches:
			if re.match('[\d\.]+', m[0]):
				ip = ip_interface('%s/%s'%(m[0],m[1]))
				
				ifound = next((i for i in self.IPAddresses if str(i.ip) == m[0]), None)			# see if the address already exists (e.g. from show ip int brief)
				if ifound is not None:
					self.IPAddresses.remove(ifound)												# remove it - it will be replaced next
				self.IPAddresses.append(ip)
		
		matches = re.findall('(standby|vrrp) \d+ ip (\S+)', self.Config)					# look for hsrp/vrrp ip addresses
		for m in matches:
			ip = ip_interface('%s/%s'%(m[0],m[1]))
			ifound = next((i for i in self.IPAddresses if str(i.ip) == m[0]), None)			# see if the address already exists (e.g. from show ip int brief)
			if ifound is not None:
				self.IPAddresses.remove(ifound)												# remove it - it will be replaced next
			self.IPAddresses.append(ip)
			
	def Detail(self):
		res = self.Collection.Device.Command(f'show interface {self.SPValue}')
		reglist = [{'attr':'line protocol','reg':'line protocol is (\w+)'},{'attr':'Hardware','reg':' Hardware is (\S+)'},{'attr':'macaddress','reg':'address is (\S+)'},{'attr':'IPAddress','reg':'Internet address is (\S+)'},
			{'attr':'Duplex','reg':'(\w+) Duplex,'},{'attr':'Speed','reg':',(\d+\w+),'},{'attr':'MTU','reg':' MTU (\d+) bytes'}]
		for r in reglist:
			m = re.search(r.get('reg'), res.output)
			if m is not None:
				self.Set(r.get('attr'),m.group(1))
		
		members = re.findall(' Member (\d+) : (\S+) , (\S+), (\S+)', res.output)			#  Member 0 : GigabitEthernet0/2 , Full-duplex, 1000Mb/s      (port-channel etc.)
		if len(members) > 0:
			self.Set('members', members)
		
	def Protocols(self):
		res = self.Collection.Device.Command(f'show interface {self.SPValue} counters protocol status')
		m = re.search(f'{self.SPValue}: (.*)', res.output)
		if m is not None:
			return m.group(1).split(', ')
			
	def Ports(self):																		# get ports for vlan interfaces
		ports = []
		cmd = 'show spanning-tree '
		cmd += f'vlan {self.Param("Port")}' if self.Param('Type') == 'Vlan' else 'interface ' + self.SPValue
		res = self.Collection.Device.Command(cmd)
		matches = re.findall('Port (\d+) \((\S+)\)', res.output)
		if matches is None:
			olines = res.output.splitlines()
			idx = next((i for i,l in enumerate(olines) if l.startswith('------------------')), 0)
			if idx > 0:
				titles = olines[idx -1].split()														# Interface           Role Sts Cost      Prio.Nbr Type
				for l in olines[idx + 1:]:
					ports.append(l.split(maxsplit = len(titles) - 1))								# Gi1/14              Root FWD 19        128.14   P2p Peer(STP) 
		else:
			ports = matches
		return ports
			
# end class

class Lines(generic_device.ComponentCollection):
	def __init__(self, device):
		generic_device.ComponentCollection.__init__(self, 'Lines', device)
		self.SignificantProperty = 'Start'
		self.ComponentName = 'Line'
		self.ComponentClass = Line
		self.reglist = [{'attr':'ACL','reg':'access-class (\S+) in'}, {'attr':'Transport','reg':'transport input (\w+)'}]

	def Status(self, type, start):															# get a component
		pass
		
	def Get(self):
		lineconf = self.Device.Configuration.Section('line')
		if lineconf == []:
			return 0
		
		for ln in lineconf:
			m = re.search('line (\w+) (\d+) ?(\d+)?', ln)									# line vty 0 4
			if m is not None:
				l = self.Add(m.group(1), m.group(2), '' if m.group(3) is None else m.group(3), ln)
				
		return len(self)
		
	def Add(self, type, start, end, config = ''):											# create a new object
		c = self[type, start]																# check if exists
		if c is None:	
			c = Line(self, type, start, end, config)		
			self.Components.append(c)
		else:
			c.ParseConfig(config)
		return c
		
# end class

class Line(generic_device.Component):
	def __init__(self, coll, type, start = '0', end = '', config = ''):
		generic_device.Component.__init__(self, coll = coll, sp = start, type = type, config = config)
		self.Parameters['Start'] = start
		self.Parameters['End'] = end

	def __repr__(self):
		return('Line %s %s %s'%(self.Type, self.Param('Start'), self.Param('End')))
		
# end class

class Controllers(generic_device.ComponentCollection):
	def __init__(self, device, type):
		generic_device.ComponentCollection.__init__(self, 'Controllers', device)
		self.SignificantProperty = 'ID'
		self.ComponentName = 'Controller E1'
		self.ComponentClass = Controller
		self.Type = type														# must be E1, T1, T3 etc.
		self.reglist = [{'attr':'framing','reg':'framing (\S+)'},{'attr':'clock source','reg':'clock source (.*)'},{'attr':'Description','reg':'description (.*)'},
				{'attr':'AdminStatus','reg':'shutdown', 'res':True}, {'attr':'pri-group','reg':'pri-group timeslots (\S+)'}]
		
	def Status(self):
		cmdtext = 'show controller ' + self.Type		
		resp = self.Device.Command(cmdtext)
		if resp.Status:
			splits = re.split('\n%s '%(self.Type), resp.output)
			for s in splits:
				m2 = re.search('([\d/]+) is (.*)\.', s)							# E1 0/1/3 is down.
				if m2 is None:
					continue
				ct = self.Add(self.Type, m2.group(1))
				if m2.group(2) == 'administratively down':
					ct.Parameters['AdminStatus'] = 'down'
					ct.Parameters['OperStatus'] = 'down'
				else:
					ct.Parameters['AdminStatus'] = 'up'
					ct.Parameters['OperStatus'] = m2.group(2)
					
				m3 = re.findall('(Transmitter .*|Receiver .*)', s)
				if m3 is not None:
					self.Alarms = m3
			
				m4 = re.search('Framing is (\S+), Line Code is (\S+), Clock Source is (\S+)', s)
				if m4 is not None:
					ct.Parameters['Framing'] = m4.group(1)
					ct.Parameters['LineCode'] = m4.group(2)
					ct.Parameters['ClockSource'] = m4.group(3)
			
				m5 = re.findall('(\d+) ([\w ]+)[,\n]', s)
				if m5 is not None:
					ct.Parameters['CurrentData'] = m5[0:9]
					ct.Parameters['TotalData'] = m5[10:]
				
		return len(self)
		
	def Get(self):
		ctrls = self.Device.Configuration.Section('controller %s'%(self.Type))
		for ctrl in ctrls:
			m = re.search('controller \S+ (\S+)', ctrl)
			if m is not None:
				c = self.Add(self.Type, m.group(1), ctrl)
		
		return len(self)
		
	def Add(self, type, id, config = ''):								# create a new object
		c = self[id]													# check if exists
		if c is None:	
			c = Controller(self, type, id, config)		
			self.Components.append(c)
		else:
			c.ParseConfig(config)
		return c
# end class

class Controller(generic_device.Component):
	def __init__(self, coll, type, id = '', config = ''):
		generic_device.Component.__init__(self, coll = coll, sp = id, config = config, reglist = reglist)
		self.Parameters['Type'] = type
		self.commands = dict(disable = 'shutdown', enable = 'no shutdown', remove = '', configure = 'controller ' + self.Param('Type') + ' %s\n')
		
	def __repr__(self):
		return('Controller %s %s'%(self.Param('Type'), self.Param('ID')))
		
# end class

class Inventory(generic_device.ComponentCollection):
	def __init__(self, device):
		generic_device.ComponentCollection.__init__(self, 'Inventory', device)
		self.SignificantProperty = 'ProductID'
		self.ComponentName = 'InventoryItem'
		self.ComponentClass = InventoryItem
	
	def Status(self):
		self.Clear()
		invresp = self.Device.Command('show inventory')
		if invresp.Status:
			splits = invresp.output.split('\n\n')													# more reliable to split text then search for items
			for s in splits:
				rlist = ['NAME: "([^"]*)"','DESCR: "([^"]*)"','PID: (\S+)','VID: ([^,]+)','SN: (\S+)']
				res = {}
				for r in rlist:
					m = re.search(r, s)
					if m is not None:
						res[r.split(':')[0]] = m.group(1)										# res['NAME'] = .....
				i = self.Add(res.get('NAME'), res.get('DESCR'), res.get('PID'), res.get('VID'), res.get('SN'))

			return len(self)
		
	def Add(self, name, descr, pid, vid, sn):													# create a new object
		c = InventoryItem(self, name, descr, pid, vid, sn)		
		self.Components.append(c)
		return c
		
	def Get(self):
		return self.Status()
# end class
		
class InventoryItem(generic_device.Component):																	# class to store inventory item
	def __init__(self, coll, name, descr, pid, vid, sn):
		generic_device.Component.__init__(self, coll = coll, sp = pid, config = '')
		self.Parameters['Name'] = name
		self.Parameters['Description'] = descr
		self.Parameters['VersionID'] = vid
		self.Parameters['SerialNumber'] = sn
		
# end class

class CDPNeighbors(generic_device.Neighbors):
	def __init__(self, device):
		generic_device.Neighbors.__init__(self, device = device)
		self.SignificantProperty = 'DeviceID'
		self.ComponentName = 'CDPNeighbor'
		self.ComponentClass = CDPNeighbor
		self.CapList = {}															# capability codes
		
	def Status(self, detail = False):
		self.Clear()
		cmdtext = 'show cdp neighbor'
		if detail:
			cmdtext += ' detail'						
		cdpresp = self.Device.Command(cmdtext, enable = detail)						# if detail, enable mode needed
		
		if detail:
			devs = re.split('\-\-+', cdpresp.output)								# split into devices 
			if len(devs) > 0:
				for d in devs:
					n = self.Add(d, detail = True)

		else:
			self.CapList = {}														# parse capability codes e.g R - Router, P - Phone....
			splits = []
			olines = cdpresp.output.splitlines()
			for line in olines[0:4]:
				if line and line.startswith('Device') == False:
					splits += line[17:].strip().split(',') 
			for s in splits:
				if s and '-' in s:
					k,v = s.split('-', 1)
					self.CapList[k.strip()] = v.strip()
			matches = re.findall(f'(\S+)\s+(\S+ \S+)\s+(\d+)\s+([{"".join(list(self.CapList.keys()))} ]+)\s+(IP Phone|\S+)\s+(.*)', cdpresp.output)						# IOS
			if matches == []:
				matches = re.findall(f'(\S+)\s+(\S+)\s+(\d+)\s+([{"".join(list(self.CapList.keys()))} ]+)\s+(\S+)\s+(\S+)', cdpresp.output)								# Nexus
			#print (matches)
			for m in matches:
				n = self.Add(arg = m, titles = ['DeviceID','Interface','Holdtime','Capability','Platform','PortID'])

		return len(self.Components)
		
	def CapLookup(self, code):														# code is single letter e.g 'R'
		cap = self.CapList.get(code, 'Unknown')
		return cap
# end class

class CDPNeighbor(generic_device.Neighbor):
	def __init__(self, coll, arg = None, detail = False, titles = []):											# class to store cdp neighbor info. arg could be string or list
		reglist = [{'attr':'DeviceID', 'reg':'Device ID: (\S+)'}, {'attr':'IPAddress', 'reg':'IP address: (\S+)'}, {'attr':'Platform', 'reg':'Platform: (.*),'}, 
					   {'attr':'Interface', 'reg':'Interface: (\S+),'}, {'attr':'PortID', 'reg':'Port ID \(outgoing port\): (.*)'}, {'attr':'HoldTime', 'reg':'HoldTime\s?: (\d+)'},
					   {'attr':'Version', 'reg':'Version :\s+(.*)\s'}, {'attr':'Duplex', 'reg':'Duplex: (\S+)'}, {'attr':'PowerDrawn','reg':'Power Drawn: (\S+) Watts'}, 
					   {'attr':'VTPDomain','reg':'VTP Management Domain: (\S+)'}]
		generic_device.Neighbor.__init__(self, coll = coll, arg = arg, detail = detail, reglist = reglist, titles = titles)
		self.Parameters['Capabilities'] = []
		self.Parameters['Type'] = 'CDP'
		#capList = [{'R':'Router'}, {'T':'Trans-Bridge'}, {'B':'Source-Route-Bridge'}, {'S':'Switch'}, {'H':'Host'}, {'I':'IGMP'}, {'r':'Repeater'}, 
		#					{'P':'Phone'}, {'D':'Remote'}, {'C':'CVTA'}, {'M':'Two-port Mac Relay'}]
		
		if detail:	
			m = re.search('Capabilities: ([\w\-\s]+)\s', arg)
			if m is not None:	
				for cap in capList:
					if cap.values()[0] in m.group(1):
						self.Parameters['Capabilities'].append(cap.values()[0])			
		else:			
			for l in arg[3].split():																# get each letter
				cap = self.Collection.CapLookup(l)
				self.Parameters['Capabilities'].append(cap)	
		
	def Interface(self):
		fullint = self.Collection.Device.Interfaces.FullName(self.Param('Interface'))	
		return fullint
		
# end class

class Licenses(generic_device.ComponentCollection):
	def __init__(self, device):
		generic_device.ComponentCollection.__init__(self, 'Licenses', device)
		self.SignificantProperty = 'Feature'
		self.ComponentName = 'License'
		self.ComponentClass = License
	
	def Status(self):
		self.Clear()
		resp = self.Device.Command('show license detail', enable = True)
		if resp.Status:
			splits = resp.output.split('\nIndex')
			for split in splits:
				if 'Feature: ' in split:
					m1 = re.search('Feature: (\S+)', split)
					if m1 is not None:
						lic = self.Add(m1.group(1))
						for line in split.splitlines()[1:]:
							arr = line.split(': ')								# License Generation version: 0x8200000, License Type: RightToUse
							if len(arr) > 1:
								k = arr[0].strip()								# License Generation version, License Type
								lic.Parameters[k] = arr[1]
					
		return len(self)
		
	def Add(self, feature):														# create a new object
		c = License(self, feature)
		self.Components.append(c)
		return c
	
	def Get(self):
		return self.Status()
# end class

class License(generic_device.Component):
	def __init__(self, coll, feature):
		generic_device.Component.__init__(self, coll = coll, sp = feature, config = '')
		
# end class

class LogMessages(generic_device.ComponentCollection):
	def __init__(self, device):
		generic_device.ComponentCollection.__init__(self, 'LogMessage', device)
		self.SignificantProperty = 'id'
		self.ComponentName = 'LogMessage'
		self.ComponentClass = LogMessage
		
	def Get(self, filter = ''):
		cmdtext = 'show log'
		if filter:
			cmdtext += ' | ' + filter					
		resp = self.Device.Command(cmdtext)
		if resp.Status:
			currmsg = None
			for line in resp.output.splitlines():
				m = re.search('(\w\w\w\s+\d+)\s(\S+):\s(.*): (.*)', line)								# '126673: Feb 15 09:26:31.594: ISDN Se0/0/1:15 Q931: TX -> DISCONNECT pd = 8  callref = 0x9FDE '
				if m is not None:
					if m.group(1):
						if currmsg is not None:
							self.LogMessages.append(currmsg)											# save current message to list
						currmsg = self.Add(m.group(1), m.group(2), m.group(3), m.group(4))				# create new LogMessage object
				else:																						
					if currmsg is not None:
						currmsg.append(line)															#  e.g.       Sending Complete
			# end for
		return resp.Status

	def Add(self, date, time, id, text):																# create a new object
		c = LogMessage(self, date, time, id, text)
		self.Components.append(c)
		return c
		
# end class 

class LogMessage(generic_device.Component):							# class to store log message
	def __init__(self, date, time, id, text):
		generic_device.Component.__init__(self, coll = coll, sp = id, config = '')
		self.Parameters['Date'] = date
		self.Parameters['Time'] = time
		self.Parameters['ID'] = id
		self.Parameters['Text'] = text
		
	def append(self, addtext):
		self.Text += addtext
# end class

class Services(generic_device.ComponentCollection):																		# generic blocks of code that do not fit into Component Collection model
	def __init__(self, device):
		generic_device.ComponentCollection.__init__(self, 'Services', device)
		self.SignificantProperty = 'Name'
		self.ComponentName = 'Service'
		self.ComponentClass = Service	
	
	def Get(self):																							# add voice services
		seclist = ['snmp-server','aaa','service','ntp','privilege','logging','ip route',]  	
		for s in seclist:
			cfg = self.Device.Configuration.StartsWith(s)													# e.g. 'service .....' or 'no service ....'
			if cfg:
				srv = self.Add(s, config = '\n'.join(cfg))
		return len(self)
	
# end class

class Service(generic_device.Component):
	def __init__(self, coll, name = '', type = '', config = ''):
		generic_device.Component.__init__(self, coll = coll, sp = name, type = type, config = config)
		
# end class

class IOSComponent(generic_device.Component):
	def __init__(self, coll = None, sp = '', type = '', config = '', itemname = ''):	
		generic_device.Component.__init__(self, coll = coll, sp = sp, type = type, config = config)
		self.ItemName = itemname
		
	def __repr__(self):
		return f'{self.ItemName} {self.Type} {self.SPValue}'

class IOSComponentCollection(generic_device.ComponentCollection):
	def __init__(self, dev, itemname, sp = 'Name', id = '', itemtype = '', filter = '', reglist = []):					# self.ClassMaps = IOSComponentCollection(dev = dev, itemname = 'class-map', id = 'class-map \S+ (\S+)', itemtype = 'class-map (\S+)')									
		generic_device.ComponentCollection.__init__(self, name = '', dev = dev, sp = sp)
		self.ComponentClass = IOSComponent
		self.ItemName = itemname																						# item name e.g. 'class-map'
		self.ID = id																									# regex for item id  e.g. name or tag
		self.ItemType = itemtype																						# regex for item type
		#self.Filter = filter																							# Method Filter() in generic_device !!
		self.reglist = reglist
	
	def Get(self, force = False):																										# self.ClassMaps.Get()
		filter = ''
		confs = self.Device.Configuration.ForceSections(self.ItemName) if force else self.Device.Configuration.Section(self.ItemName)
		for conf in confs:
			#print (f'conf: {len(conf)}')
			if not filter or filter in conf:
				m1 = None
				if self.ID == 'tag':	
					m1 = re.search('(\d+)', conf)																		# look for tag
				elif self.ID == 'name':
					m1 = re.search(self.ItemName + ' (\S+)', conf)														# look for name e.g. .GetItems('interface', 'name')  =>  'interface Ethernet99' 
				else:
					m1 = re.search(self.ID, conf)																		# e.g. .GetItems('controller, sp = 'controller [ET]1 (\S+)', itemtype = '([ET]1)')
				
				itype = ''														
				if m1 is not None:
					if self.ItemType:
						m2 = re.search(self.ItemType, conf)																# look for item type e.g. voip or pots for dial-peer
						if m2 is not None:
							itype = m2.group(1)
					#print(f'sp:{m1.group(1)} type:{itype} conf:{len(conf)}')
					newitem = self.Add( m1.group(1), type = itype, config = conf, itemname = self.ItemName)				# def Add(self, sp, type = '', config = '', unique = True):	
		return len(self)
		
	def Add(self, sp, type = '', config = '', itemname = '', unique = True):								# create a new component   ## __init__(self, coll = None, sp = '', type = '', config = ''):	
		create = False
		if unique == False:
			create = True														# always create
		else:
			c = self[sp]														# check if exists
			if c is None:
				create = True	
		
		if create:	
			if not sp:															# use next available if not supplied
				sp = self.NextTag()
			c = IOSComponent(self, sp, type, config, itemname)		
			self.Components.append(c)
			
		return c
# end class
	
class IOSFileSystems(generic_device.FileSystems):
	def __init__(self, dev = None):
		generic_device.FileSystems.__init__(self, dev = dev)
		
	def Get(self):														
		res = self.Device.Command('show file systems', enable = True)
		if res.Status:
			for line in res.output.splitlines():
				splits = line.strip().split()
				if len(splits) > 4 and 'Size(b)' not in line:
					fs = IOSFileSystem(self, text = line)
					self.Components.append(fs)
					
		return len(self)	

# end class

class IOSFileSystem(generic_device.FileSystem):
	def __init__(self, coll = None, name = '', type = '', text = ''):
		generic_device.FileSystem.__init__(self, coll = coll, name = name, type = type, text = text)

	def ParseConfig(self, config):														# ios specific	
		if config.startswith('*'):
			self.Set('Default','Yes')
		splits = config[1:].strip().split(maxsplit = 4)

		if len(splits) > 4 and splits[0] != 'Size(b)':
			prefs = splits[-1].split()													# might be more than one prefix
			self.Parameters['Name'] = prefs[0]
			if len(prefs) > 1:
				self.Parameters['Alias'] = prefs[1]
			self.Parameters['Flags'] = splits[-2]
			self.Parameters['Type'] = splits[-3]
			self.Parameters['Free'] = int(splits[-4]) if splits[-4].isdigit() else 0
			self.Parameters['Size'] = int(splits[-5]) if splits[-5].isdigit() else 0

	def List(self, path = ''):																# dev.FileSystems['flash:'].List('*')
		if self.Param('Type') not in ['opaque','network']:
			for i in range(0,3):															# try 3 times to list files
				if self.Collection.Device.debug:
					print (f'Try #{i}: List Files {path}')
				res = self.Collection.Device.Command(f'dir {self.Param("Name")}{path} | ex drwx ', ignoreexception = True)
				if res.Status:
					if res.output != '':
						fc = IOSFileCollection(self.Collection.Device)
						fc.Get(res.output)
						return fc
	
	def Upload(self, source, dest = ''):													# copy ftp://146.170.100.37/out/<filename> flash:
		dest = f'{self.Param("Name")}/{dest}' if dest else self.Param("Name")
		cmd = f'copy {source} {dest}'
		res = self.Collection.Device.TimedCommand(cmd, prompt = r'Destination filename', response = '\n', progressindicator = '!', completionindicator = '[OK -')
		return res.Status

# end class

class IOSFileCollection(generic_device.FileCollection):
	def __init__(self, device, fs = None, path = ''):
		generic_device.FileCollection.__init__(self, device, fs = fs, path = path)
		self.ComponentClass = IOSFile
		self.SignificantProperty = 'Name'

	def Get(self, output = ''):
		if output:
			for l in output.splitlines()[2:]:
				splits = l.strip().split()
				if len(splits) > 3:
					flags = splits[1]
					if 'd' in flags:
						f = IOSFileCollection(self.Device, fs = self.FileSystem, path = splits[-1])
						self.Components.append(f)
					else:
						#print (f'File:{splits[-1]}')
						f = IOSFile(coll = self, name = splits[-1])
						st = f.ParseConfig(l)
						if st:
							self.Components.append(f)
		# else: run commmand "dir path"
# end class

class IOSFile(generic_device.File):
	def __init__(self, coll, name = '', type = '', config = ''):
		generic_device.File.__init__(self, coll, name = name, type = type, config = config)
		
	def ParseConfig(self, config = ''):
		fp = "(\d+)\s+([drwx\-]+)\s+(\d+)\s+(\w{3} \d+ \d+)?\s+([\d:]+)?\s+(\+\d+:\d+)?(<no date>)?\s+(.*)$"
		self.Config = config if config else self.Config
		m = re.search(fp, self.Config)
		if m is not None:
			items = 'Index,Flags,Size,Date,Time,Misc,Name'.split(',')
			for i in range (0,3):
				self.Set(items[i], m.group(i + 1))
			for i in range (3,7):
				v = m.group(i + 1)
				if v is not None:
					self.Set(items[i],v)
			self.Set('Name',m.group(8))
			return True
		return False
		
	def Remove(self):
		res = self.Collection.Device.Command(f'del {self.Param("Name")}', prompts = {r'Delete filename':'\n',r'confirm':'\n'})			
		return res.Status
		
	def MD5CheckSum(self):
		res = self.Collection.Device.TimedCommand(f'verify /md5 {self.Param("Name")}', prompt = '', progressindicator = '.', completionindicator = '#')
		if res.Status:
			m = re.search('\) = ([0-9a-f]+)', res.output)
			if m is not None:
				return m.group(1)
		return ''
		
	def Download(self, dest):
		res = self.Collection.Device.TimedCommand(f'copy {self.Collection.Name}{self.Param("Name")} {dest}', prompt = '!', progressindicator = '!', completionindicator = 'Done!')
		return res.Status
# end class

class ROMMonitor(object):
	def __init__(self, device):
		self.Device = device
		self.Version = ''
		
	def __repr__(self):
		return f'ROMMonitor: {self.Version}'
		
	def Status(self, rp = ''):
		res = self.Device.Command('show rom-monitor ' + rp)
		m = re.search('System Bootstrap, Version (.*), ', res.output)
		self.Version = m.group(1) if m is not None else 'Not found'
		return res.Status
		
	def Upgrade(self, file, rp = 'all'):
		res = self.Device.TimedCommand('upgrade rom monitor filename {file} {rp}', prompt = '', progressindicator = 'out', completionindicator = 'ROMMON upgrade complete' )
		return res.Status
# end class
		
class VLANs(generic_device.GenericVLANs):
	def __init__(self, device):
		generic_device.GenericVLANs.__init__(self, device)
		self.ComponentClass = VLAN
		self.ComponentName = 'VLAN'
		self.reglist = [{'attr':'Name','reg':'name (\S+)'}]

	def Status(self):
		res = self.Device.Command('show vlans')
		olines = res.output.splitlines()
		ul = next((i for i,l in enumerate(olines) if l.startswith('------')), None)  # index of line starting ------
		if ul is not None:
			titles = olines[ul - 1].rsplit(maxsplit = 5)
			for l in olines[ul + 1:]:
				if l:
					vv = l.strip().split()											# vlan values  33,VLAN_33,|,Dynamic,No,No
					vlan = VLAN(self)
					vlan.fromText(titles, vv)
					self.Components.append(vlan)
		return len(self)
					
	def Get(self):
		secs = self.Device.Configuration.Section('vlan')
		for s in secs:
			m = re.search('vlan (\d+)', s)
			if m is not None:
				vlan = VLAN(self, id = m.group(1), config = s)
				self.Components.append(vlan)
		return len(self)
# end class

class VLAN(generic_device.GenericVLAN):
	def __init__(self, coll, id, name = '', type = '', config = ''):
		generic_device.GenericVLAN.__init__(self, coll, id = id, type = type, config = config)
		
	def fromText(self, titles, values):
		for a,b in zip(titles, values):
			if a != '|':
				self.Set(a, b)
		
	#def Detail(self):
	# res = self.Collection.Device.Command('show vlan {id}')
	
# end class

class AccessList(generic_device.Component):
	def __init__(self, coll, tag = '', config = ''):
		generic_device.Component.__init__(self, coll = coll, sp = tag, config = config)
		self.Rules = ACLRules(self, config)
		
	def __repr__(self):
		return ' '.join([self.__class__.__name__, self.Param('type'), self.Param('tag')])
		
	def dump(self):
		print(self)
		self.Rules.dump()
		
	def toCSV(self, headers = False):
		data = ''
		for i,line in enumerate(self.Rules):
			data += line.toCSV(not i if headers else False)
		return data
# end class

class IPAccessList(AccessList):
	def __init__(self, coll, tag = '', config = '', type = ''):
		AccessList.__init__(self, coll = coll, tag = tag, config = config)
		m = re.search('ip access-list (\w+) (\w+)', config)
		if m is not None:
			self.Parameters['tag'] = m.group(2)
			self.Parameters['type'] = m.group(1)
		
# end class

class ACLRules(generic_device.ComponentCollection):
	def __init__(self, acl, config):
		generic_device.ComponentCollection.__init__(self, 'ACLLines')
		self.ACL = acl
		self.SignificantProperty = 'ID'
		self.ComponentName = 'ACLRule'
		self.ComponentClass = ACLRule
		
		olines = config.splitlines()
		for line in olines:
			if line:
				if self.ACL.__class__.__name__ == 'AccessList':
					line = ' '.join(line.split()[2:])										# skip 'access-list xxx ' if legacy acl
					a = ACLRule(self, line)
					self.Components.append(a)
				else:
					if 'access-list' not in line:
						a = ACLRule(self, line)
						self.Components.append(a)
				
	def dump(self):
		for i,a in enumerate(self.Components):
			a.dump(not i)
# end class		

class ACLRule(object):											# rule in access control list
	def __init__(self, coll, line):
		self.Collection = coll									# parent collection
		self.line = line
		self.Protocol = ''
		self.ID = ''
		self.Remark = ''
		self.Action = ''
		self.Source = ''
		self.SourcePort = ''
		self.Dest = ''
		self.DestPort = ''
		self.Logging = False
		self.Established = False
		
		self.parse()
		
	def dump(self, header = False):
		if header:
			print('%s %-3s %-6s %-4s %-30s %-20s %-30s %-20s %s'%('ACL','ID', 'Action', 'Proto', 'Source', 'SourcePort', 'Destination', 'DestPort', 'Logging'))
		if self.Action == 'remark':
			print('%s %-3s %-6s %s'%(self.Collection.ACL.Param('tag'), self.ID, self.Action, self.Remark))
		else:
			print('%s %-3s %-6s %-4s %-30s %-20s %-30s %-20s %s'%(self.Collection.ACL.Param('tag'), self.ID, self.Action, self.Protocol, self.Source, self.SourcePort, self.Dest, self.DestPort, str(self.Logging)))

	def toCSV(self, headers = False):
		data = ''
		if headers:
			data += 'ACL,ID,Action,Protocol,Source,SourcePort,Destination,DestPort,Logging\n'
		if self.Action == 'remark':
			data += ','.join([self.Collection.ACL.Param('tag'),self.ID,self.Action, self.Remark]) + '\n'
		else:
			data += ','.join([self.Collection.ACL.Param('tag'),self.ID,self.Action, self.Protocol,self.Source,self.SourcePort,self.Dest,self.DestPort,str(self.Logging)]) + '\n'
		return data
	
	def parse(self):
		w = Splitter(self.line)
		if w.IsDigit():
			self.ID = w.Current()
			w.Next()
		
		self.Action = w.Current() 
		w.Next()
		if self.Action == 'remark':	
			self.Remark = w.Join(w.i, len(w))
		else:
			if 'log' in w:
				w.Remove('log')
				self.Logging = True
			if 'established' in w:
				w.Remove('established')
				self.Established = True
			if w.Current() in ['ip','udp','tcp','icmp']:
				self.Protocol = w.Current()
				w.Next()
			if w.Current() == 'any':
				self.Source = 'any'
				w.Next()
				if w.Current() == 'range':				# 'range' follows 'any'
					self.SourcePort = w.Join(w.i, w.i + 3)
					w.Inc(3)
				elif w.Current() in ['eq','neq','gt','lt']:					# 'eq' follows 'any'
					self.SourcePort = w.Join(w.i, w.i + 2)
					w.Inc(2)
				elif w.Current() == 'any':				# 'any' follows 'any'
					self.Dest = 'any'
					w.Next()
					
			sd = ''
			if w.Current() == 'host':
				sd = ' '.join(['host',w.Current()])
				w.i += 2
			elif w.IsIPV4():								# ip addr
				if re.match('[\d\.]+', w.Peek()):			# ip after after ip addr
					sd = ' '.join([w.Current(),w.Next()])	# just ip addr
					#print (sd)
					w.Inc(2)
				else:
					sd = w.Current()
					w.Next()
			#print(sd)
			if self.Source:
				self.Dest = sd
			else:
				self.Source = sd	
	
			if w.Current() == 'any':
				self.Dest = 'any'
			elif w.Current() == 'host':
				w.Next()
				self.Dest = ' '.join(['host',w.Current()])
			elif w.IsIPV4():							# ip addr & mask 
				self.Dest = ' '.join([w.Current(),w.Next()])
			elif w.Current() in ['eq','neq','gt','lt','range']:
				self.DestPort = ' '.join([w.Current(),w.Next()])
		
# end class

class IPAccessLists(generic_device.ComponentCollection):
	def __init__(self, device):
		generic_device.ComponentCollection.__init__(self, 'ACLLines', device)
		self.SignificantProperty = 'tag'
		self.ComponentName = 'IPAccessList'
		self.ComponentClass = IPAccessList
	
	def Get(self):																						
		confs = self.Device.Configuration.ForceSections('ip access-list') 
		#print(len(confs))
		for conf in confs:
			acl = IPAccessList(self, config = conf)
			self.Components.append(acl)
		return len(self)

# end class		

class AccessLists(generic_device.ComponentCollection):
	def __init__(self, device):
		generic_device.ComponentCollection.__init__(self, 'AccessLists', device)
		self.SignificantProperty = 'tag'
		self.ComponentName = 'AccessList'
		self.ComponentClass = AccessList
		
	def Get(self):
		acllines = self.Device.Configuration.Include('access-list*')										# get all lines starting with 'access-list'
		acltags = sorted(list(set([l.split()[1] for l in acllines])))										# get list of acl tags
		
		for t in acltags:
			alines = [l for l in acllines if l.startswith(f'access-list {t} ')]								# all lines for each acl
			self.Add(t, config = '\n'.join(alines))

	def Add(self, tag, config = ''):																		# create a new object
		c = AccessList(self, tag, config = config)
		self.Components.append(c)
		return c
# end class

