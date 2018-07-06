from UI import *
from Functions import MatterFunctions as MtrFuncs,CONN, ClientFunctions as ClntFuncs
from ScreenControl import *

from datetime import datetime as dt
from subprocess import Popen

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
        self.ui.apClear.clicked.connect(self.clearPartyFields)
        self.ui.apSave.clicked.connect(self.saveAdverseParty)
        self.ui.apDelete.clicked.connect(self.removeAdverseParty)
        self.ui.apNew.clicked.connect(self.addAdverseParty)
        
        self.ui.partyList.cellClicked.connect(self.viewAdverseParty)
        
        self.listMatterTypes()
        self.loadStates()
        self.lockWindow()

        if self.matter is None:
            self.newMatter(self.clientnum )
        else:
            self.loadMatter()
            
        for i in dir(self.ui):
                exec("if {} not in ['apFirst','apLast', 'apMiddle', 'reason']: initializeChangeTracking(self,self.ui.{})".format(i,i))
        
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
        self.ui.attachDocument.setEnabled(False)
        self.ui.apSave.setEnabled(False)
        self.ui.apDelete.setEnabled(False)
        self.ui.apClear.setEnabled(False)
        
    def loadMatter(self):
        self.lockWindow()
        self.ui.clientNum.setText(str(self.matter.clientnum))
        self.ui.matterNum.setText(str(self.matter.matternum))
        
        self.ui.attorneyInitials.setText(self.matter.attorneyinitials)
        matterindex = self.ui.matterType.findData(int(self.matter.mattertypeid))
        if matterindex > 0:
            self.ui.matterType.setCurrentIndex(matterindex)
            
        self.ui.dateOpened.setDate(QtCore.QDate(dt.strptime(str(self.matter.dateopened),"%Y-%m-%d")))
        if self.matter.dateclosed is not None:
            self.ui.dateClosed.setDate(QtCore.QDate(dt.strptime(str(self.matter.dateclosed),"%Y-%m-%d")))
            self.ui.boxNumber.setText(self.matter.boxnumber)
        else:
            self.ui.dateClosed.setDate(self.ui.dateClosed.minimumDate())
            
        self.ui.firstName.setText(self.matter.firstname)
        self.ui.lastName.setText(self.matter.lastname)
        self.ui.middleInitial.setText(self.matter.middleinitial)
        self.ui.addr1.setText(self.matter.billingaddr1)
        self.ui.addr2.setText(self.matter.billingaddr2)
        self.ui.billCity.setText(self.matter.billingcity)
        
        stateindex = self.ui.billState.findData(self.matter.billingstate)
        if stateindex > 0:
            self.ui.billState.setCurrentIndex(stateindex)
        
        self.ui.billZip.setText(self.matter.billingzip)
        
        
        self.ui.attachDocument.setEnabled(True)
        self.ui.apSave.setEnabled(True)
        self.ui.apDelete.setEnabled(True)
        self.ui.apClear.setEnabled(True)
        self.ui.apNew.setEnabled(True)
        
        self.listDocuments()
        self.listAdverseParties()
        
    def listDocuments(self):
        """Listing Documents here"""
    
    def attachDocument(self):
        filename = QtGui.QFileDialog()
        
    def listAdverseParties(self):
        self.clearPartyFields()
        self.ui.partyList.setRowCount(0)
        
        for r, party in MtrFuncs.generateAdverPartyList(self.ui.clientNum.text(), self.ui.matterNum.text()):
            self.ui.partyList.insertRow(r)
            self.ui.partyList.setRowHeight(r,20)
            firstnamelabel = QtGui.QLabel(party.firstname)
            firstnamelabel.partyid = party.partyid
            cols = [firstnamelabel,
                    QtGui.QLabel(party.middlename),
                    QtGui.QLabel(party.lastname),
                    QtGui.QLabel(party.reasondescription)]
            
            populateTableRow(self.ui.partyList, r, cols)
    
    def addAdverseParty(self):
        self.ui.apFirst.action = 'new'
        self.ui.apFirst.setReadOnly(False)
        self.ui.apMiddle.setReadOnly(False)
        self.ui.apLast.setReadOnly(False)
        self.ui.reason.setReadOnly(False)
        
        self.ui.apDelete.setEnabled(False)
    
    def viewAdverseParty(self,row,col):
        firstnamelabel = self.ui.partyList.cellWidget(row,0)
        partyid = firstnamelabel.partyid
        self.ui.apFirst.setText(firstnamelabel.text())
        self.ui.apFirst.action = 'update'
        self.ui.apFirst.partyid = partyid
        
        self.ui.apMiddle.setText(self.ui.partyList.cellWidget(row,1).text())
        self.ui.apLast.setText(self.ui.partyList.cellWidget(row,2).text())
        self.ui.reason.setText(self.ui.partyList.cellWidget(row,3).text())
        
        self.ui.apFirst.setReadOnly(False)
        self.ui.apMiddle.setReadOnly(False)
        self.ui.apLast.setReadOnly(False)
        self.ui.reason.setReadOnly(False)
        
        self.ui.apDelete.setEnabled(True)
    
    def removeAdverseParty(self):
        if self.ui.apFirst.partyid is not None:
            self.ui.apFirst.action = 'delete'
            self.saveAdverseParty()
        
    def saveAdverseParty(self):
        firstname = self.ui.apFirst.text()
        lastname = self.ui.apLast.text()
        middleinitial = self.ui.apMiddle.text()
        reasonGiven = self.ui.reason.text()
        
        action = self.ui.apFirst.action
        
        if action is not None:
            partyid = self.ui.apFirst.partyid
            data = {'action':action,
                    'table':'AdverseParties',
                    'values':{'FirstName':firstname,
                              'LastName':lastname,
                              'MiddleName':middleinitial,
                              'ReasonDescription':reasonGiven},
                    'params':{}
                    }
        
            if action == 'new':
                key = 'values'
            else:
                key = 'params'
                data[key]['PartyID'] = partyid
            data[key]['ClientNum'] = self.ui.clientNum.text()
            data[key]['MatterNum'] = self.ui.matterNum.text()
            
            CONN.connect()
            CONN.saveData(data)
            CONN.closecnxn()
            
            self.listAdverseParties()
    
    def clearPartyFields(self):
        self.ui.apFirst.clear()
        self.ui.apFirst.action = None
        self.ui.apFirst.partyid = None
        self.ui.apLast.clear()
        self.ui.apMiddle.clear()
        self.ui.reason.clear()
        
        self.ui.apFirst.setReadOnly(True)
        self.ui.apMiddle.setReadOnly(True)
        self.ui.apLast.setReadOnly(True)
        self.ui.reason.setReadOnly(True)
            
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
        
        self.ui.attachDocument.setEnabled(True)
        self.ui.apSave.setEnabled(True)
        self.ui.apNew.setEnabled(True)
        self.ui.apClear.setEnabled(True)
        
        self.client.listMatters(self.clientnum)
        
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
            self.ui.matterType.setItemData(i+1, int(matterTypes.typeid[m]))
            
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
            