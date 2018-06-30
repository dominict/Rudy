from UI import *
from ScreenControl.Managers import MatterManager, UserManager
from functools import partial

class MainMatterScreen(QtGui.QMainWindow):
    def __init__(self, app):
        
        QtGui.QMainWindow.__init__(self)
        self.ui = loadUi(UIDir+"\\MainWindow.ui", self)
        self.activeUser = None
        
        self.ui.actionManage_Matter_Types.triggered.connect(partial( self.openManager, MatterManager))
        self.ui.actionManage_Users.triggered.connect(partial(self.openManager, UserManager))
        
    
    def openManager(self, manager):
        if self.activeUser is not None:
            print(self.activeUser)
            if self.activeUser.admin == 1:
                self.mgr = manager()
                self.mgr.show()