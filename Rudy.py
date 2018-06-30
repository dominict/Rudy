from UI import *
from ScreenControl.MainScreen import MainMatterScreen
from ScreenControl.LogIn import LogInScreen
from connectors import *
import sys

@demo
class MainApp(QtGui.QApplication):
    def __init__(self, *args):
        QtGui.QApplication.__init__(self, *args)
        
        self.main = MainMatterScreen(self)
        self.login = LogInScreen(self)
        self.login.show()
        
        self.lastWindowClosed.connect(self.closeApp)
    
    def closeApp(self):
        self.exit(0)

def main(args):
    global app
    app = MainApp(args)
    app.exec_()
    
if __name__ == "__main__":
    main(sys.argv)