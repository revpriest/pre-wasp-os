#!/usr/bin/python3
import os
import sys
import types
import random
import string
import io
import time
import pexpect
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QToolBar, QVBoxLayout, QWidget, QListView, QFileSystemModel, QTextEdit, QSplitter, QComboBox, QPushButton
from PyQt5.QtCore import QDir, Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class Monographer(QMainWindow):
""" A program for getting and graphing the monolith and mood watch log data """

    def __init__(self):
        """ Build the UI """
        super().__init__()

        self.setWindowTitle("Monographer")

        # Create a toolbar
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Add a dropdown menu to the toolbar
        self.year_dropdown = QComboBox()
        self.year_dropdown.addItems([str(year) for year in range(2024, 1980, -1)])
        toolbar.addWidget(self.year_dropdown)

        # Add a button to the toolbar
        self.connect_button = QPushButton("Connect")
        toolbar.addWidget(self.connect_button)

        # Add a button to the toolbar
        sync_button = QPushButton("Sync")
        toolbar.addWidget(sync_button)

        # Add a status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Not connected")

        # Create a tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Add tabs
        self.tabs.addTab(self.create_tab('steps'), 'Steps')
        self.tabs.addTab(self.create_tab('heart'), 'Heart')
        self.tabs.addTab(self.create_tab('mood'), 'Mood')
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
        canvas = FigureCanvas(figure)
        splitter.addWidget(canvas)

        # Draw the axes
        ax = figure.add_subplot(111)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')

        # Connect the selection changed signal to a slot
        list_view.selectionModel().selectionChanged.connect(lambda: self.update_text_edit(list_view, text_edit))
        return tab


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
        if(hasattr(self,"console")):
          print("Updating ui with console ")
        else:
          print("Updating ui with no console")

        if(hasattr(self,"macaddr")):
          print("Updating ui with mac "+str(self.macaddr))
        else:
          print("Updating ui with no mac")
    
        if((hasattr(self,"console")) and (hasattr(self,"macaddr")) and 
           (self.console!=None) and (self.macaddr!=None) and (self.macaddr!="")):
            self.connect_button.setText("Disconnect")
            self.connect_button.clicked.connect(self.disconnect_device)
            try:
              self.connect_button.clicked.disconnect(self.connect_device)
            except:
              pass
        else:
            self.connect_button.setText("Connect")
            self.connect_button.clicked.connect(self.connect_device)
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
        test = self.remote_execute("print('hi')").strip()
        if(test=="hi"):
            self.status_bar.showMessage("connected and tested:"+self.macaddr)
        else:
            self.status_bar.showMessage("connected and tested badly:"+self.macaddr+" -> "+str(test))
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



### MAIN start the app ###
app = QApplication(sys.argv)
window = Monographer()
window.show()
app.exec_()


