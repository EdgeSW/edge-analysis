#Functions, methods to deal with REST communication with Simscore

import pycurl
import cStringIO
import ast
import json

class RESTfields(object):
	def __init__(self, address=None, header=None, values=None, isverbose=True, newcookie=False):
		self.header = header
		self.address = address
		self.values = values
		self.isverbose = isverbose
		self.newcookie = newcookie
		
	def print_post(self):
		print 'Posting: ' + str(self.values)
		print 'to website: ' + str(self.address)
		print 'using header:' + str(self.header)

		
	def posthttp(self, c):
		'''post content to a web address using pycurl'''
		buf  = cStringIO.StringIO()
		
		c.setopt(c.URL, self.address)
		c.setopt(c.HTTPHEADER, self.header)
		if self.values:
			c.setopt(c.POSTFIELDS, self.values)
			c.setopt(c.WRITEFUNCTION, buf.write)
		if self.newcookie:
			c.setopt(c.COOKIEFILE, '')
		c.setopt(c.VERBOSE, self.isverbose)
		c.perform()
		#c.close()

		return c, buf
	
	
	def loginSimscore(self, c):
		'''Login to Simscore with Grading account'''
		if self.address==None: self.address='http://simscore.org/simscores-v1/user/login'
		if self.values==None: self.values = json.dumps({'username': 'grading', 'password': 'r*tFQqmb'})
		if self.header==None: self.header = ['Content-Type: application/json']
		self.newcookie = True
		
		return self.posthttp(c)
	
	
	def logoutSimscore(self, c):
		"""Logout from Simscore"""
		#c = pycurl.Curl()
		if self.address==None: self.address = 'http://simscore.org/simscores-v1/user/logout'
		if self.header==None: self.header = ['Content-Type: application/json']
		
		c, buf = self.posthttp(c)
		c.close()
		return c
		#c.setopt(c.URL, )
		#c.setopt(c.POST, 1)
		#c.setopt(c.HTTPHEADER, )
		#c.setopt(c.VERBOSE, True)

	
def getSkillSimscore(c):
	"""GET json of AUA users from Simscore given previous login & global cookie"""
	
	auausers = cStringIO.StringIO()
	
	c.setopt(c.URL, 'http://simscore.org/simscores-v1/auainfo')
	c.setopt(c.HTTPHEADER, ['Content-Type: application/json'])
	c.setopt(c.HTTPGET, 1)
	#c.setopt(c.VERBOSE, True)
	c.setopt(c.WRITEFUNCTION, auausers.write);
	c.perform()
	#Given the string in auausers, convert to dict
	xx = ast.literal_eval(auausers.getvalue())
	aua_skill = {}
	for u in xx:
		aua_skill[ u['uid']] = u['level'] #two values: user id and that user's level
	return aua_skill

#auausers = getSkillSimscore(c)
#print auausers

#c = logoutSimscore(c)

	
#c = pycurl.Curl()  
#c = loginSimscore(c)