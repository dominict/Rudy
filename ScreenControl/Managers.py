from UI import *

class MatterManager(QtGui.QFrame):
    def __init__(self):
        QtGui.QFrame.__init__(self)
        self.ui = loadUi(UIDir+"\\ManageMatters.ui", self)
        


class UserManager(QtGui.QFrame):
    def __init__(self):
        QtGui.QFrame.__init__(self)
        self.ui = loadUi(UIDir+"\\ManageUsers.ui", self)