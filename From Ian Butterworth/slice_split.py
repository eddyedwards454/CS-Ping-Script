# slice_split.py - Split and Slice text. Ian Butterworth Sept 2021
# v0.4 	26-09-22 A few refinements...
# v0.3  19-07-22 Added Splitter().
# v0.2	12-11-21 Added .Titles() to Slicer, format option for output
# v0.1	24-09-21 Allow Slice.End to be -1
# v0.0

# Classes in this module:
# Slicer - parse and slice delimited text into columns. Convert to CSV, XML
# Slice - text slice definition
# Splitter - split text into lines, or lines into words

from xml.etree import ElementTree as ET
import re

# Slice text into columns.
class Slice(object):																# define a string slice
	def __init__(self, start, end = 0):
		self.Start = start
		self._End = end
		self.Status = False															# invalid if False
		self.Count = 0
		
		if isinstance(start, int):													# Slice(0, 10)
			self.Start = start
			self.End = end
		elif isinstance(start, str):												# Slice('0:10')
			if ':' in start:
				st,en = start.split(':')
				self.Start = int(st)
				self.End = int(en)
			else:
				self.Start = int(start)												# Slice('0', '10')
				self.End = int(end)

	@property
	def End(self):
		return self._End

	@End.setter
	def End(self, new_value):														# update Status when .End changes
		self._End = new_value
		if self._End >= self.Start:
			self.Status = True
		elif self._End == -1:
			self.Status = True
		else:
			self.Status = False
		
	def __repr__(self):
		return f'Slice: {self.Start}:{self.End} {"" if self.Status else "Invalid!"}'
	
	def __len__(self):
		return (self.End - self.Start)
		
	def __eq__(self, other):														# allows comparing of slices using ==
		return self.Start == other.Start and self.End == other.End
		
	def __gt__(self, other):
		return(self.Start >= other.Start and self.End >= other.End)					# allows sorting and comparing of slices using < and > 
		
	def Slice(self, text, strip = True):											# perform string slicing on a string. e.g: slice1.Slice('The  quick brown fox   ') => 'fox'
		if self.End == -1:
			st = text[self.Start:]
		else:
			st = text[self.Start:self.End]
		return st.strip() if strip else st
		
	def __contains__(self, a):														# allows 'in' operator to work. e.g:  if slice2.Start in slice1: ....
		return (a in range(self.Start, self.End))									# returns Boolean
		
# end class

class Slicer(object):
	def __init__(self, lines = [], skip = 0, file = '', auto = True, overlap = True, slices = None, debug = False):
		self.Slices = []															# list of slices. Can be auto-generated or manually specified
		#self.MaxSlices = 0															# max occurrences of slices
		self.Lines = lines if isinstance(lines, list) else lines.splitlines()		# text to parse/slice			
		self.AutoSlice = auto														# auto-slice
		self.Skip = skip															# initial lines to skip
		self.AllowOverlap = overlap													# allow overlapping slices
		self.debug = debug
		self.Titles = []									
		
		if self.debug:
			print (f'Slicer: Lines:{len(self.Lines)} Auto:{str(self.AutoSlice)}')
		if slices is not None:														# manual slices specified
			self.AutoSlice = False
			self.AddSlice(slices)
		
		if file:
			self.Open(file)
			
		if len(self.Lines) > 0 and self.AutoSlice:									# default: use first non-blank line
			if self.debug:
				print('Get slices from first non-blank line')
			for line in self.Lines:
				if len(line) > 0:
					if self.GetSlicesFromLine(line) > 1:
						if self.debug:
							print('- Using Line:' + line)
						self.Titles = line.split()									# assume it is the title line	
						break
			
	def __repr__(self):
		return f'Slicer Slices:{len(self.Slices)} Lines:{len(self.Lines)}'
	
	def FilterLines(self, ignoresequences):
		for ig in ignoresequences:
			self.Lines = [l for l in self.Lines if ig not in l]
		
	def FindLine(self, startswith):													# find a line starting with <something>
		index, line = next(((i,l) for (i,l) in enumerate(self.Lines) if l.startswith(startswith)), (0,''))
		return index,line
		
	def Words(self, line = '', index = 0):
		if line == '':
			line = self.Lines[index]
		if line != '':
			s = Splitter(line)
			return s
		
	def GetSlicesFromLine(self, line = '', index = 0, startswith = ''):
		self.Slices = []															# clear out any existing slices
		if startswith:
			index, line = self.FindLine(startswith)
		if line == '':
			line = self.Lines[index]
		words = self.Words(line = line, index = index)
		if len(words) > 0:
			cols = [line.index(w) for w in words]										# get columns indexes from words. Must be single words! 
			prev = cols[0]																# was: prev = 0
			slices = []
			if len(cols) > 1:
				for c in cols[1:]:
					self.AddSlice(prev, c)
					prev = c
				self.AddSlice(c, -1)
				return len(self.Slices)
			else:
				return 0
		else:
			return 0
		
	def GetSlicesFromText(self):														# determine slices from entire text
		self.Slices = []
		for line in self.Lines[self.Skip:]:
			if len(line) > 0:															# skip empty lines 
				prev = ' '																# initialise previous character
				if self.debug:
					print(f'Line: {line}')
				for i,c in enumerate(line):
					if c.isspace() == False and prev.isspace():							# current char is something and previous is space
						if self.debug:
							print(f'- {i}: Start')
						s = Slice(i)													# start a new slice
					elif c.isspace() and prev.isspace() == False:						# current is space, previous is something 
						if self.debug:
							print(f'- {i}: End')
						s.End = i														# end slice
						self._AddEx(s)
						
					prev = c
				# end for
				if s.End == 0:
					s.End = i
					if self.debug:
						print(f'- {i}: End (EOL)')
					self._AddEx(s)
			if self.debug:
				choice = input('Continue?')

		self.Slices.sort()																# likely to get out of order
		return len(self.Slices)

	def _AddEx(self, s):																# add and extend
		if s.Status:
			m = self.Overlap(s)															# check for overlap
			if m is not None:
				if s.Start < m.Start or s.End > m.End:									# overlap...adjust
					a = Slice(s.Start if s.Start < m.Start else m.Start, s.End if s.End > m.End else m.End)	# extended slice
					a.Count += m.Count													# carry any hits over
					if self.debug:
						print (f'- {s} Overlaps with {m}. Adjust: {a}')
					self.Slices.remove(m)												# remove smaller slice
					self._AddEx(a)														# recursive!!!
					
				m.Count += 1															# increment count
				if self.debug:
					print (f'- Existing Slice {m}.')
			else:
				if s.Status:
					if self.debug:
						print(f'- New {s}')
					self.Slices.append(s)												# new slice, add to list, if valid
	
	def Open(self, file):																# open a file and read delimited text
		with open(file) as fp:
			self.Lines = fp.read().splitlines()
		return len(self.Lines)
		
	def Output(self, skip = 0, format = 'csv', delim = ',',strip = True, tag = 'row'):	# apply the slicing to the text. Note: its a generator!
		for line in self.Lines[skip:]:
			if len(line) > 0:	
				output = []
				for s in self.Slices:
					output.append(s.Slice(line, strip = strip))
				if format == 'csv':														# output as csv
					yield (delim.join(output))
				elif format == 'list':													# output as list
					yield (output)
				elif format == 'xml':													# output as xml
					r = ET.Element(tag)
					for t,o in zip(self.Titles, output):
						sub = ET.SubElement(r, t)
						sub.text = o
					yield r
				elif format == 'dict':													# output as dict
					d = {}
					for t,o in zip(self.Titles, output):
						d[t] = o
					yield d
			
	def AddSlice(self, start, end = 0):													# for manually adding slices - is this redundant ? Combine with ._AddEx() ?
		newslices = None
		ret = False
		if isinstance(start, Slice):													# .AddSlice(Slice(0,10))
			newslices = [start]
		elif isinstance(start, int):													# .AddSlice(0, 10)
			newslices = [Slice(start, end)]
		elif isinstance(start, str):													
			if ',' in start:
				newslices = [Slice(s) for s in start.split(',')]						# .AddSlice('0:10,12:17,19:33')
			else:
				newslices = [Slice(start)]												# .AddSlice('0:10')		
		elif isinstance(start, list):
			newslices = [Slice(s) for s in start]										# .AddSlice('0:10','12:17','19:33')
		
		addcount = 0
		for ns in newslices:
			if ns.Status == False:
				break
			
			if self.AllowOverlap:
				self.Slices.append(ns)
			else:
				if self.Overlap(ns) == None:
					self.Slices.append(ns)		
		
	def Overlap(self, newslice):														# test newslice for overlap with existing slices
		for s in self.Slices:
			if (newslice.Start > s.End or newslice.End < s.Start) == False:
				return s
			
# end class

class Splitter(object):
	def __init__(self, text, splitchar = ' ', removeempty = True):
		self.Items = text.split(splitchar) if splitchar else text.split()
		if removeempty:
			self.Items = [t for t in self.Items if t != '']
		self.i = 0
		
	def __contains__(self, w):
		return bool(w in self.Items)
	
	def __getitem__(self, id):													# get a component   e.g. dev.Interfaces['Loopback0'] or dev.Interfaces[0]
		return self.Items[id]
			
	def __len__(self):
		return len(self.Items)
	
	def __repr__(self):
		return f'Splitter Items:{len(self)} Current:{self.i}'
		
	def __iter__(self, start = 0, end = 0):
	
		for w in self.Items[start:]:
			self.Inc()
			yield w
			
	def __reversed__(self):
		self.i = len(self)
		for w in reversed(self.Items):
			self.Dec()
			yield w
		
	def Inc(self, o = 1):
		self.i += o
	
	def Dec(self, o = 1):
		self.i -= o
			
	def Current(self):	
		return self.Items[self.i] if self.InRange(self.i) else ''
		
	def Next(self):
		self.Inc()
		return self.Current()
		
	def Previous(self):
		self.Dec()
		return self.Current()
			
	def Peek(self, i = 1):
		if self.InRange(self.i + i):
			return self.Items[self.i + i]  
		else:
			return ''
		
	def InRange(self, i):
		return bool(i in range(0, len(self.Items)))
		
	def Reset(self):
		self.i = 0
		
	def Test(self, pattern, o = 0):
		if self.InRange(self.i + o):
			return bool(re.match(pattern, self.Items[self.i + o]))
		else:
			return False
		
	def IsDigit(self):
		c = self.Current()
		return c.isdigit()
	
	def IsIPV4(self):
		return self.Test('[\d\.]+')
		
	def Remove(self, w):
		self.Items.remove(w)
		
	def Join(self, start, end, jointext = ' '):
		if self.InRange(start) and self.InRange(end):
			return ' '.join(self.Items[start:end])
		else:
			return ''
	
	def Filter(self, text):
		return [i for i in self.Items if text in i]
		
# end class
