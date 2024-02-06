#!/usr/bin/python3
import os
import sys
import types
import random
import string
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import io
import time
import pexpect
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QToolBar, QVBoxLayout, QWidget, QListView, QFileSystemModel, QTextEdit, QSplitter, QComboBox, QPushButton, QDialog, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, QLineEdit, QLabel
from PyQt5.QtCore import QDir, Qt, QThread, pyqtSignal, QRectF
from PyQt5.QtGui import QBrush, QPainterPath, QPen
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.patches as patches
from matplotlib.lines import Line2D


# TODO:
# 1) Save should edit log as well as metadata
# 2)


class Monographer(QMainWindow):
    categories = ["mood","steps","heart"]
    theme = {
        'bg': (0.1,0.1,0.1),
        'bggraph': (0.16,0.15,0.16),
        'grid': (0.90,0.90,1.00),
        'text': (0.82,0.85,0.82),
    }
    catcols = { }
    fsmodels = {}
    lviews = {}

    def __init__(self):
        """ Build the UI """
        super().__init__()
        self.graphdata = {}
        try:
            with open("monographer_settings.json", "r") as file:
                settings = json.load(file)
                if('catcols' in settings):
                    self.catcols = settings['catcols']
        except:
            pass
        self.setWindowTitle("Monographer")
        self.dialog = EditMetaDialog(self)
        self.actdialog = EditActivitiesDialog(self)


        # Format the stylesheet with the theme colors
        stylesheet = f"""
            QWidget {{
                background-color: {self.rgb_to_hex(self.theme['bg'])};
                color: {self.rgb_to_hex(self.theme['text'])};
            }}
        """
        self.setStyleSheet(stylesheet)

        # Main toolbar
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Year selection
        self.year_dropdown = QComboBox()
        log_dirs = [d for d in os.listdir('./logs/') if os.path.isdir(os.path.join('./logs/', d))]
        sorted_log_dirs = sorted(log_dirs, reverse=True)
        self.year_dropdown.addItems(sorted_log_dirs)
        toolbar.addWidget(self.year_dropdown)
        self.year_dropdown.currentIndexChanged.connect(self.on_year_changed)


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

        # Add a save button to the toolbar
        self.save_but = QPushButton("Save")
        self.save_but.clicked.connect(self.save_button)
        toolbar.addWidget(self.save_but)

        # Add a activites button to the toolbar
        self.act_but = QPushButton("Acitivites")
        self.act_but.clicked.connect(self.activities_button)
        toolbar.addWidget(self.act_but)

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
        self.canvas.mpl_connect('pick_event', lambda x: self.on_pick(x))
        figure.set_facecolor(self.theme['bg'])
        figure.set_picker(5)
        mainsplitter.addWidget(self.canvas)
        self.ax2=figure.add_subplot()
        self.ax2.set_facecolor(self.theme['bggraph'])
        self.ax=self.ax2.twinx()
        self.redrawgraph() 
        self.ax2.grid(True, color=self.theme['grid'], linestyle='-', linewidth=0.5, alpha=0.05)
        figure.subplots_adjust(left=0.06, right=0.94, bottom=0.06, top=0.85)

        self.ax.tick_params(axis='x', colors=self.theme['text'])
        self.ax.tick_params(axis='y', colors=self.theme['text'])
        self.ax.xaxis.label.set_color(self.theme['text'])
        self.ax.yaxis.label.set_color(self.theme['text'])
        self.ax2.tick_params(axis='x', colors=self.theme['text'])
        self.ax2.tick_params(axis='y', colors=self.theme['text'])
        self.ax2.xaxis.label.set_color(self.theme['text'])
        self.ax2.yaxis.label.set_color(self.theme['text'])

        # Add tabs
        for i in self.categories:
           self.graphdata[i] = {}
           self.tabs.addTab(self.create_tab(i), i)
        self.update_ui()

        mainsplitter.setSizes([100, 600])



    def rgb_to_hex(self,rgb):
        """ RGB to Hex """
        return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))

    def create_tab(self, name):
        """ Create a tab in the UI """
        # Create a widget for the tab
        tab = QWidget()
        tablayout = QVBoxLayout()
        tab.setLayout(tablayout)

        # Create a splitter
        tabsplitter = QSplitter(Qt.Horizontal)
        tablayout.addWidget(tabsplitter)
        

        # Create a list view
        self.lviews[name] = QListView()
        self.lviews[name].setSelectionMode(QListView.ExtendedSelection)  # Allow multiple selection
        tabsplitter.addWidget(self.lviews[name])

        # Create a file system model
        self.fsmodels[name] = QFileSystemModel()
        self.fsmodels[name].setRootPath(QDir.currentPath())
        self.lviews[name].setModel(self.fsmodels[name])
        self.fsmodels[name].setNameFilters(["*.csv"])
        self.fsmodels[name].setNameFilterDisables(False)

        year = self.year_dropdown.currentText()
        s = "./logs/{}/{}".format(year,name)
        self.lviews[name].setRootIndex(self.fsmodels[name].index(s))

        # Create a text edit
        text_edit = QTextEdit()
        tabsplitter.addWidget(text_edit)
        tabsplitter.setSizes([1, 0])

        # Connect the selection changed signal to a slot
        self.lviews[name].selectionModel().selectionChanged.connect(lambda: self.update_selected_files(name,self.lviews[name], text_edit))
        return tab



    def on_pick(self,event):
        """ Clicked on the chart? """
        if((event.mouseevent.button =="down") or (event.mouseevent.button =="up")):
            return
        l = event.artist.get_label()
        if(l in self.catcols.keys()):
            del(self.catcols[l])
        else:
            if(event.mouseevent.xdata!=None):
                for ts in self.graphdata['mood']:
                    if(ts>event.mouseevent.xdata):
                        try:
                            fname = self.graphdata["mood"][ts][3]+".meta"
                            with open(fname, "r") as file:
                                metadata = json.load(file)
                                for m in metadata:
                                    ets = m['ts']
                                    matlibts = mdates.date2num(datetime.fromtimestamp(ets))
                                    if(abs(matlibts - ts)<0.0005):
                                        self.dialog.setup(ets, self.graphdata['mood'][ts],m,self.redrawgraph)
                                        self.dialog.show()
                                        return
                        except Exception as e:
                            #print("Excep:"+str(e))
                            pass
                        
                        ets = int(mdates.num2date(ts).timestamp())
                        self.dialog.setup(ets, self.graphdata['mood'][ts],{'text':"",'ts':ts},self.redrawgraph)
                        self.dialog.show()
                        break
                
        self.redrawgraph()

    def on_year_changed(self):
        """ when the year drop-down changes """
        for mode in self.categories:
            year = self.year_dropdown.currentText()
            s = "./logs/{}/{}".format(year,mode)
            self.lviews[mode].setRootIndex(self.fsmodels[mode].index(s))
            
        

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
            else:   #free
                diff = maximum - minimum
                if(diff < 1.1):
                    self.ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
                    self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                elif(diff < 2.2):
                    self.ax.xaxis.set_major_locator(mdates.HourLocator(interval=4))
                    self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                elif(diff < 10):
                    self.ax.xaxis.set_major_locator(mdates.DayLocator())
                    self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%a %d'))
                else:
                    self.ax.xaxis.set_major_locator(mdates.DayLocator(interval=7))
                    self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        else:
            minimum = -2 
            maximum = +2
        if((maximum-minimum)<1):
          minimum = int(maximum-1)
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
        for line in self.ax2.patches:
            line.remove()
        self.ax.relim()
        self.ax2.relim()
        self.ax.autoscale_view(scalex=True, scaley=False)

        legcols = {}
        for mode in self.categories:
            if(mode in self.sorteddata):
                for data in self.sorteddata[mode]:
                    if(len(data)>0):
                        xvals = [ts for ts in data.keys()] 
                        for ii in range(0,len(data[xvals[0]])):
                            yvals = [data[ts][ii] for ts in data.keys()]
                            c = self.strtocol(mode)
                            if(mode=="mood"):
                                if(ii == 1):            #Awake determines block height, category determines color.
                                    prior = [int(xvals[0]),0]
                                    for ts in xvals:
                                        s=self.cleantopic(data[ts][2]) 
                                        c = self.strtocol(s)
                                        legcols[s]=(1,c)
                                        col = ((((c >> 16) & 0xFF)/255), (((c >>  8) & 0xFF)/255),  (((c      ) & 0xFF)/255))
                                        if(prior!=None):
                                            rect = patches.Rectangle((prior[0], -0.02), ts-prior[0], data[ts][1]+0.02, linewidth=0, edgecolor=None, facecolor=col, zorder=2)
                                            self.ax2.add_patch(rect)
                                        prior = [ts,data[ts][1]]
                                elif(ii==0):
                                    legcols[mode]=(0,c)
                                    self.ax2.plot(xvals,yvals, linewidth=1.2, color=((((c >> 16) & 0xFF)/255), 
                                                                             (((c >>  8) & 0xFF)/255), 
                                                                             (((c      ) & 0xFF)/255)), zorder=3) #drawstyle="steps-pre",
                                else:
                                    pass #Don't try and draw "category", it's already the colour of the "awake"
                            else:
                                legcols[mode]=(0,c)
                                self.ax.plot(xvals,yvals, linewidth=1.2, color=((((c >> 16) & 0xFF)/255), 
                                                                             (((c >>  8) & 0xFF)/255), 
                                                                             (((c      ) & 0xFF)/255)), label=mode+":"+str(ii), zorder=4)

        legs = []
        for i in legcols.keys():
            c = legcols[i][1]
            col = ((((c >> 16) & 0xFF)/255), (((c >>  8) & 0xFF)/255), (((c      ) & 0xFF)/255))
            if(legcols[i][0]==0):
                patch = Line2D([0],[0],color=col,label=i)
            else:
                patch = patches.Patch(color=col,label=i)
            legs.append(patch)
        leg = self.ax.legend(handles=legs, loc='upper left', bbox_to_anchor=(0.0, 1.2),framealpha=1,facecolor=(0.15,0.15,0.15),labelcolor="white",ncol=7)
        for l in leg.get_patches():
            l.set_picker(5)
        for l in leg.get_lines():
            l.set_picker(5)
        self.canvas.draw()




    def cleantopic(self,topic):
        """ Just clean up the name stripping the punctuation and excess spaces etc. """
        return topic.replace(".","").strip()


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
                self.append_graph_data(mode,contents,file)

        # Update the text edit
        text_edit.setLineWrapMode(QTextEdit.NoWrap)  # Disable word wrapping
        text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)  # Ensure scrollbar is always on
        text_edit.setText(contents)
        self.redrawgraph()

    def append_graph_data(self,mode,contents,filename):
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
                        self.graphdata[mode][dt] = [float(fields[1]),float(fields[2]),fields[3],filename]
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




    def remote_execute(self,cmd,expect=None):
        """ Execute a command on the watch """
        if((not hasattr(self,"console")) or (self.console==None)):
            return "Not Connected"
        if(expect==None):
            expect = cmd
        self.console.sendline(cmd)
        self.console.expect_exact(expect)
        self.console.expect([pexpect.EOF,'>>> '])
        result = self.console.before.replace("\n\n\n","\n").strip("\n")
        return result


    def activities_button(self):
        """ Popup the activities to edit if we are connected to watch """
        if(hasattr(self,"console")):
            self.actdialog.setup("Loading...")
            self.actdialog.show()
            res = self.remote_execute("cat('/flash/activities.csv')")
            res = "\n".join(res.strip().split("\n")[0].split(","))
            self.actdialog.setup(res)
        else:
            self.status_bar.showMessage(f"Not Connected!")
       
    def save_activities(self,newsetstr):
        newsetstr = ",".join(newsetstr.strip().split("\n")).strip()
        print("Saving:"+newsetstr)
        res = self.remote_execute("collect()").strip()

        time.sleep(0.5)
        cmd = "f=open(\"/flash/activities.csv\", \"w\")"
        res = self.remote_execute(cmd)

        time.sleep(0.5)
        cmd = "f.write(\""+newsetstr+"\")"
        res = self.remote_execute(cmd)

        time.sleep(0.5)
        cmd = "f.close()"
        res = self.remote_execute(cmd)

        time.sleep(0.5)
        cmd = "del(f)"
        res = self.remote_execute(cmd)

        if(res=="Saved"):
            self.status_bar.showMessage("Saved Great")
        else:
            self.status_bar.showMessage("Failed Save:"+res)
            
        
        

    def save_button(self):
        """ What does the save button do? It saves the color-chart
            and that is automatically loaded at restart """
        with open("monographer_settings.json", "w") as file:
            json.dump({'catcols':self.catcols}, file)
            print("Saved")

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
                    print("Different, syncing: "+str(fields[0])+":"+str(fields[1]))
                    self.sync_file(year,mode,fields[1])
                else:
                    #print("Already got a good looking "+fields[1])
                    pass
                self.scanned+=1
                self.progress_updated.emit(self.scanned)
        
            
    def sync_file(self,year,mode,fname):
        cmd = "cat(\""+("/flash/logs/{:04d}/{}/{}".format(year,mode,fname))+"\")"
        bunchoflines = self.main.remote_execute(cmd)
        bunchoflines = bunchoflines.replace('\r', '').strip()
        if(mode!="steps"):
            bunchoflines+="\n"
        time.sleep(1)
        self.main.remote_execute("collect()")
        with open("./logs/{:04d}/{}/{}".format(year,mode,fname), 'w') as f:
            f.write(bunchoflines)
        time.sleep(0.5)


### EDIT THE EXTRA CATEGORIES DIALOG ##
class EditActivitiesDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.parent = parent

        desc = QLabel(self)
        desc.setText("One per line, don't be fancy or many, you may crash the watch")
        self.layout.addWidget(desc)

        self.textEdit = QTextEdit(self)
        self.layout.addWidget(self.textEdit)

        self.saveButton = QPushButton('Save To Watch', self)
        self.layout.addWidget(self.saveButton)
        self.saveButton.clicked.connect(self.save)

        self.cancelButton = QPushButton('Cancel', self)
        self.layout.addWidget(self.cancelButton)
        self.cancelButton.clicked.connect(self.cancel)

    def setup(self, text):
        self.textEdit.setText(str(text))

    def cancel(self):
        self.hide()

    def save(self):
        self.parent.save_activities(self.textEdit.toPlainText())
        self.hide()


### EDIT AN EVENT METADATA DIALOG ##

class EditMetaDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)

        # Create a QGraphicsView with a circle in the top left corner
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)
        self.redraw()
        self.layout.addWidget(self.view)

        # Create some, QLineEdit boxes for editing values
        self.happy = QLineEdit(self)
        self.awake = QLineEdit(self)
        self.category = QLineEdit(self)
        self.layout.addWidget(self.happy)
        self.layout.addWidget(self.awake)
        self.layout.addWidget(self.category)

        # Connect the textChanged signal to the redraw method
        self.happy.textChanged.connect(self.redraw)
        self.awake.textChanged.connect(self.redraw)

        # Create a QTextEdit box for multiline text input
        self.textEdit = QTextEdit(self)
        self.layout.addWidget(self.textEdit)

        # Create Save and Cancel buttons
        self.saveButton = QPushButton('Save', self)
        self.layout.addWidget(self.saveButton)
        self.saveButton.clicked.connect(self.save)

        self.cancelButton = QPushButton('Cancel', self)
        self.layout.addWidget(self.cancelButton)
        self.cancelButton.clicked.connect(self.cancel)

    def setup(self, ts, event, meta,callback):
        self.ts    = ts   
        self.event = event
        self.meta = meta
        self.callback = callback
        self.meta['ts'] = ts
        self.happy.setText(str(event[0]))
        self.awake.setText(str(event[1]))
        self.category.setText(str(event[2].strip()))
        self.textEdit.setText(str(meta['text']))


    def redraw(self):
        # Clear the scene
        self.scene.clear()

        # Redraw the yellow ellipse
        ellipse = QGraphicsEllipseItem(QRectF(0, 0, 128, 128))
        ellipse.setBrush(QBrush(Qt.yellow))
        self.scene.addItem(ellipse)

        # Draw the black ellipses for eyes
        awake_value = 0.5
        try:
            awake_value = float(self.awake.text())
        except:
            pass
        if(awake_value>1):awake_value=1
        if(awake_value<0):awake_value=0
        offset = awake_value * 16
        ellipse1 = QGraphicsEllipseItem(QRectF(24, 48-offset, 32, awake_value * 32))
        ellipse1.setBrush(QBrush(Qt.black))
        self.scene.addItem(ellipse1)

        ellipse2 = QGraphicsEllipseItem(QRectF(72, 48-offset, 32, awake_value * 32))
        ellipse2.setBrush(QBrush(Qt.black))
        self.scene.addItem(ellipse2)

        # Draw the curve for mouth
        happy_value = 0.5
        try:
            happy_value = float(self.happy.text())
        except:
            pass

        if(happy_value>1):happy_value=1
        if(happy_value<0):happy_value=0
        pen = QPen(Qt.black, 5)
        h = 88
        mid_point = h + (happy_value - 0.5) * 80
        path = QPainterPath()
        path.moveTo(24, h)
        path.quadTo(64, mid_point, 104, h)
        self.scene.addPath(path,pen)

        # Update the view
        self.view.update()


    def cancel(self):
        self.hide()

    def save(self):
        changed=False
        changedMeta=False
        if(self.event[0] != float(self.happy.text())):
            self.event[0] = float(self.happy.text())
            changed=True
        if(self.event[1] != float(self.awake.text())):
            self.event[1] = float(self.awake.text())
            changed=True
        if(self.event[2] != self.category.text()):
            self.event[2] = self.category.text()
            changed=True
        testtext = self.textEdit.toPlainText()
        if(self.meta['text'] != testtext):
            self.meta['text'] = testtext
            changedMeta=True
        if(changedMeta):
            self.saveMetadata()
        if(changed):
            self.updateSavedLog()
        self.callback() 
        self.hide()

    def fix_str_size(self,s):
        if(s[-1]=="."):
          s = s[0:-1]
        while(len(s)<35):
          s+=" "
        s = s[0:35]
        return s+"."

    def saveMetadata(self):
        fname = self.event[3]+".meta"
        metadata = []
        try:
            with open(fname, "r") as file:
                metadata = json.load(file)
        except:
            pass
            #print("no existing file?") 
        found=False
        for i in range(0,len(metadata)):
            met = metadata[i]
            if(self.ts == met['ts']):
                found=True
                metadata[i] = self.meta
        if(not found):
            metadata.append(self.meta)
        with open(fname, "w") as file:
            json.dump(metadata, file)

    def updateSavedLog(self):
        fname = self.event[3]
        contents = ""
        try:
            with open(fname, 'r') as f:
                contents += f.read()
            lines = contents.split("\n")
            for i in range(0,len(lines)):
                fields = lines[i].split(",")
                if(len(fields)>1):
                    test_ts = int(datetime.strptime(fields[0], "%Y-%m-%d %H:%M").timestamp())
                    if(test_ts==self.ts):
                        fields[1] = "{:0.2f}".format(self.event[0])
                        fields[2] = "{:0.2f}".format(self.event[1])
                        fields[3] = self.fix_str_size(self.event[2])
                        lines[i] = ",".join(fields)
                    else:
                        lines[i] = ",".join(fields)
            newcontents = "\n".join(lines)
            with open(fname, 'w') as f:
                f.write(newcontents)
        except Exception as e:
           print("Can't write:"+str(e)) 



### MAIN start the app ###
app = QApplication(sys.argv)
window = Monographer()
window.show()
app.exec_()


