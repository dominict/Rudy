from UI import *
from Functions import UserFunctions as UsrFuncs, CONN
from PyQt4.Qt import QListWidgetItem

class MatterManager(QtGui.QFrame):
    def __init__(self):
        QtGui.QFrame.__init__(self)
        self.ui = loadUi(UIDir+"\\ManageMatters.ui", self)
        
        
        
class Password(QtGui.QFrame):
    def __init__(self,usermgr,action):
        
        QtGui.QFrame.__init__(self)
        self.usermgr = usermgr
        self.action = action
        
        self.setWindowTitle("Password")
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        
        self.layout = QtGui.QFormLayout(self)
        
        self.password = QtGui.QLineEdit()
        self.password.setEchoMode(QtGui.QLineEdit.Password)
        
        self.confirm = QtGui.QLineEdit()
        self.confirm.setEchoMode(QtGui.QLineEdit.Password)
        
        self.hbox = QtGui.QHBoxLayout()
        self.btnSavePassword = QtGui.QPushButton('Save')
        self.btnCancelPassword = QtGui.QPushButton('Cancel')
        
        self.hbox.addWidget(self.btnSavePassword)
        self.hbox.addWidget(self.btnCancelPassword)
        
        self.layout.addRow(QtGui.QLabel("Password: "),self.password)
        self.layout.addRow(QtGui.QLabel("Confirm: "),self.confirm)
        self.layout.addRow(None,self.hbox)
        
        self.btnCancelPassword.clicked.connect(self.close)
        self.btnSavePassword.clicked.connect(self.savePassword)
    
    def savePassword(self):
        if self.password.text() != self.confirm.text():
            alert = QtGui.QMessageBox()
            alert.setWindowTitle("Password Mismatch")
            alert.setText("Your password does not match the confirmation. Please try again.")
            alert.exec_()
            return
        else:
            self.usermgr.ui.password.pwd = self.password.text()
            self.usermgr.changes = True
            self.close()

class UserManager(QtGui.QFrame):
    def __init__(self):
        
        QtGui.QFrame.__init__(self)
        self.ui = loadUi(UIDir+"\\ManageUsers.ui", self)

        for i in dir(self.ui):
            if i != 'showInactive':
                exec("self.initializeChangeTracking(self.ui.{})".format(i))

        self.changes = False
        self.lockFields()
        self.listUsers()
        
        self.ui.newUser.clicked.connect(self.startNewUser)
        self.ui.save.clicked.connect(self.saveChanges)
        self.ui.clear.clicked.connect(self.clearFields)
        self.ui.password.clicked.connect(self.setPassword)
        self.ui.userList.itemClicked.connect(self.loadUserDetails)
        self.ui.showInactive.clicked.connect(self.listUsers)
    
    def initializeChangeTracking(self,widget):
        if isinstance(widget,QtGui.QLineEdit):
            widget.textEdited.connect(self.markAsChanged)
        elif isinstance(widget, QtGui.QCheckBox):
            widget.clicked.connect(self.markAsChanged)
    
    def lockFields(self,):
            
        self.ui.username.setReadOnly(True)
        self.ui.password.setEnabled(False)
        self.ui.fullName.setReadOnly(True)
        self.ui.admin.setEnabled(False)
        self.ui.inactive.setEnabled(False)
            
    def unlockFields(self):
            
        self.ui.username.setReadOnly(False)
        self.ui.password.setEnabled(True)
        self.ui.fullName.setReadOnly(False)
        self.ui.admin.setEnabled(True)
        self.ui.inactive.setEnabled(True)
    
    def listUsers(self):
        userListData = UsrFuncs.getUserList(activeOnly = self.ui.showInactive.checkState() == 0)
        
        self.ui.userList.clear()
        for i in userListData.index:
            item = QListWidgetItem()
            itemLabel = QtGui.QLabel(userListData.username[i])
            itemLabel.data = userListData.loc[i]
        
            self.ui.userList.addItem(item)
            self.ui.userList.setItemWidget(item, itemLabel)
            
    def setPassword(self):
        self.pwdWindow = Password(self,self.action)
        self.pwdWindow.show()
    
    def saveChangesCheck(self):
        if self.changes == True:
            reply = QtGui.QMessageBox.question(self, "Save Changes?", "Would you like to save you changes?"
                                               ,QtGui.QMessageBox.Yes, QtGui.QMessageBox.No, QtGui.QMessageBox.Cancel)
            if reply == QtGui.QMessageBox.Yes:
                self.saveChanges()
                return 0
            elif reply == QtGui.QMessageBox.Cancel:
                return 1
            else:
                return 0
        else:   
            
            return 0
            
    def markAsChanged(self):
        self.changes = True
    
    def startNewUser(self):
        self.clearFields()
        self.unlockFields()
        
        self.action = 'new'
    
    def clearFields(self):
        reply = self.saveChangesCheck()
        if reply == 0:
            self.lockFields()
            self.ui.username.clear()
            self.ui.password.pwd = None
            self.ui.fullName.clear()
            self.ui.lastSignin.clear()
            self.ui.admin.setCheckState(0)
            self.ui.inactive.setCheckState(0)
            
            self.changes = False
    
    def saveChanges(self):
        
        username = self.ui.username.text()
        password = self.ui.password.pwd
        fullName = self.ui.fullName.text()
        admin = self.ui.admin.checkState() == 2
        inactive = self.ui.inactive.checkState() == 2
        
        checks = UsrFuncs.validateUserChange(username)
        
        alert = QtGui.QMessageBox()
        if checks.usrchk[0] > 0 and self.action == 'new':
            alert.setWindowTitle('Invalid Username')
            alert.setText('Username Already Used')
            alert.exec_()
            return
        elif not admin and checks.admchk[0] == 1 and self.ui.admin.orig == 2:
            alert.setWindowTitle('Last Admin')
            alert.setText("This is the last administrator account.")
            alert.exec_()
            return 
        elif inactive and checks.inactivechk[0] == 1 and self.ui.inactive.origInactive == 0:
            alert.setWindowTitle('Last Active Account')
            alert.setText("This is the last active account.")
            alert.exec_()
            return
        elif password is None:
            alert.setWindowTitle('No Password')
            alert.setText("Set your password before saving.")
            alert.exec_()
            return
            
            
        data = {'action':self.action,
                'table':'UserParam',
                'values':{'Password':password,
                          'FullName':fullName,
                          'Admin':int(admin),
                          'Inactive':int(inactive)},
                'params':{}
                }
        
        if self.action == 'new':
            key = 'values'
        else:
            key = 'params'
            
        data[key]['Username'] = username
        
        CONN.connect()
        CONN.saveData(data)
        CONN.closecnxn()
        self.changes = False
        self.clearFields()
        self.listUsers()
        
    def loadUserDetails(self,item):
        reply = self.saveChangesCheck()
        if reply == 0:
            
            self.clearFields()
            self.unlockFields()
            self.ui.username.setReadOnly(True)
            self.action = 'update'
            
            userData = self.ui.userList.itemWidget(item).data    
            self.ui.username.setText(userData.username)
            self.ui.password.pwd = userData.password
            self.ui.fullName.setText(userData.fullname)
            self.ui.admin.setCheckState(int(userData.admin) * 2)
            self.ui.inactive.setCheckState(int(userData.inactive) * 2)
            
            self.ui.inactive.origInactive = int(userData.inactive) * 2
            self.ui.admin.origAdmin = int(userData.admin) * 2
        
        
    