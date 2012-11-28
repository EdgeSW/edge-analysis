#Functions, methods to deal with REST communication with Simscore

import pycurl
import cStringIO
import ast
import json

class Postfields(object):
	def __init__(self, address=None, user=None, pw=None, content=None):
		self.address = address
		self.user = user
		self.pw = pw
		self.content = content
		
	def print_post(self):
		print 'Posting to: ' + str(self.address)
		print 'User: ' + str(self.user)
		print 'Password: ' + str(self.pw)
		


def post(c, p):
	'''post content to a web address using pycurl'''
	c.setopt(c.URL, p.address)
	c.setopt(c.HTTPHEADER, ['Content-Type: application/json'])
	c.setopt(c.POSTFIELDS, '{"username":%s, "password":%s}'%(json.dumps(p.user), json.dumps(p.pw)) )
	c.setopt(c.COOKIEFILE, '')
	#c.setopt(c.VERBOSE, True)
	#c.setopt(c.WRITEFUNCTION, buf.write)
	c.perform()
	return c


def getSkillSimscore(c):
    """GET json of AUA users from Simscore given previous login & global cookie"""
    #c = pycurl.Curl()
    auausers = cStringIO.StringIO()
    
    c.setopt(c.URL, 'http://simscore.org/simscores-v1/auainfo')
    c.setopt(c.HTTPHEADER, ['Content-Type: application/json'])
    c.setopt(c.HTTPGET, 1)
    #c.setopt(c.VERBOSE, True)
    c.setopt(c.WRITEFUNCTION, auausers.write)

    c.perform()
    #Given the string in auausers, convert to dict
    xx = ast.literal_eval(auausers.getvalue())
    aua_skill = {}
    for u in xx:
        aua_skill[ u['uid']] = u['level'] #two values: user id and that user's level
    return aua_skill

#auausers = getSkillSimscore(c)
#print auausers

def logoutSimscore(c):
    """Logout from Simscore"""
    #c = pycurl.Curl()
    c.setopt(c.URL, 'http://simscore.org/simscores-v1/user/logout')
    c.setopt(c.POST, 1)
    c.setopt(c.HTTPHEADER, ['Content-Type: application/json'])
    #c.setopt(c.VERBOSE, True)
    
    c.perform()
    return c

#c = logoutSimscore(c)

	
	
#10.23.12 - written to retrieve aua user skill as per Martin's email 10/18/12
def loginSimscore(c):
	'''Login to Simscore with Grading account'''
	p = Postfields(address='http://simscore.org/simscores-v1/user/login', 
						user='grading', pw='r*tFQqmb')
	return post(c, p)
	
	    
#c = pycurl.Curl()  
#c = loginSimscore(c)