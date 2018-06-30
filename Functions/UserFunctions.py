from Functions import *

def validateUserChange(username):
    
    q = """ 
    SELECT (SELECT COUNT(username) userck FROM UserParam WHERE username = ?) as usrchk
        , (SELECT COUNT(1) admins FROM UserParam WHERE Admin = 1 AND Inactive = 0) as admchk
        , (SELECT COUNT(1) as actives FROM UserParam WHERE Inactive = 0) inactivechk
    
    """
    v = [username]
    
    CONN.connect()
    data = CONN.readData(q,v)
    CONN.closecnxn()
    
    return data

def getUserList(activeOnly = True):
    if activeOnly:
        where = ' WHERE Inactive = 0 '
    else:
        where = ''
    q = "SELECT * FROM UserParam {} ".format(where)
    
    CONN.connect()
    data = CONN.readData(q,[])
    CONN.closecnxn()
    
    return data
        