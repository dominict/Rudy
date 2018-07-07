from UI import *
from ScreenControl.Managers import MatterManager, UserManager
from ScreenControl import *
from ScreenControl import ClientMatters
from Functions import CONN, ClientFunctions as ClntFuncs, MatterFunctions as MtrFuncs
from functools import partial
from difflib import get_close_matches

class MainMatterScreen(QtGui.QMainWindow):
    def __init__(self, app):
        
        QtGui.QMainWindow.__init__(self)
        self.ui = loadUi(UIDir+"\\MainWindow.ui", self)
        
        self.activeUser = None
        self.changes = False
        self.action = None
        self.lockFields()
        self.loadStates()
        self.listClients()
        
        
        for i in dir(self.ui):
            if i != 'showInactive' and i not in ['searchFirst','searchLast','searchAddr', 'searchCity','searchState','searchContacts']: 
                exec("initializeChangeTracking(self,self.ui.{})".format(i))
        
        self.ui.actionManage_Matter_Types.triggered.connect(partial( self.openManager, MatterManager))
        self.ui.actionManage_Users.triggered.connect(partial(self.openManager, UserManager))
        self.ui.addClient.clicked.connect(self.startAddingNew)
        self.ui.clearContent.clicked.connect(self.clearFields)
        self.ui.editClient.clicked.connect(self.editUser)
        self.ui.saveClientChanges.clicked.connect(self.saveChanges)
        self.ui.clientList.cellClicked.connect(self.loadClient)
        self.ui.addMatter.clicked.connect(partial(self.openMatterWindow, None))
        self.ui.reset.clicked.connect(self.resetFilters)
        self.ui.search.clicked.connect(self.listClients)
        
    def resetFilters(self):
        self.ui.searchFirst.clear()
        self.ui.searchLast.clear()
        self.ui.searchAddr.clear()
        self.ui.searchCity.clear()
        self.ui.searchState.clear()
        self.ui.searchContacts.clear()
        self.listClients()
        
    def lockFields(self):
        self.ui.clientNum.setReadOnly(True)
        self.ui.firstName.setReadOnly(True)
        self.ui.lastName.setReadOnly(True)
        self.ui.middleInitial.setReadOnly(True)
        self.ui.addr1.setReadOnly(True)
        self.ui.addr2.setReadOnly(True)
        self.ui.city.setReadOnly(True)
        self.ui.state.setEnabled(False)
        self.ui.zipcode.setReadOnly(True)
        self.ui.firstName_2.setReadOnly(True)
        self.ui.lastName_2.setReadOnly(True)
        self.ui.middleInitial_2.setReadOnly(True)
        self.ui.phone1.setReadOnly(True)
        self.ui.phone2.setReadOnly(True)
        self.ui.email.setReadOnly(True)
        self.ui.notes.setReadOnly(True)
        self.ui.spouseInfo.setEnabled(False)
        self.ui.donotrep.setEnabled(False)
        self.ui.addMatter.setEnabled(False)
        
        self.action = None
        self.ui.saveClientChanges.setEnabled(False)
        self.ui.editClient.setText('Edit')
        
    def unlockFields(self):
        self.ui.clientNum.setReadOnly(False)
        self.ui.firstName.setReadOnly(False)
        self.ui.lastName.setReadOnly(False)
        self.ui.middleInitial.setReadOnly(False)
        self.ui.addr1.setReadOnly(False)
        self.ui.addr2.setReadOnly(False)
        self.ui.city.setReadOnly(False)
        self.ui.state.setEnabled(True)
        self.ui.zipcode.setReadOnly(False)
        self.ui.firstName_2.setReadOnly(False)
        self.ui.lastName_2.setReadOnly(False)
        self.ui.middleInitial_2.setReadOnly(False)
        self.ui.phone1.setReadOnly(False)
        self.ui.phone2.setReadOnly(False)
        self.ui.email.setReadOnly(False)
        self.ui.notes.setReadOnly(False)
        self.ui.spouseInfo.setEnabled(True)
        self.ui.donotrep.setEnabled(True)
        self.ui.addMatter.setEnabled(False)
        
    def clearFields(self):
        reply = checkChangesMade(self)
        
        if reply == 0:
            self.changes = False
            self.ui.clientNum.clear()
            self.ui.firstName.clear()
            self.ui.lastName.clear()
            self.ui.middleInitial.clear()
            self.ui.addr1.clear()
            self.ui.addr2.clear()
            self.ui.city.clear()
            self.ui.state.setCurrentIndex(0)
            self.ui.zipcode.clear()
            self.ui.firstName_2.clear()
            self.ui.lastName_2.clear()
            self.ui.middleInitial_2.clear()
            self.ui.phone1.clear()
            self.ui.phone2.clear()
            self.ui.email.clear()
            self.ui.notes.clear()
            self.ui.spouseInfo.setEnabled(False)
            self.ui.donotrep.setCheckState(0)
            self.ui.matterList.setRowCount(0)
            
            self.lockFields()

    def editUser(self):
        if self.ui.clientNum.text() != '' and self.action is None:
            self.action = 'update'
            self.ui.saveClientChanges.setEnabled(True)
            self.ui.editClient.setText('Cancel')
            self.unlockFields()
            self.ui.clientNum.setReadOnly(True)
            
        else:
            self.lockFields()
            
    def startAddingNew(self):
        reply = checkChangesMade(self)
        if reply == 0:
            self.action = 'new'
            self.unlockFields()
            self.ui.saveClientChanges.setEnabled(True)
            self.ui.addMatter.setEnabled(False)
            
    def checkName(self):
        apData = ClntFuncs.compileAdversePartyList()
        partyFullNames = apData.fullname.values
        
        clientName = "{} {} {}".format( self.ui.firstName.text(), self.ui.middleInitial.text(), self.ui.lastName.text())
        closeNames = get_close_matches(clientName, partyFullNames)
        if self.ui.spouseInfo.isChecked():
            spouseName = "{} {} {}".format( self.ui.firstName_2.text(), self.ui.middleInitial_2.text(), self.ui.lastName_2.text())
            closeNames.extend(get_close_matches(spouseName, partyFullNames, n = 5, cutoff = .5))
        if len(closeNames) > 0:
            print(closeNames)
            names = "\n".join(closeNames)
            reply = QtGui.QMessageBox.question(self, "Matching Names?", "The following names are possible adverse party matches to this new client. \n{}\nDo you want to save this new client still?".format(names)
                                               ,QtGui.QMessageBox.Yes, QtGui.QMessageBox.No, QtGui.QMessageBox.Cancel)
            
            if reply == QtGui.QMessageBox.Yes:
                return False
            else:
                return True
        else:
            return False
            
    def saveChanges(self):
        
        if self.action is not None:
            if self.checkName():
                return
            if self.ui.clientNum.text().strip() == '':
                alert = QtGui.QMessageBox()
                alert.setWindowTitle('Missing Client #')
                alert.setText("Enter Client Number Before Saving")
                alert.exec_()
                return
            elif self.ui.state.currentIndex() == 0:
                alert = QtGui.QMessageBox()
                alert.setWindowTitle('Missing State')
                alert.setText("Select a state before saving")
                alert.exec_()
                return
            else:
                data = {'action':self.action,
                        'table':'ClientInfo',
                        'values':{'FirstName':str(self.ui.firstName.text()),
                                  'LastName':str(self.ui.lastName.text()),
                                  'MiddleInitial':str(self.ui.middleInitial.text()),
                                  'Address1':str(self.ui.addr1.text()),
                                  'Address2':str(self.ui.addr2.text()),
                                  'City':str(self.ui.city.text()),
                                  'State':str(self.ui.state.currentText()),
                                  'ZipCode':str(self.ui.zipcode.text()),
                                  'Married':str(int(self.ui.spouseInfo.isEnabled())),
                                  'SpouseFirstName':str(self.ui.firstName_2.text()),
                                  'SpouseLastName':str(self.ui.lastName_2.text()),
                                  'SpouseMiddleInitial':str(self.ui.middleInitial_2.text()),
                                  'Phone1':str(self.ui.phone1.text()),
                                  'Phone2':str(self.ui.phone2.text()),
                                  'Email':str(self.ui.email.text()),
                                  'Notes':str(self.ui.notes.toPlainText()),
                                  'DoNotRep':str(int(self.ui.donotrep.checkState()) / 2)},
                        'params':{}
                        }
                if self.action == 'new':key = 'values'
                else:key = 'params'
                
                data[key]['ClientNum'] = str(self.ui.clientNum.text())
                
                CONN.connect()
                CONN.saveData(data)
                CONN.closecnxn()
                self.changes = False
                self.listClients()
                self.lockFields()
                self.ui.addMatter.setEnabled(True)
                
    def listClients(self):
        firstNames = self.ui.searchFirst.text()
        lastNames = self.ui.searchLast.text()
        addrFilter = self.ui.searchAddr.text()
        cityFilter = self.ui.searchCity.text()
        stateFilter = self.ui.searchState.text()
        contactFilters = self.ui.searchContacts.text()
        
        cws = [60,115,125,75,35,50]
        for c, w in enumerate(cws):
            self.ui.clientList.setColumnWidth(c,w)
        
        self.ui.clientList.setRowCount(0)
        
        for r, data in ClntFuncs.listClients(firstNames, lastNames, addrFilter, cityFilter, stateFilter, contactFilters):
            
            self.ui.clientList.insertRow(r)
            self.ui.clientList.setRowHeight(r,20)
            
            clientlabel = QtGui.QLabel(str(data.clientnum))
            clientlabel.cdata = data
            cols = [clientlabel,
                    QtGui.QLabel("{0}, {1}".format(data.lastname,data.firstname) ),
                    QtGui.QLabel(data.address1),
                    QtGui.QLabel(data.city),
                    QtGui.QLabel(data.state),
                    QtGui.QLabel(data.zipcode)]
            populateTableRow(self.ui.clientList, r, cols)
            
    def loadClient(self,row,col):
        reply = checkChangesMade(self)
        if reply == 0:
            self.changes = False
            data = self.ui.clientList.cellWidget(row,0).cdata
            self.ui.clientNum.setText(str(data.clientnum))
            self.ui.firstName.setText(data.firstname)
            self.ui.lastName.setText(data.lastname)
            self.ui.middleInitial.setText(data.middleinitial)
            self.ui.addr1.setText(data.address1)
            self.ui.addr2.setText(data.address2)
            self.ui.city.setText(data.city)
            
            ind = self.ui.state.findData(data.state)
            if ind > 0:
                self.ui.state.setCurrentIndex(ind)

            self.ui.zipcode.setText(data.zipcode)
            self.ui.firstName_2.setText(data.spousefirstname)
            self.ui.lastName_2.setText(data.spouselastname)
            self.ui.middleInitial_2.setText(data.spousemiddleinitial)
            self.ui.phone1.setText(data.phone1)
            self.ui.phone2.setText(data.phone2)
            self.ui.email.setText(data.email)
            self.ui.notes.setText(data.notes)
            self.ui.spouseInfo.setEnabled(int(data.married) == 1)
            self.ui.donotrep.setCheckState(int(data.donotrep) * 2)
            
            self.ui.addMatter.setEnabled(True)
            
            self.listMatters(data.clientnum)
            
    def listMatters(self, clientnum):
        
        self.ui.matterList.setRowCount(0)
        for r, data in MtrFuncs.generateClientMatters(clientnum):
            self.ui.matterList.insertRow(r)
            matterLabel = QtGui.QLabel("{}.{}".format(str(clientnum),str(data.matternum)))
            matterLabel.data = data
            if data.dateclosed is not None:
                closed = 'Yes'
            else:
                closed = 'No'
                
            viewMatter = QtGui.QToolButton()
            viewMatter.setText('View')
            viewMatter.clicked.connect(partial(self.openMatterWindow, data))

            cols = [matterLabel,
                    QtGui.QLabel(data.matterdescr),
                    QtGui.QLabel(data.attorneyinitials),
                    QtGui.QLabel(str(data.dateopened)),
                    QtGui.QLabel(closed),
                    viewMatter
                    ]
            
            populateTableRow(self.ui.matterList, r, cols)

    def loadStates(self):
        
        self.ui.state.addItem("")
        i = 1
        for name, abbrv in stateGenerator():
            self.ui.state.addItem(abbrv)
            self.ui.state.setItemData(i,abbrv)
            i += 1
            
    def openMatterWindow(self, matter = None):
        if self.ui.clientNum.text() != '':
            self.matter = ClientMatters.ClientMatter(self,self.ui.clientNum.text(), matter)
            self.matter.show()
    
    def openManager(self, manager):
        if self.activeUser is not None:
            print(self.activeUser)
            if self.activeUser.admin == 1:
                self.mgr = manager()
                self.mgr.show()