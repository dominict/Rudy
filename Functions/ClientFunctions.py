from Functions import *

        
def listClients(nameFilters, addrFilters, contactFilters):
    
    q = "SELECT ci.* FROM ClientInfo ci "
    v = []
    CONN.connect()
    data = CONN.readData(q,v)
    CONN.closecnxn()
    for r, i in enumerate(data.index):
        yield r, data.loc[i]
        
def getClientInfo(clientNum):
    q = "SELECT * FROM ClientInfo WHERE ClientNum = ?"
    v = [str(clientNum)]
    CONN.connect()
    data = CONN.readData(q,v)
    CONN.closecnxn()
    
    return data