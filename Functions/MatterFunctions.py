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

