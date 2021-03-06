# from UI import *
from ScreenControl import *
from ScreenControl.Managers import MatterManager, UserManager,CleanUp
from ScreenControl import ClientMatters, ReportControlWindow
from Functions import CONN, ClientFunctions as ClntFuncs, MatterFunctions as MtrFuncs
from functools import partial
from difflib import get_close_matches
# from os import getcwd
from datetime import datetime as dt
from pandas import DataFrame

class MainMatterScreen(QtGui.QMainWindow):
    def __init__(self, app):

        QtGui.QMainWindow.__init__(self)
        self.ui = loadUi("MainWindow", self)

        self.ui.addClient.setIcon(QtGui.QIcon(addIcon))
        self.ui.addMatter.setIcon(QtGui.QIcon(addIcon))
        self.ui.saveClientChanges.setIcon(QtGui.QIcon(saveIcon))
        self.ui.editClient.setIcon(QtGui.QIcon(editIcon))
        self.ui.clearContent.setIcon(QtGui.QIcon(clearIcon))
        self.ui.deleteAccount.setIcon(QtGui.QIcon(deleteIcon))
#         
        self.activeUser = None
        self.changes = False
        self.action = None
        self.lockFields()
        self.loadStates()
        self.listClients()
        
        
        for i in dir(self.ui):
            if i != 'showInactive' and i not in ['searchFirst','searchLast','searchAddr', 'searchCity','searchState','searchContacts','seeDeleted']: 
                exec("initializeChangeTracking(self,self.ui.{})".format(i))
        
        self.ui.actionManage_Matter_Types.triggered.connect(partial( self.openManager, MatterManager))
        self.ui.actionManage_Users.triggered.connect(partial(self.openManager, UserManager))
        self.ui.actionFile_Maintenance.triggered.connect(partial(self.openManager, CleanUp))
        self.ui.actionBuild_a_Report.triggered.connect(self.openReportWindow)
        self.ui.addClient.clicked.connect(self.startAddingNew)
        self.ui.clearContent.clicked.connect(self.clearFields)
        self.ui.editClient.clicked.connect(self.editUser)
        self.ui.saveClientChanges.clicked.connect(self.saveChanges)
        self.ui.clientList.cellClicked.connect(self.loadClientRow)
        self.ui.addMatter.clicked.connect(partial(self.openMatterWindow, None))
        self.ui.reset.clicked.connect(self.resetFilters)
        self.ui.search.clicked.connect(self.listClients)
        self.ui.deleteAccount.clicked.connect(self.deleteClient)
        
        
        
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
        self.ui.donotrep.setEnabled(False)
        self.ui.addMatter.setEnabled(False)
        self.ui.deleteAccount.setEnabled(False)
        
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
            self.ui.donotrep.setCheckState(0)
            self.ui.matterList.setRowCount(0)
            
            self.lockFields()

    def editUser(self):
        if self.ui.clientNum.text() != '' and self.action is None:
            self.action = 'update'
            self.ui.saveClientChanges.setEnabled(True)
            self.ui.deleteAccount.setEnabled(True)
            self.ui.editClient.setText('Cancel')
            self.unlockFields()
            self.ui.clientNum.setReadOnly(True)
            
        else:
            reply = checkChangesMade(self)
            if reply == 0:
                self.loadClient()
                self.lockFields()
                self.ui.addMatter.setEnabled(True)
            
    def startAddingNew(self):
        reply = checkChangesMade(self)
        if reply == 0:
            self.action = 'new'
            self.unlockFields()
            clientnum = ClntFuncs.getNextClientNum()
            
            if len(clientnum) > 0:
                self.ui.clientNum.setText(str(clientnum.nextnum[0]))
            else:
                self.ui.clientNum.setText(str(1))
            
            self.ui.deleteAccount.delAction = '0'
            self.ui.saveClientChanges.setEnabled(True)
            self.ui.addMatter.setEnabled(False)
            self.ui.deleteAccount.setEnabled(False)
            
    def checkName(self):
        apData = ClntFuncs.compileAdversePartyList()
        partyFullNames = apData.fullname.values
        
        clientName = "{} {} {}".format( self.ui.firstName.text(), self.ui.middleInitial.text(), self.ui.lastName.text())
        closeNames = get_close_matches(clientName, partyFullNames)
        if self.ui.spouseInfo.isChecked():
            spouseName = "{} {} {}".format( self.ui.firstName_2.text(), self.ui.middleInitial_2.text(), self.ui.lastName_2.text())
            
            closeNames.extend(get_close_matches(spouseName, partyFullNames, n = 5, cutoff = .7))
        if len(closeNames) > 0:
            
            closeNameDF = DataFrame(closeNames,columns = ['fullname'])
            nameData = apData.merge(closeNameDF, how = 'inner',on = 'fullname').reset_index()
            
            nameDisplay = []
            for i in nameData.index:
                
                disp = '{} - Matter: {}.{}'.format(nameData.fullname[i],nameData.clientnum[i],nameData.matternum[i])
                nameDisplay.append(disp)
                
            names = "\n".join(nameDisplay)
            reply = QtGui.QMessageBox.question(self, "Matching Names?", "The following names are possible adverse party matches to this new client. \n{}\nDo you want to save this new client still?".format(names)
                                               ,QtGui.QMessageBox.Yes, QtGui.QMessageBox.No, QtGui.QMessageBox.Cancel)
            
            if reply == QtGui.QMessageBox.Yes:
                return False
            else:
                return True
        else:
            return False
        
    def checkForDupes(self):
        
        clientnum = self.ui.clientNum.text()
        clientName = "{} {} {}".format( self.ui.firstName.text(), self.ui.middleInitial.text(), self.ui.lastName.text())
        spouseName = "{} {} {}".format( self.ui.firstName_2.text(), self.ui.middleInitial_2.text(), self.ui.lastName_2.text())
        clientAddr = "{} {} {} {} {}".format(self.ui.addr1.text(), self.ui.addr2.text(), self.ui.city.text(), self.ui.state.currentText(), self.ui.zipcode.text())
        
        refList = ClntFuncs.compileDupeCheck(clientnum)
        nameList = refList.fullname.values
        addrList = refList.fulladdr.values
        
        closeNames = get_close_matches(clientName, nameList, n = 5, cutoff = .7)
        closeNames.extend(get_close_matches(spouseName, nameList, n = 5, cutoff = .7))
        
        closeNameDF = DataFrame(closeNames,columns = ['fullname'])
        nameData = refList.merge(closeNameDF, how = 'inner',on = 'fullname').drop_duplicates().reset_index()
        
        closeAddrs = get_close_matches(clientAddr, addrList, n = 5, cutoff = .90)
        closeAddrDF = DataFrame(closeAddrs, columns = ['fulladdr'])
        addrData = refList.merge(closeAddrDF, how = 'inner',on = 'fulladdr').drop_duplicates().reset_index()
        
        dupeDisp = []
        for i in nameData.index:
            dupeDisp.append('Client #: {} - {} '.format(nameData.clientnum[i], nameData.fullname[i]))
        
        for j in addrData.index:
            dupeDisp.append('Client #: {} {} - {}'.format(addrData.clientnum[j], addrData.fullname[j], addrData.fulladdr[j]))
            
        if len(dupeDisp) > 0:
               
            names = "\n".join(dupeDisp)
            reply = QtGui.QMessageBox.question(self, "Matching Names?", "The following names or address are possible duplicate matches to this new client. \n{}\nDo you want to save this new client still?".format(names)
                                               ,QtGui.QMessageBox.Yes, QtGui.QMessageBox.No, QtGui.QMessageBox.Cancel)
            
            if reply == QtGui.QMessageBox.Yes:
                return False
            else:
                return True
        else:
            return False
        
        
    def deleteClient(self):
        if self.action == 'update':
            if self.ui.deleteAccount.delAction == '0':
                
                reply = QtGui.QMessageBox.question(self, 'Restore Account', 'Do you want to restore this account from the deleted group?',
                                                   QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            else:
                reply = QtGui.QMessageBox.question(self, 'Delete Account', 'Do you want to delete this account?',
                                                   QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                
            

            if reply == QtGui.QMessageBox.Yes:        
                if self.ui.deleteAccount.actionDate is None:
                    self.ui.deleteAccount.actionDate = ''                              
                data = {'action':self.action,
                        'table':'ClientInfo',
                        'values':{'Deleted':str(self.ui.deleteAccount.delAction),
                                  'DeleteDate':str(self.ui.deleteAccount.actionDate)
                                  },
                        'params':{'ClientNum':str(self.ui.clientNum.text())}
                    }

                CONN.connect()
                CONN.saveData(data)
                CONN.closecnxn()
                
                
                self.listClients()
                self.lockFields()
                
                
            
    def saveChanges(self):
        
        if self.action is not None:
            if self.checkName():
                return
            
            if self.checkForDupes():
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
                        'table':'[NortonAbert].[dbo].[ClientInfo]',
                        'values':{'FirstName':str(self.ui.firstName.text()).strip(),
                                  'LastName':str(self.ui.lastName.text()).strip(),
                                  'MiddleInitial':str(self.ui.middleInitial.text()).strip(),
                                  'Address1':str(self.ui.addr1.text()).strip(),
                                  'Address2':str(self.ui.addr2.text()).strip(),
                                  'City':str(self.ui.city.text()).strip(),
                                  'State':str(self.ui.state.currentText()),
                                  'ZipCode':str(self.ui.zipcode.text()).strip(),
                                  'Married':str(int(self.ui.spouseInfo.isChecked())),
                                  'SpouseFirstName':str(self.ui.firstName_2.text()).strip(),
                                  'SpouseLastName':str(self.ui.lastName_2.text()).strip(),
                                  'SpouseMiddleInitial':str(self.ui.middleInitial_2.text()).strip(),
                                  'Phone1':str(self.ui.phone1.text()).strip(),
                                  'Phone2':str(self.ui.phone2.text()).strip(),
                                  'Email':str(self.ui.email.text()).strip(),
                                  'Notes':str(self.ui.notes.toPlainText()).strip(),
                                  'DoNotRep':str(int(self.ui.donotrep.checkState() / 2))},
                        'params':{}
                        }
                if self.action == 'new':
                    key = 'values'
                    data[key]['Deleted'] = str(0)
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
        
        deleted = self.ui.seeDeleted.checkState() == 2
        cws = [60,115,125,75,35,50]
        for c, w in enumerate(cws):
            self.ui.clientList.setColumnWidth(c,w)
        
        self.ui.clientList.setRowCount(0)
        
        for r, data in ClntFuncs.listClients(firstNames, lastNames, addrFilter, cityFilter, stateFilter, contactFilters, deleted):
            
            self.ui.clientList.insertRow(r)
            self.ui.clientList.setRowHeight(r,20)
            
            clientlabel = QtGui.QLabel(str(data.clientnum))
            clientlabel.cdata = data
            cols = [clientlabel,
                    QtGui.QLabel("{0}, {1}".format(data.lastname.strip(),data.firstname.strip()) ),
                    QtGui.QLabel(data.address1),
                    QtGui.QLabel(data.city),
                    QtGui.QLabel(data.state),
                    QtGui.QLabel(data.zipcode)]
            populateTableRow(self.ui.clientList, r, cols)
            
    def loadClientRow(self,row,col):
        reply = checkChangesMade(self)
        if reply == 0:
            self.changes = False
            self.data = self.ui.clientList.cellWidget(row,0).cdata
            self.loadClient()
            
    def loadClient(self):
        
        self.ui.clientNum.setText(str(self.data.clientnum))
        self.ui.firstName.setText(self.data.firstname.strip())
        self.ui.lastName.setText(self.data.lastname.strip())
        self.ui.middleInitial.setText(self.data.middleinitial.strip())
        self.ui.addr1.setText(self.data.address1.strip())
        self.ui.addr2.setText(self.data.address2.strip())
        self.ui.city.setText(self.data.city.strip())
        
        ind = self.ui.state.findData(self.data.state)
        if ind > 0:
            self.ui.state.setCurrentIndex(ind)

        self.ui.zipcode.setText(self.data.zipcode)
        self.ui.firstName_2.setText(self.data.spousefirstname.strip())
        self.ui.lastName_2.setText(self.data.spouselastname.strip())
        self.ui.middleInitial_2.setText(self.data.spousemiddleinitial.strip())
        self.ui.phone1.setText(self.data.phone1)
        self.ui.phone2.setText(self.data.phone2)
        self.ui.email.setText(self.data.email)
        self.ui.notes.setText(self.data.notes)
        
        self.ui.spouseInfo.setChecked(int(self.data.married) == 1)
        self.ui.donotrep.setCheckState(int(self.data.donotrep) * 2)
        
        if self.data.deleted == 1:
            self.ui.deleteAccount.setText("Restore")
            self.ui.deleteAccount.setIcon(QtGui.QIcon(alertIcon))
            self.ui.deleteAccount.actionDate = ''
            self.ui.deleteAccount.delAction = '0'
        else:
            self.ui.deleteAccount.setText("Delete")
            self.ui.deleteAccount.setIcon(QtGui.QIcon(deleteIcon))
            self.ui.deleteAccount.delAction = '1'
            self.ui.deleteAccount.actionDate = str(dt.today().date())
        
        self.ui.addMatter.setEnabled(True)
        
        self.listMatters(self.data.clientnum)
            
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
        print(self.activeUser)
        if self.activeUser is not None:
            if self.activeUser.admin == 1:
                self.mgr = manager()
                self.mgr.show()
                
    def openReportWindow(self):
        self.reporter = ReportControlWindow.ReportingControls()
        self.reporter.show()
