#!/home/repos/public/Python/bin/python3.6
# TescoCE switch audit. Ian Butterworth. July 2022
# v0.0

from ios_device import IOSDevice
from credentials import Credentials
#from cinfo import Customer
from multiprocessing import Pool
from functools import wraps

import os,sys,getopt,re,time,socket,logging,traceback,datetime
from fnmatch import fnmatch

def Prompt(message):
	if noprompt:																			# bypass prompts
		return True
	choice = input(message)
	if choice and choice.lower() == 'y':
		return True
	return False
# end function

# wrapper for multiprocessing worker function
def trace_unhandled_exceptions(func):
	@wraps(func)
	def wrapped_func(*args, **kwargs): 
		result = None 
		try: 
			result = func(*args, **kwargs) 
		except: 
			print ('Exception in ' + func.__name__)
			print ('Arguments: ' + str(args))
			traceback.print_exc() 
		return result 
	return wrapped_func
# end func

# mp worker function with wrapper to catch exceptions
@trace_unhandled_exceptions
def worker(host, c, settings):											# worker process for multi-processing
	st = Status(host, settings.get('verbose'), settings.get('lenhost'))
	st.Output('Connecting')
	dev = IOSDevice(host,c.UserID, c.Password, logging = settings.get('logging'))			# connect to device. 
	if dev.Reachable == False:
		st.Output('Device not reachable!')
		return st
		
	if dev.Connect(fast_cli = not settings.get('slow')) == False:
		st.Output('Unable to connect!')
		return st

	helpers = []
	dhcps = []
	acls = []
	st.Output('Connected.')
	dev.DeviceInfo.Get()																	# show version
	st.Output(' '.join([dev.DeviceInfo.Param(p) for p in ['Hostname','Model','Version']]))
	dev.Configuration.Get()
	dev.Interfaces.Get()
	vlans = dev.Interfaces.Filter('Type','Vlan')											# vlan interfaces
	htotal = 0
	for v in vlans:
		htotal += len(v.Param('iphelpers'))
		for h in v.Param('iphelpers'):
			helpers.append(','.join([dev.DeviceInfo.Param('Hostname'), v.Param('Name'), h]))
	dev.DHCPPools.Get()
	for d in dev.DHCPPools:
		o43 = next((o[1] for o in d.Param('options') if o[0] == '43'), '')
		dhcps.append(','.join([dev.DeviceInfo.Param('Hostname'), d.Param('Name'), d.Param('network'), d.Param('mask'), d.Param('default-router'), o43, d.Param('lease')]))
		
	dev.IPAccessLists.Get()
	dev.AccessLists.Get()
	for a in dev.AccessLists:
		acsv = a.toCSV(False).splitlines()
		for c in acsv:
			acls.append(','.join([dev.DeviceInfo.Param('Hostname'),c]))
	st.Output(f'{dev.DeviceInfo.Param("Hostname")} Vlans: {len(vlans)}, IP Helpers: {htotal}, DHCP Pools: {len(dev.DHCPPools)}, Access Lists: {len(dev.AccessLists) + len(dev.IPAccessLists)}')
	for a in dev.IPAccessLists:
		acsv = a.toCSV(False).splitlines()
		for c in acsv:
			acls.append(','.join([dev.DeviceInfo.Param('Hostname'),c]))

	return (helpers, dhcps, acls)
# end function

class Status(object):
	def __init__(self, host, verbose = False, length = 10):
		self.Host = host
		self.Status = ''
		self.Verbose = verbose
		self.formatStr = f'%s %-{length}s: %s'
	
	def Output(self, message):
		self.Status = message
		now = datetime.datetime.now()
		print(self.formatStr%(now.strftime('%H:%M:%S'),self.Host,message))
		
# end class
	
def usage():
	print ('tescoce-switch-audit.py <options> [devices]')
	print ('options:')
	print (' %-40s %s'%('-d, --devices <devices file>','Specify devices file. (List of devices, one per line.)'))
	print (' %-40s %s'%('-u, --user <userid>','Specify login userid.'))
	print ('Troubleshooting options:')
	print (' %-40s %s'%('-l, --logging','Log debug output to files.'))
	print (' %-40s %s'%('--clear','Clear cached credentials.'))
	print (' %-40s %s'%('--noconn','Run script but do not connect to any devices.'))
	print (' %-40s %s'%('--processes <n>','Number of parallel processes (default:5)'))
	
	sys.exit()
# end function

#************************ Main ***********************

domhost = socket.gethostname()									# host name e.g. pdcd05-tools1a or ip
hosts = []														# hosts to be upgraded
customer = ''													# cinfo customer name - for retrieving enable password
mainmodule = sys.modules[__name__]
reloadoptions = dict( wait = True, option = '', time = '')		# reload options
settings = dict(noconn = False,verbose = False,logging = False,slow = False)
secret = None													# secret credentials	
user = ''														# staging userid
clear = False													# clear cached credentials option
processes = 1													# max number of parallel processes
maxitems = 0									# 0 = all
chunksize = 100
progresscount = 0
startat = 0

print ('TescoCE switch audit v0.0')

if len(sys.argv) > 1:
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'd:lp:u:', ['clear','customer=','user=','noconn','logging','verbose','processes=','slow','devices='])
		
	except getopt.GetoptError as e:
		print (e)
		usage()
		
	for opt, arg in opts:
		if opt in ('-u','--user'):
			user = arg
		elif opt == '--clear':
			print ('Removing cached credentials.')
			clear = True
		elif opt in ('--noconn','--verbose','--slow'):
			settings[opt[2:]] = True
		elif opt in ('-l', '--logging'):
			print ('Device logging enabled')
			settings['logging'] = True
		elif opt in ['-p','--processes']:
			processes = int(arg)
		elif opt in ('-d','--devices'):													# input file
			with open(arg) as fin:
				hosts = [line.strip() for line in fin]									# one device per line
		elif opt == '--customer':
			customer = arg
		
	if len(args) > 0:
		hosts = args
		maxitems = len(hosts)
				
if hosts == []:
	print ('No hosts specified!')
	usage()
		
c = Credentials(user, useos = True, prompt = True)										# use cached credentials. will prompt first time.
if c.Source == 'File':
	if clear:
		c.Remove()
		sys.exit()
	else:
		print (f'Using cached credentials for {c.UserID}.')

settings['lenhost'] = max([len(h) for h in hosts])										# get longest host name
if settings.get('slow'):
	print ('%-10s: %s'%('Timeouts','Increased'))
print ('%-10s: %s'%('Devices',len(hosts)))
			
if settings.get('noconn'):
	sys.exit()
	
csvfiles = [{'index':0,'filename':'iphelpers','handle':None, 'titles':'hostname,vlan,ip helper-address\n'},
	{'index':1,'filename':'dhcppools','handle':None, 'titles':'hostname,pool name,network,mask,gateway,option 43,lease\n'},
	{'index':2,'filename':'acls','handle':None, 'titles':'hostname,acl,rule,action,protocol,source,source port,destination,dest port,logging\n'}]
now = datetime.datetime.now()
timestamp = now.strftime("%d%m%Y-%H%M")
for file in csvfiles:
	filename = f"tescoce-{file.get('filename')}-{timestamp}.csv"																# tescoce-iphelpers-04062018-1411.csv
	handle = open(filename, 'a')																								# open file
	file['handle'] = handle
	file['filename'] = filename
	handle.write(file['titles'])
	print ('%-10s: %s'%('Output', filename))
																												# multi-processing in chunks
for start in range(startat, maxitems, chunksize):																# startat == 0 unless resuming
	end = start + chunksize if start + chunksize < maxitems else maxitems
	print (f'Range: {start} to {end}')
	pool = Pool(processes = processes)                                                                          # define multiprocessing pool
	procs = [pool.apply_async(worker, args = (h,c,settings)) for h in hosts[start:end] ]  				   		# must have comma in args - its a tuple....
	output = [p.get() for p in procs]   

	for v in csvfiles:
		data = '\n'.join(['\n'.join(o[v.get('index')]) for o in output if o[v.get('index')] != []])
		if len(data) > 0:
			v.get('handle').write(data)

