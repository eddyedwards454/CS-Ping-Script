# interface parsing script. Ian Butterworth Sept 2022

# Parse 'show interface ...' commands
# Output: Interface (stack/port), VLAN, speed/duplex, up/down status

from slice_split import Slicer
import sys, re, os

class Port(object):
	def __init__(self, d = {}, name = '', vlan = '', vendor = ''):
		self.Name = name
		self.Speed = ''							# 10,100,1000...
		self.Duplex = ''						# full|half
		self.Status = ''
		self.VLAN = vlan
		self.Vendor = vendor
		self.Host = ''
		
		if d != {}:
			for k,v in d.items():						# set values from Dictionary
				self.Set(k, v)

	def __repr__(self):
		return f'Port: {self.Name}'
		
	def Set(self, k, v):								# Set parameters. Reconcile vendor differences. e.g port.Set('Interface', 'Eth1/0')
		if k in ['Port','Interface']:
			self.Name = v
		elif k in ['Vlan','Untagged','PVID']:
			self.VLAN = v
		elif k == 'Speed':
			m = re.search('(\d+)([FH]Dx)?', v)
			if m is not None:
				self.Speed, dx = m.groups()
				if dx is not None:
					if dx == 'FDx':
						self.Duplex = 'Full' 
					if dx == 'HDx':
						self.Duplex = 'Half' 
		elif k == 'Duplex':
			if 'full' in v.lower():
				self.Duplex = 'Full'
			elif 'half' in v.lower():
				self.Duplex = 'Half'
			elif 'auto' in v.lower():
				self.Duplex = 'Auto'
		elif k in ['Link','Status']:
			if v in ['DOWN','Down','notconnect']:
				self.Status = 'Down'
			if v in ['UP','Up','connected']:
				self.Status = 'Up'
			if v in ['ADM DOWN','disabled','Down']:
				self.Status = 'Disabled'
				
	def toCSV(self, headers = True):
		output = ''
		if headers:
			output += ','.join(['Port','VLAN','Speed','Duplex','Status']) + '\n'
		output += ','.join([getattr(self, p,'') for p in ['Name','VLAN','Speed','Duplex','Status']]) + '\n'
		return output
# end class

titlelines = {'3COM':'Interface ','Cisco':'Port ','HP':'  Port ','Juniper':'Routing instance'} # match vendor based on title line
files = []

if len(sys.argv) > 1:
	files = sys.argv[1:]			
else:
	print('** No input files!')
	print('Usage: python interfaces.py <input-file> [<input-file>...]')
	sys.exit(1)

for f in files:
	ports = []
	slicer = Slicer(file = f, auto = False)
	fpath, fext = os.path.splitext(f)
	slicer.FilterLines(['>','}','---'])											# discard lines with certain sequences
	
	for vendor,t in titlelines.items():
		i, titleline = slicer.FindLine(startswith = t)							# look for title lines
		if len(titleline) > 0:	
			slicer.Titles = titleline.split()
			break																# found items
	
	if i == 0 and titleline == '':	
		print(f'** Unable to find title in file: {f}')
	else:
		if vendor == 'Juniper':
			slicer.Titles = ['Routing instance','VLAN name','Tag','Interfaces']
			slicer.GetSlicesFromText()
			vlan = ''
			for c in slicer.Output(format = 'list', skip = i + 1):
				if c[0]:														# default-switch          AP-Management         108      ''
					vlan = c[2]
				else:
					port = Port(name = c[3], vlan = vlan, vendor = vendor)
					ports.append(port)
		else:	
			slicer.GetSlicesFromLine(index = i)
			for c in slicer.Output(format = 'dict', skip = i + 1):
				port = Port(c, vendor = vendor)
				ports.append(port)
		output = ''		
		for i, p in enumerate(ports):
			output += p.toCSV(not(bool(i)))
		#print(output)
		with open(fpath + '.csv' , 'w') as fout:								# writes output as *.csv file
			fout.write(output)
			

			

