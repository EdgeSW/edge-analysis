import pickle

def appendOrCreate(adict, akey, toappend):
    '''given a dictionary, its key, and a value to append, create an entry of 
that value if it does not exist (as a list, duh) or append that value to list so
long as that value is not already there. If you want to do the first part, but not
the second part just use adict.setdefault(akey, []).append(toappend), dummy'''
    #check if key, if not, make and append
    if akey not in adict.keys():
        adict[akey] = [toappend]
    #if key, check if value
    elif toappend not in adict[akey]:
        adict[akey].append(toappend)
    #no need to return, original dict modified
    
def load_pickle(filepath, ftype='r'):
    '''opens and closes pickled file and returns contained pickleobj'''
    
    f = open(filepath, ftype)
    contents = pickle.load(f)
    f.close()
    return contents    

def save_pickle(content, filepath, ftype='w'):
    
    f = open(filepath, ftype)
    xx = pickle.dump(content, f)
    f.close()
    return xx

def lists_contain_same(lis1, lis2):
    if lis1 == lis2:
        return True
    if len(lis1)!=len(lis2):
        return False
    for item in lis1:
        if item not in lis2:
            return False
    for item in lis2:
        if item not in lis1:
            return False
    return True
