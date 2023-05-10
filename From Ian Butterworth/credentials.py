# credential handling library. Ian Butterworth Nov 2018
# v0.8  08-03-22	Added .Source property, updated expiry mechanism
# v0.7	11-11-21	Now uses Fernet encryption
# v0.6	10-11-21	Added Customer, modified fromCinfo()
# v0.5	08-10-21	Added Remove() and ChangePassword() methods
# v0.4 	17-05-21	Now works on Windows 10 as well as linux. Expiry feature added.
# v0.3 	16-04-21	Python 3 updates, files now 'hidden' using dot prefix
# v0.2	22-01-19	User mismatch check added, PromptUser() added, user and password validation added
# v0.1	02-01-19	Added Name, Entity, ReadFromFile, Saved properties
# v0.0

# Vz libraries
cinfoavailable = True
try:
	from cinfo import Entity,Customer										# conditional import
except:
	cinfoavailable = False

# system libraries
import os, getpass, base64, hashlib, re, string, datetime
from itertools import cycle
from cryptography.fernet import Fernet

class Credentials(object):
	def __init__(self, user = '', password = '', prompt = False, useos = False, autosave = True, verbose = False, name = '', entity = '', pwtype = '3', expires = '', cust = ''):			# c = Credentials(), c = Credentials('E529657'), c = Credentials(prompt = True)
		self.Home = ''														# home folder on OS
		self.UserID = ''
		self.Path = ''														# path to cached credentials
		self.Password = password
		self.Error = ''
		self.key = b''													
		self.AutoSave = autosave											# automatically save to file if True
		self.verbose = verbose												# print (debug messages)
		self.Name = name													# file name e.g. 'tacacs'. for reading userid/pw pair from file.
		self.Entity = entity												# cinfo entity name
		self.Customer = cust												# cinfo customer shortname
		self.CinfoPWType = pwtype											# cinfo password type e.g. cinfo -43
		self.Saved = False													# True when saved to file
		self.Mismatch = False												# True if 'user' does not match self.UserID
		self.Expires = None													# Expiry date if populated
		self.TimeStamp = None												# timestamp retrieved from encrypted data
		self.Source = ''													# Where did the credentials come from ? (File|Prompt|CINFO)
		
		if os.name == 'nt':													# Windows 
			self.Home = os.getenv('USERPROFILE') + '\AppData\Local'							
			self.osuser = os.getenv('USERNAME')
			self.osuid = ''													# no real equivalent 
		else:
			self.Home = os.getenv('HOME')									# get $HOME path - linux
			self.osuser = os.getenv('USER')
			self.osuid = str(os.getuid())

		self.oldkey = hashlib.md5((self.osuser + self.osuid).encode('utf-8')).hexdigest()		# generate a key unique to os user - not used - left here for reference
		
		if self.verbose:
			print ('init() name:%s prompt:%s useos:%s autosave:%s'%(name,str(prompt),str(useos),str(self.AutoSave)))
		
		self.GetKey()
		
		if expires:
			self.SetExpiry(expires)
		
		if self.Entity or self.Customer:										# get credentials from cinfo
			self.AutoSave = False												# don't want to save cinfo credentials to file
			self.fromCinfo(user)
		
		if self.Name:															# get credentials from named file
			self.fromFile(self.Name) 						
	
		if self.UserID == '':
			if user:
				self.UserID = user	
			elif useos:
				self.UserID = self.osuser										# use os user id if none supplied
			elif prompt:	
				self.PromptUser()												# prompt for a user id if not one

		if self.Password == '':													# if there is no pw so far	
			ret = self.fromFile(self.Name) if self.Name else self.fromFile()	# lookup file
			if ret == False:
				if user:
					self.UserID = user											# if name lookup fails, but there is a user, use it
				if prompt:														# prompt for pw
					self.Password = self.PromptPassword()
					if self.Expires is None:
						self.PromptExpiry()										# prompt for expiration date
					
		if self.Source == 'File':												# check if username read from file matches supplied user
			if user and self.UserID != user:
				if self.verbose:
					print ('UserID Mismatch %s %s'%(user, self.UserID))
				self.Mismatch = True

		elif self.AutoSave and self.Saved == False:                           	# save to file
			self.saveFile(self.Name)
					
		if self.verbose:
			print (' - UserID is "%s"'%(self.UserID))
			print (' - Password is "%s"'%(self.Password))
			
	def __repr__(self):
		return 'Credentials: ' + self.UserID
		
	def _setpath(self, filename = ''):											# set full path name of credentials file
		if filename:
			self.Path = self.Home + '/.' + filename + '.cred'					# use filename if there is one
		else:
			self.Path = self.Home + '/.' + self.UserID + '.cred'				# else use userid
		if self.verbose:
			print ('_setpath(): %s'%(self.Path))
	
	def GetKey(self):															# get encryption key
		keyfile = self.Home + '/.key'											# look for key file in path
		if os.path.exists(keyfile):
			with open(keyfile,'rb') as kf:
				if self.verbose:
					print ('_getkey(): Load key.')
				self.key = kf.read()
				
		if self.key == b'':														# generate new key
			if self.verbose:
				print ('_getkey(): Generate new key')
			self.key = Fernet.generate_key()
			with open(keyfile,'wb') as kf:
				kf.write(self.key)
	
	def RemoveKey(self):
		keyfile = self.Home + '/.key'											# look for key file in path
		if self.verbose:
			print (f'Delete key file {keyfile}.')
		if os.path.exists(keyfile):
			os.remove(keyfile)
		
	def ChangePassword(self, newpw = ''):										# prompt if new password is not supplied.
		if newpw == '':
			oldpw = self.PromptPassword(prmptxt = 'Enter Old Password for %s:')
			if self.Password == oldpw:
				newpw = self.PromptPassword(prmptxt = 'Enter New Password for %s:')
				verpw = self.PromptPassword(prmptxt = 'Re-Enter New Password for %s:')
				if newpw != verpw:
					print ('** Password mismatch!')
					return False
			else:
				print ('** Incorrect password!')
				return False
		
		if newpw:
			self.Password = newpw
			if self.Expires is not None:
				self.PromptExpiry()
			if self.AutoSave:
				self.saveFile()
			return True
		else:
			return False
	
	def Remove(self):															# remove file
		if self.verbose:
			print (f'Delete credential file {self.Path}.')
		os.remove(self.Path)
	
	def SetExpiry(self, expires):												# set the expiry as number of days:  .SetExpiry('60')  or absolute date: .SetExpiry('15/09/2022')
		if expires.isdigit():																	
			self.Expires = datetime.datetime.today() + datetime.timedelta(days = int(expires)) 
		elif expires:
			self.Expires = datetime.datetime.strptime(expires, '%d/%m/%Y')
		self.TimeStamp = datetime.datetime.today()
		
	def Expired(self):															# return True if expired
		today = datetime.datetime.today()
		if self.verbose:
			print (f'Expired(): today {today} expires {self.Expires}')
		return True if today > self.Expires else False	
		
	def Age(self):																# return age of password
		today = datetime.datetime.today()
		diff = today - self.TimeStamp 
		return diff
	
	def PromptPassword(self, prmptxt = 'Password for %s:', minlen = 3, caps = False, special = False, digits = False, retries = 3):	
		if self.verbose:
			print ('PromptPassword() for password, AutoSave:%s'%(str(self.AutoSave)))
		pwdprompt = prmptxt%(self.UserID) if '%s' in prmptxt else prmptxt
		ret = False
		for i in range(0, retries):
			pwd = getpass.getpass(pwdprompt)
			rl = True if len(pwd) >= minlen else False							# check min length
			rc = any(c.isupper() for c in pwd) if caps else True				# check for Capitals
			rs = any(c in string.punctuation for c in pwd) if special else True	# check for special chars
			rd = any(c.isdigit() for c in pwd) if digits else True				# check for digits
			ret = rl and rc and rs and rd
			if ret:
				break
			
			if self.verbose:
				print (' - Validation: %s'%(str(ret)))
		# end for
		self.Source = 'Prompt'
		return pwd
	
	def PromptUser(self, prmptxt = 'Enter User ID: ', validation = '.*', retries = 3):	# prompt for a userid
		if self.verbose:
			print ('PromptUser()' )
		ret = False
		for i in range(0, retries):
			user = input(prmptxt)		
			if re.match(validation, user):										# match user against regex pattern
				self.UserID = user
				ret = True
				break
			else:
				if self.verbose:
					print (' - UserID fails validation: %s: %s'%(user, validation))
		return ret
	
	def PromptExpiry(self, prmptxt = 'Enter Password Expiry as number of days, or date DD/MM/YY: '):
		if self.verbose:
			print ('PromptExpiry()' )
		exp = input(prmptxt)
		if exp:
			self.SetExpiry(exp)
			
	def fromFile(self, filename = ''):										# read creds from file
		ret = False
		if self.verbose:
			print ('fromFile() ' + self.Path)
			
		if not filename and not self.UserID:								# nothing to lookup
			if self.verbose:
				print (' - nothing to check, return.')
			return False
			
		self._setpath(filename)
		if os.path.exists(self.Path):
			if self.verbose:
				print (' - File exists')
			try:
				fp = open(self.Path, 'rb')
			except:
				self.Error = 'Unable to open ' + self.Path
				if self.verbose:
					print (self.Error)
			else:
				encstr = fp.read()
				decstr = self.Decrypt(encstr)
				if decstr is not None:
					fp.close()
					for line in decstr.splitlines():
						k,v = line.split(':')
						if k == 'Expires':
							self.Expires = datetime.datetime.strptime(v, '%d/%m/%Y')
						else:
							setattr(self, k, v)
				
					ret = True
				self.Source = 'File'
		else:
			if self.verbose:
				print (' - not found')
		return ret
				
	def saveFile(self, filename = ''):										# write creds to file
		self._setpath(filename)
		ret = False
		if self.verbose:
			print ('saveFile() ' + self.Path)
		try:
			fp = open(self.Path, 'wb')
		except:
			self.Error = 'Unable to open ' + self.Path
			if self.verbose:
				print (self.Error)
		else:
			data = f'UserID:{self.UserID}\nPassword:{self.Password}'
			if self.Expires is not None:
				data += f'\nExpires:{datetime.datetime.strftime(self.Expires,"%d/%m/%Y")}'
			fp.write(self.Encrypt(data))	
			self.Saved = True
			ret = True
		return ret
		
	def fromCinfo(self, user = '', idx = 0):									# get from cinfo		
		if cinfoavailable == False:
			return False
		ret = False
		
		if self.Entity:
			e = Entity(self.Entity, search = True)
		elif self.Customer:
			e = Customer(self.Customer, search = True)
		else:
			return False
			
		if self.verbose:
			print ('fromCinfo() Getting password from %s ID:%s Type:%s'%(str(e), user if user else self.UserID, self.CinfoPWType))
		if e.Status:
			crs = e.PasswordTypes[self.CinfoPWType].Get()
			if len(crs) > 0:
				c = crs[user] if user else crs[idx]								# select by user, or by index 
				if c is not None:
					self.Password = c.Password
					if self.UserID == '':
						self.UserID = c.ID
					ret = True
					self.Source = 'CINFO'
					if self.verbose:
						print (' - UserID:%s\n - Got password'%(self.UserID))
			else:
				self.Error = 'Credential Not found'
		else:
			self.Error = 'Entity not found'
		
		if self.verbose and self.Error:
			print (' - ' + self.Error)
		return ret
		
	def toBase64(self):														# return password b64 encoded
		return base64.b64encode(self.Password)
	
	def toBasic(self):														# return basic token
		return 'Basic ' + base64.b64encode(self.UserID + ":" + self.Password)
		
	def fromBase64(self, b64str):											# set user & pw from  b64 string
		if b64str.startswith('Basic '):										# strip off Basic prefix, if there
			b64str = b64str[6:]
		decstr = base64.b64decode(b64str).decode()
		if ':' in decstr:
			self.UserID, self.Password = decstr.split(':')
		else:
			self.Password = decstr
	
	def Encrypt(self, data):
		if self.verbose:
			print ('Encrypt() data: ' + data)
		f = Fernet(self.key)
		return f.encrypt(data.encode())
		
	def Decrypt(self, data):
		f = Fernet(self.key)
		try:
			self.TimeStamp = datetime.datetime.fromtimestamp(f.extract_timestamp(data))
			text = f.decrypt(data).decode()
		except Exception as e:
			self.Error = 'Unable to decrypt: ' + str(e)
			if self.verbose:
				print (self.Error)
		else:
			if self.verbose:
				print ('Decrypt() data: ' + text)
				print ('Timestamp: ' + self.TimeStamp.strftime('%d/%m/%Y %H:%m:%S'))	
			return text
		
	def oldEncrypt(self, data):												# xor encryption - not used - left here for reference
		#data = '%s:%s'%(self.UserID,self.Password) if self.Name else self.Password
		if self.verbose:
			print ('Encrypt() data: ' + data)
		xored = self.xor(data)
		return base64.b64encode(xored)
		
	def oldDecrypt(self, data):												# not used - left here for reference
		dec = base64.b64decode(data)							
		xored = self.xor(dec)
		if self.verbose:
			print ('Decrypt() data: '  + xored.decode())
		return xored.decode()												# return a string
	
	def xor(self, data):													# not used - left here for reference
		xd = data.encode() if isinstance(data, str) else data
		xk = self.key.encode() if isinstance(self.key, str) else self.key
		return bytes(a ^ b for a, b in zip(xd, cycle(xk)))
	
	def dump(self):
		print ('ID:%s PW:%s Path:%s Home:%s Err:%s'%(self.UserID, self.Password, self.Path, self.Home, self.Error))
# end class