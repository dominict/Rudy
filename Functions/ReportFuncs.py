from Functions import *

def compileTables():
    tables = [('ClientInfo','ci'),('ClientMatters', 'cm'),('MatterTypes','mt'),('AdverseParties','ap')]
    q = "SELECT * FROM {} LIMIT 1"
    CONN.connect()
    results = []
    for t in tables:
        data = CONN.readData(q.format(t[0]),[])
        
        results.append([t[0], data.columns,t[1]])
        
    return results


def runSearch(selection, filters, values):
    q = """
    
    SELECT DISTINCT {}
    FROM ClientInfo ci
        LEFT JOIN ClientMatters cm on ci.ClientNum = cm.ClientNum
        LEFT JOIN MatterTypes mt on cm.MatterTypeID = mt.TypeID
        LEFT JOIN AdverseParties ap on cm.ClientNum = ap.ClientNum AND ap.MatterNum = cm.MatterNum
    {}
    
    """.format(', '.join(selection), filters)
    
    CONN.connect()

    data = CONN.readData(q, values)
    CONN.closecnxn()
    
    return data