import sys
from run import runBash

try:
    import Tkinter, tkMessageBox
    gui = True
except ImportError:
    gui = False
    pass

def popup(msg):
    root = Tkinter.Tk()
    root.withdraw()
    tkMessageBox.showinfo(sys.argv[0], str(msg))

def broadcast_msg(msg):
    runBash('echo "%s" | wall' % str(msg))
