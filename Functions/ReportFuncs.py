from Functions import *

def compileTables():
    tables = [('[NortonAbert].[dbo].ClientInfo','ci'),('[NortonAbert].[dbo].ClientMatters', 'cm'),('[NortonAbert].[dbo].MatterTypes','mt'),('[NortonAbert].[dbo].AdverseParties','ap')]
    q = "SELECT * FROM {} "
    CONN.connect()
    results = []
    for t in tables:
        data = CONN.readData(q.format(t[0]),[])
        
        results.append([t[0], data.columns,t[1]])
        
    return results


def runSearch(selection, filters, values):
    q = """
    
    SELECT DISTINCT {}
    FROM [NortonAbert].[dbo].ClientInfo ci
        LEFT JOIN [NortonAbert].[dbo].ClientMatters cm on ci.ClientNum = cm.ClientNum
        LEFT JOIN [NortonAbert].[dbo].MatterTypes mt on cm.MatterTypeID = mt.TypeID
        LEFT JOIN [NortonAbert].[dbo].AdverseParties ap on cm.ClientNum = ap.ClientNum AND ap.MatterNum = cm.MatterNum
    {}
    
    """.format(', '.join(selection), filters)
    
    CONN.connect()

    data = CONN.readData(q, values)
    CONN.closecnxn()
    
    return data