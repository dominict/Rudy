from Functions import *

def listMatters(activeOnly = True):
   
    if activeOnly:
        where = ' WHERE Inactive = 0'
    else:
        where = ""
    
    q = """
    SELECT * FROM MatterTypes {}
    """.format(where)
    
    CONN.connect()
    data = CONN.readData(q,[])
    CONN.closecnxn()
    
    return data

def generateClientMatters(clientnum):
    q = "SELECT * FROM ClientMatters WHERE ClientNum = ?"
    v = [str(clientnum)]
    
    CONN.connect()
    data = CONN.readData(q,v)
    CONN.closecnxn()
    
    for r, i in enumerate(data.index):
        yield r, data.loc[i]
        
def findMatter(matternum):
    q = """SELECT cm.*, mt.matterdescr
            FROM ClientMatters cm 
                INNER JOIN MatterTypes mt on cm.mattertypeid = mt.typeid
            WHERE MatterNum = ?"""
    v = [str(matternum)]
    CONN.connect()
    data = CONN.readData(q,v)
    CONN.closecnxn()
    
    return data