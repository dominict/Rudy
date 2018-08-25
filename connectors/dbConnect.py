from connectors import *
from pandas.io.sql import read_sql
class Connection:
    
    is_closed = True
    
    def connect(self, driver = "{SQL Server}",
                    server = None,
                    database = PATH + "\\NortonAbert.db",
                    username = "",
                    pwd = "",
                    auto_commit = True):
        
        
        if not self.is_closed:
            self.closecnxn()
            
        if DEMO == 1:
            self.cnxn = sqlite3.connect(database)
        else:
            string = "DRIVER="+driver+";SERVER="+server+";DATABASE="+database+";UID="+username+";PWD="+pwd
            self.cnxn = odbc.connect(string,autocommit = auto_commit)
        
    def closecnxn(self):
        self.is_closed = True
        self.cnxn.close()
        
    def writeData(self,query,params):
        
        if self.is_closed == True:
            self.connect()
            
        cursor = self.cnxn.cursor()
        
        query = query
        result = cursor.execute(query,params)
        
        cursor.close()
        self.cnxn.commit()
        return result
        
    def readData(self,query,params = []):
        if self.is_closed == True:
            self.connect()
        
        query = query
        data = read_sql(query,self.cnxn, params = params)
        self.cnxn.cursor().close()
        return data
    
    def saveData(self,data):
        action = data['action']
        if action == 'new':
            q = "INSERT INTO "+data['table']+" ("
            qa = []
            qb = []
            vals = []
            
            for key in data['values'].keys():
                qa.append(key)
                qb.append("?")
                vals.append(str(data['values'][key]))
                
            q += ",".join(qa) + ") VALUES ("
            q += ",".join(qb) +")"
            
        elif action == 'update':
            q = "UPDATE " + data['table'] +" SET "
            qa = []
            vals = []
            for key in data['values'].keys():
                qa.append(str(key) + " = ?")
                vals.append(str(data['values'][key]))
                
            q += ",".join(qa)
            
            qb = []
            for key in data['params'].keys():
                qb.append(str(key)+ " = ?")
                vals.append(str(data['params'][key]))
            q += " WHERE "+ " AND ".join(qb)
            
            
        elif action == 'delete':
            q = "DELETE FROM "+data['table']+" WHERE " + " AND ".join([str(key)+ " = ?" for key in data['params'].keys()])
            
            vals = [str(data['params'][key]) for key in data['params'].keys()]
        
        return self.writeData(q,vals)