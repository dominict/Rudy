from Functions import *

        
def listClients(firstNames, lastNames, addrFilter, cityFilter, stateFilter, contactFilters):
    v = []
    
    qSearchs = []
    if firstNames != '':
        qSearchs.append( " (ci.firstname LIKE ? OR ci.spousefirstname LIKE ? )")
        v.extend(['%'+firstNames+'%','%'+firstNames+'%'])
        
    if lastNames != '':
        qSearchs.append( " ( ci.lastname LIKE ? OR ci.spouselastname LIKE ? )" )
        v.extend(['%'+lastNames+'%','%'+lastNames+'%'])
        
    if addrFilter != '':
        qSearchs.append("(ci.Address1 LIKE ? OR ci.Address2 LIKE ? )")
        v.extend(['%'+addrFilter+'%','%'+addrFilter+'%'])
    
    if cityFilter != '':
        qSearchs.append(" (ci.City LIKE ?)")
        v.append("%"+cityFilter+"%")
        
    if stateFilter != '':
        qSearchs.append("(ci.State LIKE ? )")
        v.append("%"+stateFilter+"%")
    
    if contactFilters != '':
        qSearchs.append(" (ci.Phone1 LIKE ? OR ci.Phone2 LIKE ? OR ci.Email LIKE ?) ")
        v.extend(['%'+contactFilters+'%','%'+contactFilters+'%','%'+contactFilters+'%'])
    
    if len(qSearchs) > 0:
        searches = ' WHERE {} '.format(" AND ".join(qSearchs))
    else:
        searches = ''
    q = """
    SELECT ci.* 
    FROM ClientInfo ci 
    {}
    ORDER BY ci.clientnum asc
    """.format(searches)

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

def compileAdversePartyList():
    q = "SELECT * FROM AdverseParties"
    v = []
    CONN.connect()
    data = CONN.readData(q,v)
    data['fullname'] = data.firstname + ' ' + data.middlename + ' ' + data.lastname
    CONN.closecnxn()
    print(data)
    return data