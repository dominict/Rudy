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
    q = """SELECT  cm.*, mt.matterdescr
            FROM ClientMatters cm 
                LEFT JOIN MatterTypes mt on cm.mattertypeid = mt.typeid 
            WHERE cm.ClientNum = ?"""
    v = [str(clientnum)]
    
    CONN.connect()
    data = CONN.readData(q,v)
    CONN.closecnxn()
    
    for r, i in enumerate(data.index):
        yield r, data.loc[i]

def nextMatterNum(clientNum):
    q = """
    SELECT MAX(CAST( MatterNum as INT)) +1 as next_matter
    FROM ClientMatters
    WHERE ClientNum = ? 
    """
    v = [str(clientNum)]
    CONN.connect()
    data = CONN.readData(q,v)
    CONN.closecnxn()
    
    if data.next_matter[0] is None:
        nextNum = '01'
    else:
        numForm = '00'
        number = str(data.next_matter[0])
        nextNum = numForm[:-len(number)]+number
    return nextNum
        
    

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

def generateAdverPartyList(clientnum,matternum):
    q = "SELECT * FROM AdverseParties WHERE ClientNum = ? AND MatterNum = ?"
    v = [str(clientnum),str(matternum)]
    CONN.connect()
    data = CONN.readData(q,v)
    CONN.closecnxn()
    
    for r, i in enumerate(data.index):
        yield r, data.loc[i]
        
def generateDocumentList(clientnum, matternum):
    q = "SELECT * FROM OriginalDocuments WHERE ClientNum = ? AND MatterNum = ?"
    v = [str(clientnum),str(matternum)]
    CONN.connect()
    data = CONN.readData(q,v)
    CONN.closecnxn()
    
    for r, i in enumerate(data.index):
        yield r, data.loc[i]