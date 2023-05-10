# mac table parsing script. Ian Butterworth Sept 2022

# Parse 'show mac table ...' commands
# Output: MAC address, VLAN ID,  Interface 

from slice_split import Slicer
import sys, re, os


titlelines = {'3COM':'MAC ADDR ','Cisco':'Vlan ','HP':'  MAC Address','Juniper':'    name'} # match vendor based on title line
indexes = [{'vendor':'3COM', 'mac':0, 'vlan':1, 'port':3}, {'vendor':'Cisco', 'mac':1, 'vlan':0, 'port':3}, {'vendor':'HP', 'mac':0, 'port':1, 'vlan':2}, {'vendor':'Juniper', 'mac':1, 'port':4, 'vlan':0}]
files = []

if len(sys.argv) > 1:
	files = sys.argv[1:]			
else:
	print('** No input files!')
	print('Usage: python macs.py <input-file> [<input-file>...]')
	sys.exit(1)

for f in files:
	macs = []
	slicer = Slicer(file = f, auto = False)
	fpath, fext = os.path.splitext(f)
	slicer.FilterLines(['>','}','---','Total'])											# discard lines with certain sequences
	
	for vendor,t in titlelines.items():
		i, titleline = slicer.FindLine(startswith = t)							# look for title lines
		if len(titleline) > 0:	
			break																# found items
	
	if i == 0 and titleline == '':	
		print(f'** Unable to find title in file: {f}')
	else:
		vidx = next((v for v in indexes if v.get('vendor') == vendor), None)	# get vendor specific indexes
		if vidx is None:
			print(f'** unable to find Vendor Indexes: {vendor}')
			sys.exit(1)
		else:	
			for line in slicer.Lines[i + 1:]:
				mac = []
				c = line.split()
				if len(c) > 0:
					for t in ['mac','vlan','port']:
						v = c[vidx.get(t)]
						if t == 'mac':
							mac.append(re.sub('[:\-\.]', '', v))					# remove any/all punctuation chars in mac address
						else:
							mac.append(v)													
					macs.append(','.join(mac))
					
			output = '\n'.join(macs)		
		
			#print(output)
		with open(fpath + '.csv' , 'w') as fout:								# writes output as *.csv file
			fout.write('MAC,VLAN,Interface\n' + output)
			

			

