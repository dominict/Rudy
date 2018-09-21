from Functions import *

def validateUserChange(username):
    
    q = """ 
    SELECT (SELECT COUNT(username) userck FROM [NortonAbert].[dbo].UserParam WHERE username = ?) as usrchk
        , (SELECT COUNT(1) admins FROM [NortonAbert].[dbo].UserParam WHERE Admin = 1 AND Inactive = 0) as admchk
        , (SELECT COUNT(1) as actives FROM [NortonAbert].[dbo].UserParam WHERE Inactive = 0) inactivechk
    
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
    q = "SELECT * FROM [NortonAbert].[dbo].UserParam {} ".format(where)
    
    CONN.connect()
    data = CONN.readData(q,[])
    CONN.closecnxn()
    
    return data

def cleanOutDeletedAccounts(cutoffDate):
    
    q = """
    SELECT ClientNum
    FROM [NortonAbert].[dbo].ClientInfo
    WHERE Deleted = 1 AND DeleteDate <= ?
    """
    v = [str(cutoffDate)]
    
    q1 = "DELETE FROM [NortonAbert].[dbo].OriginalDocuments WHERE ClientNum = ?"
    q2 = "DELETE FROM [NortonAbert].[dbo].ClientMatters WHERE ClientNum = ?"
    q3 = "DELETE FROM [NortonAbert].[dbo].ClientInfo WHERE ClientNum = ?"
    q4 = "DELETE FROM [NortonAbert].[dbo].AdverseParties WHERE ClientNum = ?"
    CONN.connect()
    data = CONN.readData(q,v)
    
    for i in data.index:
        clientnum = [str(data.clientnum[i])]
        CONN.writeData(q1,clientnum)
        CONN.writeData(q2,clientnum)
        CONN.writeData(q3,clientnum)
        CONN.writeData(q4,clientnum)
        
    
    