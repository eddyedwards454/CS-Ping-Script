# Generic Device - For use as sub-classes for other devices. Not to be used directly.
# Ian Butterworth Jan-Apr 2019.
# v0.9	30-06-22	Dummy mode. Response uses Slicer,Splitter
# v0.8	13-05-22	Added SecondProperty to __getitem__ in Component. Added Neighbors and Routing.
# v0.7  22-10-21	Added Telnet
# v0.6  24-09-21	Added FileSystems. Updated Command(), added TimedCommand()
# v0.5  04-03-21	Bug fixes
# v0.4  25-02-21	Now uses Netmiko! Added Connect and Disconnect methods. command method now Command()
# v0.3	29-09-20	Tweaks for Python 3
# v0.2  04-06-20	Flag for enable in DeviceInfo.Get()
# v0.1	25-04-19	ComponentCollection.Filter() returns Collection class instead of List
# v0.0

# standard libraries
import re, subprocess, os.path, datetime, tempfile, threading, types, gzip, time, telnetlib, logging
from netmiko import ConnectHandler
from ipaddress import ip_interface
# Vz libraries
from slice_split import Slicer, Splitter
cinfoavailable = True
try:
	from cinfo import Entity,Customer										# conditional import
except:
	cinfoavailable = False	

def ErrHandler(response):
	print (' - Error: %s'%response.Error)
	print (' - Command: %s'%response.Command)
# end function

class GenericDevice(object):
	def __init__(self, host = '', user = '', pw = '', enablepw = '', ping = True, port = 22, entity = None, creduser = '', debug = False, logging = False, dummy = False):							# define an Generic Device
		self.DeviceInfo = GenericDeviceInfo(self)											# device info object
		self.Interfaces = GenericInterfaces(self)											# Interfaces
		self.Configuration = GenericConfiguration(self)										# configuration
		self.VLANs = GenericVLANs(self)
		self.FileSystems = FileSystems(self)
		self.DeviceType = 'generic'															# Netmiko device type
		self.Connection = None																# Netmiko ConnectHandler or telnetlib telnet
		self.Protocol = 'ssh'																# or 'telnet'
		self.Host = host
		self.HostName = ''
		self.Username = user
		self.Password = pw
		self.EnablePassword = enablepw
		self.Error = ''
		self.Reachable = False																
		self.LastCommand = None																# last command
		self.LastResponse = None															# response to last command
		self.Entity = None																	# cinfo entity 
		self.debug = debug
		self.ResponseClass = GenericResponse												# response class name
		self.CommandClass = GenericCommand
		self.fails = ['Line has invalid autocommand', 'Invalid input', 'Permission denied', 'Authentication failed']			# list of device specific failure responses
		self.ErrorHandler = ErrHandler														# error handler function
		self.Logging = logging

		self.Port = port
		
		# IOS commands here for reference - must be replaced in sub-class!
		self.standardcmds = {}
		#self.standardcmds = dict(reload = 'reload')
		#deleteInterface = 'no interface ')
		
		if dummy:																			# dummy mode setup
			self.ping = self._DummyPing														# ping always returns true
			self.Connect = self._DummyConnect												# connect always returns true
			
		if entity:
			self.Entity = Entity(entity)													# cinfo details lookup
			self.Entity.Search()
			if self.Entity.Status:
				self.Host = self.Entity.ManagedIP
				if self.Username == '':														# profile and user provided - user overrides profile credentials		
					creds = self.Entity.PasswordTypes['3'].Get(creduser)					# get application user credentials
					if len(creds) > 0:
						self.Username = creds[0].ID
						self.Password = creds[0].Password
					else:
						self.Error = 'CINFO credential lookup failed. ' 
						return False
				if self.EnablePassword == '':
					encreds = self.Entity.PasswordTypes['4'].Get()
					if len(encreds) > 0:
						self.EnablePassword = encreds[0].Password
					else:
						self.Error = 'CINFO credential lookup failed. ' 
						return False
			else:
				self.Error = 'CINFO device lookup failed. ' 								
				return False
		# end if
				
		if self.Host and self.Username and self.Password:									# check we have user, pw and host
			self.Initialised = True
			if self.EnablePassword == '':
				self.EnablePassword = self.Password 										# use the same pw for enable if none supplied
		
		if self.debug:
			print ('Host:%s, User:%s, Pwd:%s, EnPwd:%s Port:%d '%(self.Host, self.Username, self.Password, self.EnablePassword, port))
		if ping:
			self.Reachable = self.ping()													# ping the host	
			if self.Reachable == False:
				self.Error = 'Device Unreachable'
				
		if self.Logging:
			self._Logging()
	
	def __repr__(self):
		status = 'Reachable' if self.Reachable else 'Unreachable'
		if self.Connection is not None and self.Connection.is_alive():
			status = 'Connected(%s)'%self.Connection.protocol
		return('%s %s %s'%(type(self).__name__, self.HostName if self.HostName else self.Host, status))
	
	def subproc(self, cmd):																	# spawn a subprocess
		
		if self.debug:
			print ('Sent:' + ';'.join(cmd))
		
		output = ''
		
		proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)								# spawn a subprocess
		res = proc.communicate()															# read output - blocking - will wait until proc responds, or watchdog timer stops it
		if proc.returncode >= 0:															# normal return
			output = res[0]
		
		if self.debug:
			print ('Received:\n' + output.decode())
				
		return output.decode()	
		
	def ping(self, host = '', count = 5): 													# ping the device
		status = False
		if not host:
			host = self.Host
		cmd = ['ping', '-c', str(count), '-q', host]
		output = self.subproc(cmd)
		
		if 'unknown host' in output:
			self.PingResult = output
		else:
			rx = 0
			m = re.search('(\d+) packets transmitted, (\d+) received', output)
			if m is not None:
				rx = int(m.group(2))
				if rx > 0:
					status = True
			
			self.PingResult = {'sent':count, 'received':rx}
		return status									
	
	def Connect(self, quiet = True, **kwargs):																				# kwargs allows other parameters e.g ssh_strict = True, timeout = 10
		try:
			if self.debug:
				print ('Host:%s Userid:%s Password:%s DevType:%s Port:%d'%(self.Host,self.Username,self.Password,self.DeviceType,self.Port))
				print (kwargs)
				print ('Connecting....')
			if self.Protocol == 'ssh':
				self.Connection = ConnectHandler(device_type=self.DeviceType, host=self.Host, username=self.Username, password=self.Password, secret=self.EnablePassword, port=self.Port, **kwargs)
			#elif self.Protocol == 'telnet':
				#self.Connection = TelnetConnection()
		except Exception as e:
			if not quiet:
				print(e)																							# suppress 'common causes' message																		
			return False
		else:
			if self.debug == True:
				print('Connected: protocol:%s'%self.Protocol)
			return True
	
	def Disconnect(self):
		self.Connection.disconnect()
															
	def Command(self, cmds, enable = False, config = False, prompts = {}, ignoreexception = False, **kwargs):		# submit a command to device.  example: prompt={'512':'2048'} {'Confirm':'Yes'}
		self.LastCommand = cmds
		if cmds == '':
			return self.ResponseClass(self, error = 'Empty command string!')
		
		if self.Connection is None:
			if self.Connect() == False:
				return self.ResponseClass(self, error = 'Unable to connect!')
		#else:
			#if self.Connection.is_alive() == False:																# removed as it f**ks up Juniper commands !
				#return self.ResponseClass(self, error = 'Connection closed!')
		
		if config or enable:
			if self.EnableMode() == False:
				return
		
		output = ''
		iresp = self.ResponseClass(self, True, '', cmds)															# assume it worked, unless we find out otherwise!
		iresp.StartTime = datetime.datetime.now()
		if self.debug:
			print (f'- {iresp.StartTime}: sending command "{cmds}" ...')
		try:
			if prompts != {}:
				if self.debug:
					print (f'   : sending command and expecting prompt: {list(prompts.keys())[0]}')
				output = self.Connection.send_command(cmds, expect_string = list(prompts.keys())[0], strip_prompt=False, strip_command=False)						# wait for custom prompt e.g. '[confirm]'
				if len(prompts) > 1:	
					if self.debug:
						print (f' 	: sending response: {list(prompts.values())[0]} ...expecting prompt: {list(prompts.keys())[1]}')
					output += self.Connection.send_command(list(prompts.values())[0], expect_string = list(prompts.keys())[1], strip_prompt=False, strip_command=False)	# send response e.g. 'y', expect next prompt
					if self.debug:
						print (f' 	: sending response: {list(prompts.values())[1]}')
					output += self.Connection.send_command(list(prompts.values())[1], strip_prompt=False, strip_command=False)											# send next response
				else:
					if self.debug:
						print (f' 	: sending response: {list(prompts.values())[0]}')
					output += self.Connection.send_command(list(prompts.values())[0], strip_prompt=False, strip_command=False)
			elif config:
				output = self.Connection.send_config_set(cmds)
			else:
				if self.debug and kwargs != {}:
					print ('kwargs: ' + str(kwargs))
				output = self.Connection.send_command(cmds, **kwargs)
		
		except Exception as e:
			if self.debug:
				print (f'** Exception: {e}')
			if ignoreexception == False:
				iresp.Error = e
				iresp.Status = False
		
		iresp.EndTime = datetime.datetime.now()		
		if self.debug:
			print (f'- {iresp.EndTime}: response received')
			print (output)
			
		iresp.parseOutput(output)												
		
		self.LastResponse = iresp
		return iresp

	def TimedCommand(self, cmds, prompt = '', response = '\n', progressindicator = '', completionindicator = '', prog = ''):		# TimedCommand('copy ftp://test.bin flash:', prompt = 'Destination filename', progressindicator = '!', completionindicator = '[OK')
		self.LastCommand = cmds
		if self.debug:
			print (f'TimedCommand: {cmds}')

		output = ''
		iresp = self.ResponseClass(self, True, '', cmds)										# assume it worked, unless we find out otherwise!
		iresp.StartTime = datetime.datetime.now()
		conn = self.Connection
		
		try:
			if prompt:
				output = conn.send_command(cmds, expect_string = prompt)						# send command, look for initial prompt
				output += conn.send_command_timing(response)									# send response
			else:
				output += conn.send_command_timing(cmds)										#  send_command_timing(self, command_string, delay_factor=1.0, max_loops=150, strip_prompt=True, strip_command=True, normalize=True, use_textfsm=False, textfsm_template=None, use_ttp=False, ttp_template=None, use_genie=False, cmd_verify=False)
			
			while(1):
				if self.Connection.is_alive():
					output+= conn.read_channel()
					if output.endswith(progressindicator):											# look for progress indicator (! or .)
						time.sleep(10)
						if prog:
							now = datetime.datetime.now()
							diff = now - iresp.StartTime
							print(f'{diff.seconds}s:{prog}', end = '\r')
					else:
						break
				else:
					iresp.Error = 'Connection broken'
					iresp.Status = False
					
		except Exception as e:
			iresp.Error = e
			iresp.Status = False
		
		iresp.EndTime = datetime.datetime.now()		
		iresp.parseOutput(output)	
		iresp.Status = True if completionindicator in output else False							# look for completion indicator
		self.LastResponse = iresp
		return iresp
		
	def Reload(self):										
		cmdtext = self.standardcmds.get('reload')		
		runresp = self.Command(cmdtext)	
		return runresp.Status
	
	def EnableMode(self, secret = ''):
		if self.debug:
			print ('- Enter Enable Mode')
		if secret:
			self.EnablePassword = secret
			self.Connection.secret = secret
		if self.Connection.check_enable_mode() == False:
			try:
				self.Connection.enable()
			except Exception as e:
				self.LastResponse = self.ResponseClass(self, error = e)
				return False
		return True
		
	def EnableExit(self):
		if self.debug:
			print ('- Exit Enable Mode')
		if self.Connection.check_enable_mode() == True:
			try:
				self.Connection.exit_enable_mode()
			except Exception as e:
				self.LastResponse = self.ResponseClass(self, error = e)
				return False
		return True
		
	def _Logging(self, logfile = ''):
		if logfile == '':
			logfile = f'{self.Host}.log'
		logging.basicConfig(filename = logfile, level = logging.DEBUG)
		logger = logging.getLogger("netmiko")
		
	def _DummyConnect(self, quiet = True, **kwargs):	
		self.Connection = DummyConnection()
		for k,v in kwargs.items():	
			setattr(self.Connection, k, v)
		return True
		
	def _DummyPing(self, host = '', count = 5): 	
		self.PingResult = {'sent':'3', 'received':'3'}
		return True
# end class	

class DummyConnection(object):													# Dummy connection. Uses files for output. Testing only.
	def __init__(self):
		self._connected = True
		self.protocol = 'dummy'
		self._enabled = True
		self.device_type = ''
		self.fast_cli = True
		
	def is_alive(self):
		return True if self._connected else False
	
	def disconnect(self):
		self._connected = False
		
	def send_command(self, cmds, *args, **kwargs):
		output = ''
		with open(f"{cmds.replace(' ','-').replace('/','-')}.txt") as fp:		# show version => show-version.txt
			output = fp.read()
		return output
	
	def send_command_timing(self, cmds, *args, **kwargs):
		return send_command(self, cmds, *args, **kwargs)
	
	def check_enable_mode(self):
		return True
		
	def enable(self):
		self._enabled = True
		return self._enabled
		
	def exit_enable_mode(self):
		self._enabled = False
		return self._enabled
# end class

class GenericRouter(GenericDevice):
	def __init__(self, host = '', user = '', pw = '', enablepw = '', ping = True, port = 22, entity = None, creduser = '', debug = False, logging = False):					
		GenericDevice.__init__(self, self, host = host, user = user, pw = pw, enablepw = enablepw, ping = ping, port = port, entity = entity, creduser = creduser, logging = logging, debug = debug)
		self.RoutingProtocols = RoutingProtocols(self)
		self.IPRoutes = IPRoutes(self)
		
# end class

class GenericCommand(object):													# command definition
	def __init__(self, commands, enable = False, config = False, timeout = 0, customprompt = {}, yesno = 'yes'):
		self.Commands = commands
		self.Enable = enable													# enable mode command
		self.Config = config													# config mode commmand
		self.Timeout = timeout													# specify a timeout for the command, 0 - use device timeout
		self.YesNo = yesno														# response to Yes/No prompt if needed.
		self.CustomPrompt = customprompt										# custom prompt/reponse for expect script  
		
		if self.Config:															# force enable if config mode requested
			self.Enable = True
		
	def submit(self, connection):												# run the command on the connected device
		resp = connection.Command(self)											# get Reponse object back
		return resp

# end class
		
class GenericResponse(object):
	def __init__(self, dev, status = False, text = '', command = '', error = ''):
		self.Device = dev														# parent device
		self.Status = status
		self.Error = error
		self.Command = command													# the command this is a response to
		self.output = ''														# the output of the command
		self.debug = False
		self.FailedLines = []													# commands that failed, list of tuples
		self.StartTime = None													# start time
		self.EndTime = None                                                     # end time
		self.Elapsed = 0														# execution time
		self.PromptChars = ['#','>'] 											# prompt characters - device specific - override in device class
		self.Executed = False													# whether there is evidence of the commands being executed
		self.Retry = 0															# retry #
		self.lastul = 0															# last underline line
		self.olines = []														# output split into lines
		
		dev.LastResponse = self		
		if self.Device.debug and self.Error:
			print ('- Response: %s'%self.Error)
	
	def __repr__(self):
		return ('%s: Status:%s'%(self.__class__.__name__, str(self.Status)))
	
	def cleanOutput(self, dirtytext):											# placeholder - device specific
		return dirtytext														# return what was received. Real function will return cleantext.
		
	def parseOutput(self, output):														
		if self.StartTime is not None:
			self.Elapsed = self.EndTime - self.StartTime
			self.output = self.cleanOutput(output)
			
		self.findFails()													
		
		if self.Status == False and self.Device.ErrorHandler is not None:		# call the error handler
			self.Device.ErrorHandler(self)
			
		return self.Status
		
	def findFails(self):														# placeholder - device specific code to look for failed commmands
		pass																	# add code to device class, not here!
	
	def SplitLines(self, delim = '------'):
		self.olines = Splitter(self.output, '\n')
		self.uls = [i for i,o in enumerate(self.olines) if o.startswith(delim)] # underlines
		self.lastul = self.uls[-1] if len(self.uls) > 0 else 0
		return self.olines
	
	def Slicer(self, slices = None):
		s = Slicer(self.output, slices = slices)								# auto-slice output by default. def __init__(self, lines = [], skip = 0, file = '', auto = True, overlap = True, slices = None, debug = False):
		return s
# end class

class GenericDeviceInfo(object):												# class to hold verison information
	def __init__(self, dev = None):
		self.Device = dev
		self.Parameters = {}
		self.text = ''															# command output text
		self.commands = dict(getInfo = 'show version')
		self.reglist = {}
		self.debug = False
		
	def Get(self, enable = False):												# get device info
		verresp = self.Device.Command(self.commands.get('getInfo'), enable = enable)
		if verresp.Status:
			self.parseText(verresp.output)
		
		return verresp.Status			
	
	def parseText(self, text):
		if self.debug:
			print ('parseText: len: %d'%len(text))
		self.text = text		
		for reg in self.reglist:												# look for things in command output
			if reg.get('all',''):
				m = re.findall(reg.get('reg'), self.text)
				if m is not None:
					self.Parameters[reg.get('all')] = m
			else:
				attr = reg.get('attr')
				res = re.search(reg.get('reg'), self.text)
				if res is not None:
					if attr == 'Flash' or attr == 'Memory':
						self.Parameters[attr] = self.formatMemory(res.group(1))
						self.Parameters[attr + 'KB'] = res.group(1)	
					else:
						self.Parameters[attr] = res.group(1)
					if self.debug:
						print('- Reg: %s: %s'%(attr, res.group(1)))
		
		if self.Param('Hostname'):
			self.Device.HostName = self.Param('Hostname')
			
	def Param(self, pname):
		return self.Parameters.get(pname, '')
		
	def formatMemory(self, mem, format = 'auto', unit = 'kb'):							# format is 'k', 'M' or 'G', unit = 'b' or 'kb'
		# return a formatted string for amount of memory
		memstr = ''
		rnd99 = lambda f:  round(f) if (f - int(f)) * 100 > 97 else f			# round up if .99 or .98 
		kb = rnd99(int(mem)/1024.0) if unit == 'b' else int(mem)
		if kb == 0:
			return '0kb'
		mb = rnd99(kb/1024.0)
		gb = rnd99(mb/1024.0)
		
		if format == 'auto':
			if kb < 1024:
				memstr = str(kb) + 'kb'
			elif kb < 1048576:	
				memstr = '{0:.2f}'.format(mb) + 'Mb'
			elif kb >= 1048576:
				memstr = '{0:.2f}'.format(gb) + 'Gb'
		elif format.startswith('k'):
			memstr = str(kb) + 'kb'
		elif format.startswith('M'):
			memstr = '{0:.2f}'.format(mb) + 'Mb'
		elif format.startswith('G'):
			memstr = '{0:.2f}'.format(gb) + 'Gb'
		
		return memstr.replace('.00', '')

# end class	

class GenericConfiguration(object):													# can be used as standalone class for parsing IOS config
	def __init__(self, dev = None):
		self.Device = dev
		self.Sections = []															# sections of configuration
		self.Text = ''																# actual text
		self.commands = dict(GetCommand = 'show configuration', GetItem = '', save = '')
		self.DeferConfig = False													# defer config - save configuration changes for one command
		self.ConfigBuffer = ''
		self.gotconfig = False														# True when loaded
		
	def __len__(self):
		return len(self.Text)
		
	def __repr__(self):
		return '%s %s len:%d sections:%d'%(type(self).__name__, 'Loaded' if self.gotconfig else 'Not Loaded', len(self), len(self.Sections))
	
	def __getattribute__(self, attr):
		method = object.__getattribute__(self, attr)
		if type(method) == types.MethodType:										# get the config if read method is called but no config loaded yet
			if attr in ['Section','Find','Include','Item'] and self.gotconfig == False:
				self.Get()															
		return method
		
	def Get(self, timeout = 0):														# get the configuration
		runresp = self.Device.Command(self.commands.get('GetCommand'), enable = True)		# requires enable mode, override default timeout if specified
		if runresp.Status:
			self.fromText(runresp.output)											# read config	
			self.gotconfig = True
		return runresp.Status
	
	def Import(self, text = '', filename = ''):										# import config from text or file
		if filename:
			try:
				fp = open(filename, 'r')
			except IOError as e:
				self.Error = e.strerror
			else:
				text = fp.read()
		
		if text:
			self.fromText(text)
			self.gotconfig = True
		
		return self.gotconfig
	
	def Export(self, filename, compress = False):											# export the config to a file
		try:
			if compress:
				fp = gzip.open(filename + '.gz', 'w')
			else:
				fp = open(filename, 'w')
		except IOError as e:
			self.Error = e.strerror
			return False
		else:
			fp.write(self.Text)
			fp.close()
			return True
	
	def fromText(self, text):																# sanitise and filter a configuration - device specific											
		pass
	
	def Section(self, keyword, filter = ''):													
		if filter:
			secs = [s for s in self.Sections if s.startswith(keyword) and filter in s]	 	# return section(s) of config matching keyword and includes filter e.g conf.Section('dial-peer voice', 'pots')
		else:
			secs = [s for s in self.Sections if s.startswith(keyword)]						# return section(s) of config matching keyword e.g conf.Section('dial-peer voice')
		return secs
					
	def Include(self, keyword):																# return lines including keyword e.g. conf.Include('service')
		if keyword.endswith('*'):
			return [l for l in self.Text.splitlines() if l.startswith(keyword[:-1])]		# line starts with 
		elif keyword.startswith('*'):
			return [l for l in self.Text.splitlines() if l.endswith(keyword[1:])]			# line ends with
		else:
			return [l for l in self.Text.splitlines() if keyword in l]
			
	def Find(self, regex):																	# e.g. Find('ip ssh version (\S+)')
		m = re.search(regex, self.Text)
		if m is not None:
			return m.group(1)
		else:
			return ''
	
	def Item(self, itemtype, id):
		itemConfig = ''
		if self.Text == '':		
			resp = self.Command('%s %s %s'%(self.commands.get('GetItem'), itemtype, id), enable = True)		# 'show run | sec' 'interface' 'FastEthernet0/1'
			if resp.Status:
				itemConfig = resp.Text
		else:					
			secs = self.Section(itemtype + ' ' + id)
			itemConfig = secs[0] if len(secs) > 0 else ''								# get the section from main config, Section returns a list
		
		return itemConfig
	
	def Save(self):																		# save running configuration
		resp = self.Device.Command(self.commands.get('save'), enable = True)
		return resp.Status
	
	def Defer(self):																	# defer config changes until later
		self.DeferConfig = True
		
	def CommitChanges(self):															# commit stored changes to the device configuration
		if self.DeferConfig:
			self.DeferConfig = False													# turn off deferring
			resp = self.Device.Command(self.ConfigBuffer, config = True)
			if resp.Status:
				self.ConfigBuffer = ''
			return resp	
			
	def Clear(self):																	# Clear memory, not device itself
		self.Text = ''
		self.Sections = []
		self.gotconfig = False
		
	def Start(self):
		if self.Device.debug:
			print ('- Enter Config Mode')
			if self.Device.Connection.check_enable_mode() == False:
				self.LastResponse = self.Device.ResponseClass(self.Device, error = 'Not in enable mode')
				return False
			if self.Device.Connection.check_config_mode() == False:
				try:
					self.Device.Connection.config_mode()
				except Exception as e:
					self.LastResponse = self.Device.ResponseClass(self.Device, error = e)
					return False
		return True

	def End(self):
		if self.Device.debug:
			print ('- Exit Config Mode')
			if self.Device.Connection.check_config_mode() == True:
				try:
					self.Device.Connection.exit_config_mode()
				except Exception as e:
					self.LastResponse = self.Device.ResponseClass(self.Device, error = e)
					return False
		return True
		
	def Configure(self, cmds):
		return self.Device.Command(cmds, config = True)
# end class

# common component class template
class Component(object):
	def __init__(self, coll = None, sp = '', type = '', config = ''):					# e.g. ConfigComponent(self.Interfaces, 'FastEthernet0/1', '')
		self.SPValue = ''																# 100, 12, FastEthernet0/1, vty
		self.Type = type																# type variant, vty/con/aux  E1/T1  pots/voip  etc
		self.Config = config	
		self.Collection = coll															# parent collection
		self.Parameters = {}															# component parameters, e.g. Name, description, slot, port etc
		self.reglist = {}																# attribute/regex pairs
		self.commands = dict(configure = '',enable = '',disable = '',remove = '')										
		
		if config:
			self.ParseConfig(config)
			
		if sp:
			self.SPValue = sp															# e.g. 'FastEthernet0/1'
			self.Parameters[self.Collection.SignificantProperty] = sp
			
		if type:
			self.Parameters['Type'] = type
				
	def __repr__(self):
		return ' '.join([self.__class__.__name__, self.Type, self.SPValue])
		
	def __eq__(self, other):
		if self.SPValue.isdigit():
			return int(self.SPValue) == int(other.SPValue)										
		else:
			return self.SPValue == other.SPValue
	
	def __hash__(self):
		return( hash(self.SPValue))
	
	def __lt__(self, other):
		if self.SPValue.isdigit() and other.SPValue.isdigit():									# if digit, use int to get correct sort order
			return(int(self.SPValue) < int(other.SPValue))
		else:
			return(self.SPValue < other.SPValue)					
	
	def __contains__(self, param):																# check for presence of Parameter name. e.g. 'Name' in i => True
		return True if param in self.Parameters.keys() else False
		
	def GetConfig(self):
		if self.Collection.Device is not None:
			self.Config = self.Collection.Device.Configuration.GetItemConfig(self.Collection.ComponentName, self.Tag)	# get config from device
			self.ParseConfig()																	# parse config
			
	def Save(self):																				# save config to the router
		if self.Config:
			res = self.Collection.Device.Command(self.Config, config = True)
			return res.Status
	
	def Remove(self):
		return self.Configure(self.commands.get('remove'))
	
	def ParseConfig(self, config = ''):
	
		if config:
			self.Config = config
	
		for r in self.Collection.reglist:
			if r.get('all',''):
				m = re.findall(r.get('reg'), self.Config)
				self.Parameters[r.get('all')] = m
			else:
				m = re.search(r.get('reg'), self.Config)
				if m is not None:
					if r.get('res'):
						self.Parameters[r.get('attr')] = 'Down'
					else:
						self.Parameters[r.get('attr')] = m.group(1)
					
	def Param(self, pname):
		return self.Parameters.get(pname, '')
	
	def Set(self, param, val):
		self.Parameters[param] = val
		
	def Configure(self, cmd):																	# configure a command for the component
		if cmd:
			prefix = self.commands.get('configure')%(self.SPValue) if '%' in self.commands.get('configure') else self.commands.get('configure')
			cmdtxt = '%s\n%s'%(prefix, cmd)														# e.g. 'dial-peer voice 10\nvoice-class codec 1'
			resp = self.Collection.Device.Command(cmdtxt, config = True)
			return resp.Status		
		else:
			return False
	
	def Enable(self):																			# command to enable a component e.g. 'no shutdown'
		return self.Configure(self.commands.get('enable'))
		
	def Disable(self):
		return self.Configure(self.commands.get('disable'))										# command to disable a component e.g. 'shutdown'

	def dump(self, header = True):
		if header:
			print('\t'.join(self.Parameters.keys()))
		print('\t'.join([str(p) for p in self.Parameters.values()]))

# end class

class ComponentCollection(object):
	def __init__(self, name = '', dev = None, sp = 'Name'):
		self.Components = []
		self.CollectionName = name												# Interfaces, VLANs, dial-peers....
		self.Device = dev														# parent device
		self.SignificantProperty = sp											# could be 'ID', 'Tag' etc.
		self.ComponentClass = Component											# replace in sub-class. e.g. Interface
		self.ComponentName = 'Component'										# component name e.g. 'interface', 'dial-peer voice' etc
		self.reglist = []														# list of attribute/regex pairs  {'attr':'','reg':''} (moved from Component)
		self.SearchParam = ''													# searchable parameter, should be unique e.g. mac-address, phone number
		self.SecondProperty = 'Type'											# second propery to search when tuple used with __getitem__
		
	def __repr__(self):
		return '%s: %d'%(self.__class__.__name__, len(self.Components))
	
	def __len__(self):
		return len(self.Components)
		
	def __iter__(self):															# create a generator  e.g  g = iter(dev.Interfaces), next(g) -- or --- for i in iter(dev.Interfaces):
		for c in self.Components:
			yield c
	
	def __contains__(self, id):													# if collection contains 'id'. e.g. 'Loopback0' in dev.Interfaces, '900' in dev.DialPeers
		return True if self.__getitem__(id) is not None else False
		
	def Status(self):															# get component status
		pass
		return len(self)
		
	def Get(self):																# get all components from config
		pass
		return len(self)
		
	def __getitem__(self, id):													# get a component   e.g. dev.Interfaces['Loopback0'] or dev.Interfaces[0]
		if isinstance(id, int):
			return self.Components[id]
		elif isinstance(id, tuple):
			return next((c for c in self.Components if c.Param(self.SignificantProperty) == id[0] and c.Param(self.SecondProperty) == id[1]), None)		# search for id and type
		else:
			#item = next((c for c in self.Components if c.SPValue == id), None)
			item = next((c for c in self.Components if c.Param(self.SignificantProperty) == id), None)
			if item is None:
				item = next((c for c in self.Components if c.Param(self.SearchParam) == id), None)			# use searchable parameter
			return item
			
	def Filter(self, pname, pvalue):											
		if isinstance(pvalue, bool):
			items = [c for c in self.Components if c.Param(pname) == pvalue]						# filter component collection
		else:
			if pvalue.startswith('*') and pvalue.endswith('*'):									# filter component collection e.g. dev.Interfaces.Filter('ip address', '10.128*')
				items = [c for c in self.Components if pvalue[1:-1] in c.Param(pname)]		
			elif pvalue.endswith('*'):
				items = [c for c in self.Components if c.Param(pname).startswith(pvalue[:-1])]	
			elif pvalue.startswith('*'):
				items = [c for c in self.Components if c.Param(pname).endswith(pvalue[1:])]	
			else:
				items = [c for c in self.Components if c.Param(pname) == pvalue]			
		
		newcoll = self.__class__(self.Device)												# create new collection 
		for i in items:
			newcoll.Components.append(i)
		return newcoll
			
	def Add(self, sp, type = '', config = '', unique = True):								# create a new component   ## __init__(self, coll = None, sp = '', type = '', config = ''):	
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
			c = self.ComponentClass(self, sp, type, config)		
			self.Components.append(c)
			
		return c
		
	def Remove(self, id):														# remove an item from the collection. does not remove it from the device. Use Component.Remove() for that.
		i = self.__getitem__(id)
		if i is not None:
			self.Components.remove(i)
			
	def Clear(self):
		self.Components = []
		
	def NextTag(self):															# return next available numeric tag
		nexttag = ''
		if len(self) == 0:
			return '1'
		tags = [i.SPValue.isdigit() for i in self.Components]
		if all(tags):															# if all significant values are numeric...
			maxc = max(self.Components)											# find the highest component
			nexttag = str(int(maxc.SPValue) + 1	)								# add 1 
		return nexttag
		
	def dump(self):
		print('\t'.join(self.Components[0].Parameters.keys()))
		for r in self.Components:
			r.dump(False)
# end class	

class GenericInterfaces(ComponentCollection):
	def __init__(self, device):
		ComponentCollection.__init__(self, 'Interfaces', device)
		self.ComponentName = 'Interface'
		self.ComponentClass = GenericInterface

# end class

class GenericVLANs(ComponentCollection):
	def __init__(self, device):
		ComponentCollection.__init__(self, 'VLANs', device)
		self.SignificantProperty = 'ID'
		self.ComponentName = 'VLAN'
		self.ComponentClass = GenericVLAN

# end class

class GenericInterface(Component):
	def __init__(self, coll, name, type = '', config = ''):
		Component.__init__(self, coll, sp = name, type = type, config = config)
		self.commands = {}														# self.commands = dict(ifconfig = 'interface ',disable = 'shutdown', enable = 'no shutdown')		
		if name:
			self.parseName()
		
	def parseName(self):														# device specific - get type/slot/port etc..
		pass

# end class

class GenericVLAN(Component):
	def __init__(self, coll, id, type = '', config = ''):
		Component.__init__(self, coll, sp = id, type = type, config = config)
		
# end class

class FileSystems(ComponentCollection):
	def __init__(self, dev = None):	
		ComponentCollection.__init__(self, name = 'FileSystems', dev = dev, sp = 'Name')
		self.ComponentClass = FileSystem
		self.SearchParam = 'Alias'
	
	def Default(self):																	# get the default file system
		return next((f for f in self.Components if f.Param('Default') == 'Yes'), None)
		
	def Get(self):																		# device specific
		pass		
		return len(self)		
					
# end class

class FileSystem(Component):
	def __init__(self, coll = None, name = '', type = '', text = ''):					# self.Flash = FileSystem(dev, 'flash0:')
		Component.__init__(self, coll = coll, sp = name, type = type, config = text)
	
	def __repr__(self):
		return f'FileSystem: {self.Param("Name")}'
		
	def ParseConfig(self, config):														# device specific
		pass
		
	def List(self, path = '*'):															# dev.FileSystems['flash:'].List('*')
		pass
		
	def Upload(self, path):																# upload (copy) file
		pass	
		
	def FileExists(self, file):
		files = self.List(file)
		return True if len(files) == 1 else False
# end class

class FileCollection(ComponentCollection):
	def __init__(self, device, fs = None, path = ''):
		self.Path = path
		ComponentCollection.__init__(self, 'Files', device)
		self.SignificantProperty = 'Name'
		self.ComponentName = 'File'
		self.ComponentClass = File
		self.FileSystem = fs
		
		if self.FileSystem is None:
			self.FileSystem = self.Device.FileSystems.Default()

# end class

class File(Component):
	def __init__(self, coll, name, type = '', config = '', reglist = []):
		Component.__init__(self, coll, sp = name, type = type, config = config)

	def __repr__(self):
		return f'File: {self.Param("Name")}'
# end class

class Neighbors(ComponentCollection):
	def __init__(self, device):
		ComponentCollection.__init__(self, 'Neighbors', device)
		self.SignificantProperty = 'Neighbor'
		self.ComponentName = 'Neighbor'
		self.ComponentClass = Neighbor
	
	def Status(self):
		pass																			# protocol specific
		
	def Add(self, arg, detail = False, titles = []):									# create a new object
		#print(f'{self} Add(): {arg}\ndetail: {detail} titles: {titles}\nclass: {self.ComponentClass}')  
		c = self.ComponentClass(self, arg = arg, detail = detail, titles = titles)		
		if c.SPValue:
			self.Components.append(c)													# only add valid entries
		return c
		
	def Get(self):
		return self.Status()	
# end class

class Neighbor(Component):
	def __init__(self, coll, arg = None, detail = False, reglist = [], titles = []):	# class to store neighbor info. 
		Component.__init__(self, coll = coll, sp = '', config = '')
		if detail:
			for r in reglist:
				m = re.search(r.get('reg'), arg)
				if m is not None:
					self.Parameters[r.get('attr')] = m.group(1).strip()
		else:
			for a,b in zip(titles, arg):
				self.Parameters[a] = b
				
		self.SPValue = self.Parameters[self.Collection.SignificantProperty]
			
	def __repr__(self):
		return f'{self.__class__.__name__} {self.SPValue}'
# end class

class RoutingProtocols(ComponentCollection):
	def __init__(self, device):
		ComponentCollection.__init__(self, name = 'RoutingProtocols', dev = device)			# def __init__(self, name = '', dev = None, sp = 'Name'):
		self.ComponentClass = RoutingProtocol
		self.ComponentName = 'RoutingProtocol'
		self.SecondProperty = 'ID'
		
	def Status(self):
		resp = self.Device.Command('show ip protocols')	
		if resp.Status:
			pros = re.findall('Routing Protocol is "(.*)"', resp.output)
			for p in pros:
				if ' ' in p:
					name,rid = p.split()
					self.Add(name.upper(), rid)					# OSPF 1
				else:
					self.Add(p)									# RIP
				
	def Add(self, rname, rid = ''):
		if rname == 'BGP':
			rp = BGP(self, rid)
		elif rname == 'OSPF':
			rp = OSPF(self, rid)
		elif rname == 'EIGRP':
			rp = EIGRP(self, rid)
		else:
			rp = RoutingProtocol(self, rname, rid)
		self.Components.append(rp)
		
# end class

class RoutingProtocol(Component):															# generic routing protocol
	def __init__(self, coll, name, id):
		Component.__init__(self, coll = coll)
		self.Parameters['Name'] = name
		self.Parameters['ID'] = id
		self.Neighbors = None
		
	def __repr__(self):
		return f'Routing Protocol: {self.Parameters["Name"]} {self.Parameters["ID"]}'
		
	def Status(self):
		pass
		
# end class

class IPRoutes(ComponentCollection):
	def __init__(self, device):
		self.Codes = {}	
		ComponentCollection.__init__(self, 'IPRoute', device)
		self.SignificantProperty = 'Route'
		self.ComponentName = 'IPRoute'
		self.ComponentClass = IPRoute
		self.SecondProperty = 'Mask'
	
	def Status(self):
		pass
		
	def Add(self, route, mask = '', dest = '', metric = '', default = False): 
		r = IPRoute(self, route, mask, dest, metric, default)
		self.Components.append(r)
		
	def NextHop(self, route):																	# get next hops for a route
		res = self.Device.Command(f'show ip route {route}')
		m = re.search('(\d+\.\d+\.\d+\.\d+)/(\d+)', res.output)
		if m is not None:
			nhs = [r for r in self if r.Param('Route') == m.group(1) and r.Param('Mask') == m.group(2) and r.Param('Summary') == False]
			return nhs
	
	def Flagged(self, rtype):																	# return routes flagged by type .Flagged('static')
		items = [r for r in self if rtype in r.Param('Flags')]
		newcoll = self.__class__(self.Device)													# create new collection 
		for i in items:
			newcoll.Components.append(i)
		return newcoll
		
# end class

class IPRoute(Component):
	def __init__(self, table = None, route = '', mask = '', dest = '', metric = '', default = False):
		Component.__init__(self, coll = table, sp = '', config = '')
		self.Parameters['Route'] = route
		self.Parameters['Mask'] = mask
		self.Parameters['Destination'] = dest
		self.Parameters['Metric'] = metric
		self.Parameters['Default'] = default											# default route if true
		self.Parameters['Flags'] = []
		self.Parameters['Summary'] = False
		self.Parameters['Timestamp'] = ''
		self.SPValue = self.Param('Route')
		
	def __repr__(self):
		return f'IP Route {self.Param("Route")}'
	
# end class