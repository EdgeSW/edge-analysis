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

    def __str__(self):
        return 'Posting: '+str(self.values)+' to endpoint: '+str(self.address)+' using header: '+str(self.header)

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

    

def loginSimscore(address=None):
    '''Login to Simscore with Grading account'''
    c = pycurl.Curl() 
    p = RESTfields(address=address, header=['Content-Type: application/json'], newcookie=True)
    
    if address==None: p.address='http://simscore.org/simscores-v1/user/login'
    p.values = json.dumps({'username': 'grading', 'password': 'r*tFQqmb'})
    
    return p.posthttp(c)


def logoutSimscore(c, address=None):
    """Logout from Simscore"""
    p = RESTfields(address=address, header=['Content-Type: application/json'])
    if p.address==None: p.address = 'http://simscore.org/simscores-v1/user/logout'
        
    c, buf = p.posthttp(c)
    c.close()
    return c, buf
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


def extract_cookies(pycurlobj):
    """  Extract cookies from previous curl."""
    # Example of line:
    # www.google.com\tFALSE\t/accounts/\tFALSE\t0\tGoogleAccountsLocale_session\ten
    cookies = {}
    for line in pycurlobj.getinfo(pycurl.INFO_COOKIELIST):
        chunks = line.split('\t')
        cookies[chunks[-2]] = chunks[-1]
        cookies['expires'] = chunks[4]
    return cookies


import time
def is_expired_cookie(c):
    ''' test if cookie in pycurl object has expired'''
    try:
        if extract_cookies(c):
            return True if time.time() > int(extract_cookies(c)['expires']) else False
        else: return True
    except:
        raise ValueError, 'Cookie did not contain expiration date or is misformatted'
    
    