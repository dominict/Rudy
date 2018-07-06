from UI import *
from Functions import MatterFunctions as MtrFuncs,CONN, ClientFunctions as ClntFuncs
from ScreenControl import *

from datetime import datetime as dt

class ClientMatter(QtGui.QMainWindow):
    def __init__(self, client, clientnum, matter = None):
        
        QtGui.QMainWindow.__init__(self)
        self.ui = loadUi(UIDir + "\\MatterWindow.ui",self)
        
        self.client = client
        self.clientnum = clientnum
        self.matter = matter
            
        self.changes = False
        self.action = None
        
        self.ui.dateOpened.setDate(QtCore.QDate(dt.today().date()))
        self.ui.dateClosed.setSpecialValueText('Not Closed')
        self.ui.dateClosed.setDate(self.ui.dateClosed.minimumDate())
        self.ui.useClientAddress.clicked.connect(self.populateClientAddress)
        
        self.listMatterTypes()
        self.loadStates()
        self.lockWindow()

        if self.matter is None:
            self.newMatter(self.clientnum )
        else:
            self.loadMatter()
            
        for i in dir(self.ui):
                exec("initializeChangeTracking(self,self.ui.{})".format(i))
        
        self.ui.actionClose.triggered.connect(self.closeWindow)
        self.ui.actionEdit.triggered.connect(self.editMatter)
        self.ui.actionSave.triggered.connect(self.saveChanges)
            
    def lockWindow(self ):
        for i in dir(self.ui):
            exec("""self.setLocks(self.ui.{},True)""".format( i ))
    
    def unlockWindow(self ):
        for i in dir(self.ui):
            exec("""self.setLocks(self.ui.{},False)
    """.format( i ))
        
    def setLocks(self,widget,locked):
        
        if isinstance(widget,QtGui.QLineEdit):
            widget.setReadOnly(locked)
        elif isinstance(widget,(QtGui.QComboBox,QtGui.QDateEdit,QtGui.QToolButton, QtGui.QPushButton)):
            widget.setDisabled(locked)
            
    def newMatter(self , clientNum):
        nextMatter = MtrFuncs.nextMatterNum(clientNum)
        self.ui.clientNum.setText(clientNum)
        self.ui.matterNum.setText(nextMatter)
        self.action = 'new'
        self.unlockWindow()
        
        self.ui.clientNum.setReadOnly(False)
        
    def loadMatter(self):
        self.ui.clientNum.setText(str(self.matter.clientnum))
        self.ui.matterNum.setText(str(self.matter.matternum))
        
        
            
    def editMatter(self ):
        reply = checkChangesMade(self)
        if reply == 0:
            if self.action is None:
                self.unlockWindow()
                self.action = 'update'
                self.ui.clientNum.setReadOnly(True)
                self.ui.matterNum.setReadOnly(True)
                self.ui.actionEdit.setText('Cancel Edit')
            elif self.action == 'update':
                self.action = None
                self.lockWindow()
                self.ui.actionEdit.setText('Edit')
                
    def saveChanges(self):
        
        alert = QtGui.QMessageBox()
        if self.action is not None:
            if self.ui.matterNum == '':
                alert.setText("Missing Matter Number")
                alert.setWindowTitle('Need Matter Number')
                alert.exec_()
                return
            if self.ui.matterType.currentIndex() == 0:
                alert.setText("Missing Matter Type")
                alert.setWindowTitle("Need Matter Type")
                alert.exec_()
                return
            if self.ui.dateClosed.date().toPyDate() > self.ui.dateClosed.minimumDate().toPyDate() and self.ui.boxNumber().text() == '':
                alert.setText("Closed matters require a box number.")
                alert.setWindowTitle('Box Number Needed')
                alert.exec_()
                return
            
        mattertype = self.ui.matterType.itemData(self.ui.matterType.currentIndex())
        
        data = {'action':self.action,
                'table':'ClientMatters',
                'values':{'FirstName':self.ui.firstName.text(),
                          'LastName':self.ui.lastName.text(),
                          'MiddleInitial':self.ui.middleInitial.text(),
                          'BillingAddr1':self.ui.addr1.text(),
                          'BillingAddr2':self.ui.addr2.text(),
                          'BillingCity':self.ui.billCity.text(),
                          'BillingState':self.ui.billState.currentText(),
                          'BillingZip':self.ui.billZip.text(),
                          'DateOpened':str(self.ui.dateOpened.date().toPyDate()),
                          'AttorneyInitials':self.ui.attorneyInitials.text(),
                          'MatterTypeID':str(mattertype)
                          },
                'params':{}
                }
        
        if self.ui.dateClosed.date().toPyDate() > self.ui.dateClosed.minimumDate().toPyDate():
            data['values']['DateClosed'] = str(self.ui.dateClosed.date().toPyDate())
            data['values']['BoxNumber'] = self.ui.boxNumber.text()
            
        if self.action == 'new':
            key = 'values'
        else:
            key = 'params'
        data[key]['ClientNum'] = self.ui.clientNum.text()
        data[key]['MatterNum'] = self.ui.matterNum.text()
        
        CONN.connect()
        CONN.saveData(data)
        CONN.closecnxn()
        
        self.changes = False
        self.action = None
        self.lockWindow()
        alert.setText("Save Complete")
        alert.setWindowTitle("Save")
        alert.exec_()
        
    def populateClientAddress(self):
        clientInfo = ClntFuncs.getClientInfo(self.clientnum)
        
        self.ui.firstName.setText(clientInfo.firstname[0])
        self.ui.lastName.setText(clientInfo.lastname[0])
        self.ui.middleInitial.setText(clientInfo.middleinitial[0])
        self.ui.addr1.setText(clientInfo.address1[0])
        self.ui.addr2.setText(clientInfo.address2[0])
        self.ui.billCity.setText(clientInfo.city[0])
        self.ui.billZip.setText(clientInfo.zipcode[0])

        ind = self.ui.billState.findData(clientInfo.state[0])
        if ind > 0:
            self.ui.billState.setCurrentIndex(ind)
        
    def listMatterTypes(self):
        matterTypes = MtrFuncs.listMatters()
        
        self.ui.matterType.addItem("")
        for i, m in enumerate(matterTypes.index):
            self.ui.matterType.addItem(matterTypes.matterdescr[m])
            self.ui.matterType.setItemData(i+1, matterTypes.typeid[m])
            
    def loadStates(self ):
        
        self.ui.billState.addItem("")
        i = 1
        for name, abbrv in stateGenerator():
            self.ui.billState.addItem(abbrv)
            self.ui.billState.setItemData(i,abbrv)
            i += 1
    
    def closeWindow(self):
        self.close()
    
    def closeEvent(self, *args, **kwargs):
        reply = checkChangesMade(self)
        if reply == 0:
            return QtGui.QMainWindow.closeEvent(self, *args, **kwargs)
            