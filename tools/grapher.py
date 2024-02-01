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



class Monographer(QMainWindow):
    """ A program for getting and graphing the monolith and mood watch log data """
    categories = ["steps","heart","mood"]
    catcols = {
      "mood:0":0xffff00,
      "mood:1":0x006666,
      "steps:0":0x00aa00,
      "heart:0":0xaa0000,
    }

    def __init__(self):
        """ Build the UI """
        super().__init__()
        self.graphdata = {}

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
        self.xaxis_dropdown.addItems(["free","day","week","month"])
        toolbar.addWidget(self.xaxis_dropdown)
        self.xaxis_dropdown.currentIndexChanged.connect(self.redrawgraph)

        # Add a test button to the toolbar
        self.test_button = QPushButton("Test")
        self.test_button.clicked.connect(self.sync_files)
        toolbar.addWidget(self.test_button)

        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Not connected")

        # Create a splitter
        mainsplitter = QSplitter(Qt.Horizontal)
        layout = QVBoxLayout()
        layout.addWidget(mainsplitter)

        # Create a tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(mainsplitter)
        mainsplitter.addWidget(self.tabs)

        # Create a figure and a canvas
        figure = Figure()
        self.canvas=FigureCanvas(figure)
        mainsplitter.addWidget(self.canvas)
        self.ax2=figure.add_subplot()
        self.ax=self.ax2.twinx()
        self.redrawgraph() 

        # Add tabs
        for i in self.categories:
            self.graphdata[i] = {}
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

        # Connect the selection changed signal to a slot
        list_view.selectionModel().selectionChanged.connect(lambda: self.update_selected_files(name,list_view, text_edit))
        return tab


    def resort_data(self):
        """ Make sure all the data is in TS order, and also adjust those time-stamps if
            they are outside the range of the viewed month/day/week, so as to make them
            appear overlayed on the viewed week """
        now = datetime.now()
        keys = []
        for i in self.graphdata.keys():
            if(len(self.graphdata[i])>0):
                keys = self.graphdata[i].keys() | keys
        keys = sorted(keys)

        if(len(keys)>0):
            minimum = min(keys)
            maximum = max(keys)
            interval = self.xaxis_dropdown.currentText()
            tsdiff = 1
            if interval == 'day':
                s = now - timedelta(days=now.weekday())
                minimum = s.replace(hour=0, minute=0, second=0, microsecond=0)
                maximum = now.replace(hour=23, minute=59, second=59, microsecond=99999)
                minimum = mdates.date2num(minimum)
                maximum = mdates.date2num(maximum)
                self.ax.xaxis.set_major_locator(mdates.HourLocator(interval=4))
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                tsdiff=1
            elif interval == 'week':
                s = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                minimum = s.replace(hour=0, minute=0, second=0, microsecond=0)
                maximum = s.replace(hour=23, minute=59, second=59, microsecond=999999)
                minimum = mdates.date2num(minimum)
                maximum = mdates.date2num(maximum)+7
                self.ax.xaxis.set_major_locator(mdates.DayLocator())
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%a %d'))
                tsdiff=7
            elif interval == 'month':
                s = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                minimum = s.replace(hour=0, minute=0, second=0, microsecond=0)
                maximum = (minimum + timedelta(days=31)).replace(day=1) - timedelta(microseconds=1)
                minimum = mdates.date2num(minimum)
                maximum = mdates.date2num(maximum)
                self.ax.xaxis.set_major_locator(mdates.DayLocator(interval=7))
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
                tsdiff=28*now.day
            else:
                self.ax.xaxis.set_major_locator(mdates.DayLocator())
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%a %d'))
        else:
            minimum = -2 
            maximum = +2
        self.ax.set_xlim(minimum,maximum)
       

        newdata = {}
        for mode in self.graphdata.keys():
            newdata[mode] = []
            tsoffset = 0
            ii = 0
            thisplot = {}

            if(len(keys)>0):
                oldestts = keys[0]
                while(oldestts+tsoffset<minimum):
                    tsoffset+=tsdiff

                while(ii<len(keys)):
                    ts = keys[ii]
                    tso = ts+tsoffset
                    if(tso<=maximum):
                        if(ts in self.graphdata[mode]):
                            thisplot[tso]=self.graphdata[mode][ts]
                        ii+=1;
                    else:
                        tsoffset-=tsdiff
                        newdata[mode].append(thisplot)
                if(len(thisplot.keys())>0):
                    newdata[mode].append(thisplot)
        return newdata


    def redrawgraph(self):
        """ Redraw the whole graph """
        self.sorteddata = self.resort_data();

        for line in self.ax.lines:
            line.remove()
        for line in self.ax.collections:
            line.remove()
        for line in self.ax2.lines:
            line.remove()
        for line in self.ax2.collections:
            line.remove()
        self.ax.relim()
        self.ax2.relim()
        self.ax.autoscale_view(scalex=True, scaley=False)

        for mode in self.categories:
            if(mode in self.sorteddata):
                for data in self.sorteddata[mode]:
                    if(len(data)>0):
                        xvals = [ts for ts in data.keys()] 
                        for ii in range(0,len(data[xvals[0]])):
                            yvals = [data[ts][ii] for ts in data.keys()]
                            c = self.strtocol(mode+":"+str(ii))
                            if(mode=="mood"):
                                if(ii == 1):
                                    self.ax2.fill_between(xvals,yvals, linewidth=2, color=((((c >> 16) & 0xFF)/255), 
                                                                             (((c >>  8) & 0xFF)/255), 
                                                                             (((c      ) & 0xFF)/255)), step='pre',zorder=1)
                                    for ts in xvals:
                                        print("Dat:"+str(data[ts][1]))
                                else:
                                    self.ax2.plot(xvals,yvals, linewidth=2, color=((((c >> 16) & 0xFF)/255), 
                                                                             (((c >>  8) & 0xFF)/255), 
                                                                             (((c      ) & 0xFF)/255)), zorder=2) #drawstyle="steps-pre",
                            else:
                                self.ax.plot(xvals,yvals, linewidth=2, color=((((c >> 16) & 0xFF)/255), 
                                                                             (((c >>  8) & 0xFF)/255), 
                                                                             (((c      ) & 0xFF)/255)),zorder=3)
        self.canvas.draw()





    def update_selected_files(self, mode, list_view, text_edit):
        """ Set the UI textbox to contain the content of selected files 
            and set the global data-vars for the graph-drawer """
        # Get the selected files
        indexes = list_view.selectionModel().selectedIndexes()
        files = [index.data(QFileSystemModel.FilePathRole) for index in indexes]

        # Read the contents of the files
        contents = ''
        self.graphdata[mode] = {}
        for file in files:
            with open(file, 'r') as f:
                contents += f.read()
                if(mode=="steps"):
                    contents+="\n"
                self.append_graph_data(mode,contents)

        # Update the text edit
        text_edit.setLineWrapMode(QTextEdit.NoWrap)  # Disable word wrapping
        text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)  # Ensure scrollbar is always on
        text_edit.setText(contents)
        self.redrawgraph()

    def append_graph_data(self,mode,contents):
        lines = contents.strip().split("\n")
        for l in lines:
            fields = l.split(",")
            dt = self.parsedate(fields[0])
            if(len(fields)>1):
                if("steps"==mode):
                    #Steps is different coz it's a row per time-block
                    gap = 1/(len(fields)-1)
                    for i in range(1,len(fields)-1):
                        self.graphdata[mode][dt] = [float(fields[i])]
                        dt+=gap
                elif("mood"==mode):
                    #Mood if different coz col3 is a string
                        self.graphdata[mode][dt] = [float(fields[1]),float(fields[2])]
                else:
                    #Default is to just put all numbers into the chain
                        self.graphdata[mode][dt] = []
                        for i in range(1,len(fields)):
                            n = 0
                            try:
                                n = float(fields[i])
                            except:
                                n = self.strtocol(fields[i])
                            self.graphdata[mode][dt].append(n)
                


    def strtocol(self,thestring):
        if(thestring in self.catcols):
            return self.catcols[thestring]
        col = random.randint(0, 255**3)
        self.catcols[thestring] = col
        return col


    def parsedate(self,dstring):
        if((dstring==None)or(dstring=="")):
            return 0
        date_format = "%Y-%m-%d %H:%M" if " " in dstring else "%Y-%m-%d"
        dt = datetime.strptime(dstring, date_format)
        date_num = mdates.date2num(dt)
        return date_num
 

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


    def diff_files(self,year,mode,bunchoflines):
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


