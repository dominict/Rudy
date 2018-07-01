from UI import *
from Functions import MatterFunctions as MtrFuncs
from ScreenControl import *

class ClientMatter(QtGui.QMainWindow):
    def __init__(self, client, clientnum, matter = None):
        
        QtGui.QMainWindow.__init__(self)
        self.ui = loadUi(UIDir + "\\MatterWindow.ui",self)
        
        self.client = client
        self.clientnum = clientnum
        self.matter = matter
        
        self.listMatterTypes()
        self.loadStates()
        
        for i in dir(self.ui):
                exec("initializeChangeTracking(self,self.ui.{})".format(i))
        
        self.ui.actionClose.triggered.connect(self.closeWindow)
        
    def listMatterTypes(self):
        matterTypes = MtrFuncs.listMatters()
        
        self.ui.matterType.addItem("")
        for i, m in enumerate(matterTypes.index):
            self.ui.matterType.addItem(matterTypes.matterdescr[m])
            self.ui.matterType.setItemData(i+1, matterTypes.typeid[m])
            
    def loadStates(self):
        
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
            