#!/usr/bin/python3
import os
import sys
import types
import random
import string
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import io
import time
import pexpect
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QToolBar, QVBoxLayout, QWidget, QListView, QFileSystemModel, QTextEdit, QSplitter, QComboBox, QPushButton
from PyQt5.QtCore import QDir, Qt, QThread, pyqtSignal
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas



# So. The log files are all named per days,
# and pretty much have exactly one per day (4am to 4am for mood though, sometimes weirder)
# Heart-log has to be read in with no timestamps other than the first
# If I select a range of files, then I have a range of days.
# The plot therefore needs widgets:
#    * Serial/Parallell: Ie, overday days or line 'em up/
#    * Day/Week -> if they're parallel at least




class Monographer(QMainWindow):
    """ A program for getting and graphing the monolith and mood watch log data """
    categories = ["mood","heart","steps"]

    def __init__(self):
        """ Build the UI """
        super().__init__()

        self.setWindowTitle("Monographer")

        # Main toolbar
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Year selection
        self.year_dropdown = QComboBox()
        self.year_dropdown.addItems([str(year) for year in range(2024, 1980, -1)])
        toolbar.addWidget(self.year_dropdown)


        # Connect/Disconnect button
        self.connect_button = QPushButton("Connect")
        toolbar.addWidget(self.connect_button)

        # Sync button
        self.sync_button = QPushButton("Sync")
        self.sync_button.clicked.connect(self.sync_files)
        toolbar.addWidget(self.sync_button)

        # Axis-control
        self.xaxis_dropdown = QComboBox()
        self.xaxis_dropdown.addItems(["day","week","month"])
        toolbar.addWidget(self.xaxis_dropdown)
        self.xaxis_dropdown.currentIndexChanged.connect(self.setup_x_axis)

        # Add a test button to the toolbar
        self.test_button = QPushButton("Test")
        self.test_button.clicked.connect(self.sync_files)
        toolbar.addWidget(self.test_button)

        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Not connected")

        # Create a tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Add tabs
        self.canvases = []
        self.axes = []
        for i in self.categories:
            self.tabs.addTab(self.create_tab(i), i)
        self.update_ui()

    def create_tab(self, name):
        """ Create a tab in the UI """
        # Create a widget for the tab
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        # Create a splitter
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        # Create a list view
        list_view = QListView()
        list_view.setSelectionMode(QListView.ExtendedSelection)  # Allow multiple selection
        splitter.addWidget(list_view)

        # Create a file system model
        model = QFileSystemModel()
        model.setRootPath(QDir.currentPath())
        list_view.setModel(model)
        list_view.setRootIndex(model.index(f'./logs/2024/{name}/'))

        # Create a text edit
        text_edit = QTextEdit()
        splitter.addWidget(text_edit)

        # Create a figure and a canvas
        figure = Figure()
        self.canvases.append(FigureCanvas(figure))
        splitter.addWidget(self.canvases[-1])
        self.axes.append(figure.add_subplot(111))
        self.setup_x_axis() 

        # Connect the selection changed signal to a slot
        list_view.selectionModel().selectionChanged.connect(lambda: self.update_text_edit(list_view, text_edit))
        return tab


    def setup_x_axis(self):
        """ Set up the width of the graph """
        # Get the current selection from the dropdown
        interval = self.xaxis_dropdown.currentText()
        print("Setting up X-Axis"+interval)
        # Set up the x-axis based on the selected interval
        now = datetime.now()

        for ax in self.axes:
            if interval == 'day':
                ax.set_xlim(now.replace(hour=0, minute=0, second=0, microsecond=0), now.replace(hour=23, minute=59, second=59, microsecond=999999))
                ax.xaxis.set_major_locator(mdates.HourLocator(interval=4))
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            elif interval == 'week':
                start_of_week = now - timedelta(days=now.weekday())
                end_of_week = start_of_week + timedelta(days=6, hours=23, minutes=59, seconds=59, microseconds=999999)
                ax.set_xlim(start_of_week, end_of_week)
                ax.xaxis.set_major_locator(mdates.DayLocator())
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%a %d'))
            elif interval == 'month':
                start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                end_of_month = (start_of_month + timedelta(days=31)).replace(day=1) - timedelta(microseconds=1)
                ax.set_xlim(start_of_month, end_of_month)
                ax.xaxis.set_major_locator(mdates.DayLocator(interval=7))
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))

        for c in self.canvases:
            c.draw()


    def update_text_edit(self, list_view, text_edit):
        """ Set the UI textbox to contain the content of selected files """
        # Get the selected files
        indexes = list_view.selectionModel().selectedIndexes()
        files = [index.data(QFileSystemModel.FilePathRole) for index in indexes]

        # Read the contents of the files
        contents = ''
        for file in files:
            with open(file, 'r') as f:
                contents += f.read()

        # Update the text edit
        text_edit.setLineWrapMode(QTextEdit.NoWrap)  # Disable word wrapping
        text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)  # Ensure scrollbar is always on
        text_edit.setText(contents)



    def update_ui(self):
        """ Set the UI up depending on current state """

        #The connect/disconnect button
        if((hasattr(self,"console")) and (hasattr(self,"macaddr")) and 
           (self.console!=None) and (self.macaddr!=None) and (self.macaddr!="")):
            self.connect_button.setText("Disconnect")
            self.connect_button.clicked.connect(self.disconnect_device)
            if(hasattr(self,"sync_thread")):
                self.sync_button.setEnabled(False) 
            else:
                self.sync_button.setEnabled(True) 
            try:
              self.connect_button.clicked.disconnect(self.connect_device)
            except:
              pass
        else:
            self.connect_button.setText("Connect")
            self.connect_button.clicked.connect(self.connect_device)
            self.sync_button.setEnabled(False) 
            try:
              self.connect_button.clicked.disconnect(self.disconnect_device)
            except:
              pass

            

    def disconnect_device(self):
        """ Disconnect from the watch terminal """
        if(hasattr(self,"console")):
            self.console.send('\x18')
            self.console.close()
        self.status_bar.showMessage(f"Disconnected..")
        if(hasattr(self,"console")):
            del(self.console)
        if(hasattr(self,"macaddr")):
            del(self.macaddr)
        self.update_ui()



    def connect_device(self):
        """ Connect to the watch terminal """
        self.status_bar.showMessage(f"Connecting...")
        pynus = os.path.dirname(sys.argv[0]) + '/pynus/pynus.py'
        self.console = pexpect.spawn(pynus, encoding='UTF-8')
        try:
            self.console.expect(r'Connect.*\(([0-9A-F:]*)\)')
        except pexpect.exceptions.TIMEOUT:
            print('ERROR: Cannot find suitable device')
            self.status_bar.showMessage(f"Timeout. Can't find device.")

        self.macaddr = self.console.match.group(1)
        self.status_bar.showMessage(f"Connected:"+self.macaddr)

        self.console.expect('Exit console using Ctrl-X')
        time.sleep(0.5)
        res = self.remote_execute("from shell import ls, cd, cat").strip()
        time.sleep(0.5)
        res = self.remote_execute("from gc import collect").strip()
        time.sleep(0.5)
        res = self.remote_execute("collect()").strip()
        if(res==""):
            self.status_bar.showMessage("connected and tested:"+self.macaddr)
        else:
            self.status_bar.showMessage("connected and tested badly:"+self.macaddr+" -> "+str(res))
        self.update_ui()




    def remote_execute(self,cmd):
        """ Execute a command on the watch """
        if((not hasattr(self,"console")) or (self.console==None)):
            return "Not Connected"
        self.console.sendline(cmd)
        self.console.expect_exact(cmd)
        self.console.expect([pexpect.EOF,'>>> '])
        result = self.console.before.replace("\n\n\n","\n").strip("\n")
        return result



    def sync_files(self):
        """ Start the thread to pull files from the watch into our own log directory """#
        self.sync_thread = SyncThread(self)
        self.sync_thread.main = self
        self.sync_thread.finished.connect(self.sync_files_finished)
        self.sync_thread.progress_updated.connect(self.update_progress)
        self.sync_button.setEnabled(False) 
        self.sync_button.setText("Syncing")
        self.sync_thread.start()

    def sync_files_finished(self):
        del(self.sync_thread)
        self.sync_button.setText("Sync")
        self.sync_button.setEnabled(True) 
        self.update_ui()

    def update_progress(self,x):
        self.sync_button.setText("Synced:"+str(x))
        self.sync_button.setEnabled(False) 
        self.update_ui()



class SyncThread(QThread):
    """ A thread that's keeping the sync running but not blocking the GUI """
        #We do this by catting them using the shell library I reckon.
        #We assume if they are the same length then they are the same
        #file. Presumably mostly it'll be appended-data. Can't be
        #copying every byte of every file or trying to generate diff
        #hashes on the watch and "ls" on the watch only gives file size

    progress_updated = pyqtSignal(int)  # Define a custom signal


    def __init__(self, parent=None):
        super(SyncThread, self).__init__(parent)
        self.scanned=0

    def run(self):
        year = int(self.main.year_dropdown.currentText())
        for mode in self.main.categories:
            res = self.main.remote_execute("cd('/flash/logs/{:04d}/{}/')".format(year,mode)).strip()
            time.sleep(1.1)
            res = self.main.remote_execute("ls").strip()
            self.diff_files(year,mode,res)
            time.sleep(1.1)
            res = self.main.remote_execute("collect()").strip()
            time.sleep(1.1)


    def diff_files(self,year=2024,mode="steps",bunchoflines=None):
        """ We check if the file-lengths are the same as those we
            have on record and if not then by golly we will have
            to inform the proper authorities: IE the sync function """

        #Get the current hard-drive side
        path = "./logs/{:04d}/{}/".format(year,mode)
        files_list = filter(lambda x : os.path.isfile(os.path.join(path,x)), os.listdir(path))
        existing = {}
        for f in files_list:
            size = os.stat(os.path.join(path, f)).st_size
            existing[f] = size

        #Compare
        lines = bunchoflines.split("\n")
        for l in lines:
            fields = l.strip().split()
            if(len(fields)>1):
                if((not fields[1] in existing.keys())or(existing[fields[1]]!=int(fields[0]))):
                    print("Different, syncing: "+fields[1])
                    self.sync_file(year,mode,fields[1])
                else:
                    #print("Already got a good looking "+fields[1])
                    pass
                self.scanned+=1
                self.progress_updated.emit(self.scanned)
        
            
    def sync_file(self,year,mode,fname):
        cmd = "cat(\""+("/flash/logs/{:04d}/{}/{}".format(year,mode,fname))+"\")"
        bunchoflines = self.main.remote_execute(cmd)
        bunchoflines = bunchoflines.replace('\r', '').strip()+"\n"
        time.sleep(1)
        self.main.remote_execute("collect()")
        with open("./logs/{:04d}/{}/{}".format(year,mode,fname), 'w') as f:
            f.write(bunchoflines)
        time.sleep(0.5)




### MAIN start the app ###
app = QApplication(sys.argv)
window = Monographer()
window.show()
app.exec_()


