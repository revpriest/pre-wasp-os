# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2023 Adam Priest
                  
"""Mood application
~~~~~~~~~~~~~~~~~~~~
This app allows you to set a mood and status to be logged.

.. figure:: res/screenshots/MoodApp.png
    :width: 179
"""

# Issues:
# * MEMORY - those Entry objects can be squished to mostly bytes.

# You may add extra categories to the activities list
# by placing a file in /flash/activities.csv containing
# all the categories comma-separated in the first row.
# Be frugal: we are tight on RAM.
# We try and upload that while not in foreground.
# 
# Should be a single line but I find the wasp tool won't
# upload a file which is less than 64 bytes long so you may 
# pad it with junk to be ignored in the second line if it's 
# less.
#
# Can now set it with the monographer companion tool.

import wasp
import watch
import widgets
import time
import os
import fonts
import gc
import array
from micropython import const


COLS = array.array("H",[ 0xc000,0x0620,0x0018,0xc620,0x0638,0xc018,0xc638,
                         0xC30C,0x662C,0x6318,0xC318,0xC62C,0x6638,0x630C ])
_newcol      = const(0x366e)
_edittimecol = const(0xa986)
_editcol     = const(0xee85)
_blankentry  = array.array("L",[0,0,0])

class MoodApp():
    NAME = "Mood"
    # The app-icon is also used as the base to draw the face.
    # 2-bit RLE, 64x64, generated from res/moodball.png, 209 bytes
    ICON = (
        b'\x02'
        b'@@'
        b'\x19@\xa8ALA.ATA(AXA$A'
        b'\\A A`A\x1cAdA\x19AfA\x17A'
        b'hA\x15AjA\x13AlA\x11AnA\x0fA'
        b'pA\rArA\x0bAtA\nv\tAvA'
        b'\x08x\x07AxA\x06z\x05AzA\x04|\x03A'
        b'P\x80*\x81Z\x81PA\x02P\x83X\x83P\x02Q'
        b'\x81Z\x81Q\x02~\x01A~A\x7f\xff\xff\xc3A~'
        b'A\x01~\x02~\x02~\x02A|A\x03Z\x82\x84\x82'
        b'Z\x04A\\\x82\\A\x05z\x06AxA\x07x\x08'
        b'AvA\tv\nAtA\x0bArA\rAp'
        b'A\x0fAnA\x11AlA\x13AjA\x15Ah'
        b'A\x17AfA\x19AdA\x1cA`A A\\'
        b'A$AXA(ATA.ALA\x19'
    )

    def __init__(self):
        #Make methods available to the watch-faces.
        wasp.mood_draw = self._draw_mood_face
        wasp.mood_logrotate = self._logrotate
        self._cacheentry = _blankentry
        self._filediff    = ""
        self._currentact = 0
        self._topid = 0
        self._showdaydiff = 0
        self._editingface = None        ##Or the starting accelerator coords if editing
        self._startedit = (0.5,0.5)
        self._lastlogrotate = time.mktime(wasp.watch.rtc.get_localtime()+(0,))
        self._cacheprior = _blankentry
        self._load_acts()
        self._load()
        self._reset()
        self._update()

    def unregister(self):
        del(wasp.mood_draw)
        del(wasp.mood_logrotate)

    def background(self):
        pass

    def wake(self):
        pass

    def foreground(self):
        wasp.system.bar.clock = True
        wasp.system.request_event(wasp.EventMask.TOUCH)
        wasp.system.request_event(wasp.EventMask.TOUCH | wasp.EventMask.SWIPE_UPDOWN| wasp.EventMask.SWIPE_LEFTRIGHT)
        self._reset()
        self._draw()
        wasp.system.request_tick(500)
        self._load_acts()

    def _load_acts(self):
        gc.collect()
        self._activities = ["slack", "social", "work", "sleep", "exercise", "travel", "cooking", "tv", "games", "project"]
        try:
          with open("/flash/activities.csv", 'r') as f:
            l = f.readline()
            for i in l.split(","):
              self._activities.append(i.strip())
        except Exception as e:
            print("ActLoadExcep:" +str(e))
        gc.collect()

    #Reset the cache-entry to be the next one in line
    def _reset(self):
        self._cacheentry   =self._clone_entry(self._cacheprior)
        self._editingface = None
        if(self._cacheentry!=None):
            n = self._get_rounded_now_ts()
            self._cacheentry[0]=int(n)
        self._viewid = self._topid+1


    #What to do if someone touches us
    def touch(self, event):
        wasp.watch.vibrator.pulse(duty=30, ms=50)
        x = event[1]
        y = event[2]
        if(y<105):
          if(x<105):
            if(self._editingface==None):
                self._editingface = 1
                h = self._cacheentry[1] & 0xffff
                a = (self._cacheentry[1] >> 16) & 0xffff
                self._startedit = (h/1000,a/1000)
            else:
                self._editingface=None
          if(x>139):
            self._savebut()
            self._draw()
        elif((y>=96)and(y<160)):
          if(x<80):
            self._act_change(-1)
          elif(x>160):
            self._act_change(1)
          self._draw_act_selector()
        elif((y>160)and(y<192)):
          self._undobut()
        elif(y>=192):
          if(x<40):
            self._cacheentry[0]-= 60*60
          elif(x<80):
            self._cacheentry[0]-= 60*5
          elif(x>200):
            self._cacheentry[0]+= 60*60
          elif(x>160):
            self._cacheentry[0]+= 60*5
          else:
            self._cacheentry[0] = int(self._get_rounded_now_ts())
          self._draw_time_period()

    #What to do if someone strokes us
    def swipe(self, event):
        if(event[0]==1):      #down
          self._switch_entry(1)
        elif(event[0]==2):    #up
          self._switch_entry(-1)
        elif(event[0]==3):    #left
          if(self._viewid>self._topid):
            return True       #True, the launcher should handle it.
          else:
            self._switch_day(-1)
        elif(event[0]==4):    #right
          if(self._viewid>self._topid):
            return True       #True, the launcher should handle it.
          else:
            return self._switch_day(+1)
        return False


    #Drawing the thing
    def _draw(self):
        wasp.watch.drawable.set_color(0x0000)
        wasp.watch.drawable.fill()
        wasp.system.bar.draw()
        wasp.watch.drawable.set_font(fonts.sans24)
        if(self._cacheentry==None):
          self._draw_mood_face(32,34,0.5,0.5)
        else:
          h = self._cacheentry[1] & 0xffff
          a = (self._cacheentry[1] >> 16) & 0xffff
          self._draw_mood_face(32,34,h/1000,a/1000)
        self._draw_act_selector()
        self._draw_time_period()
        self._draw_save_button()
        if(self._showdaydiff!=0):
          wasp.watch.drawable.set_color(0,_editcol)
          wasp.watch.drawable.string("{}".format(self._showdaydiff),60, 0, width=119)
          
        self._update()


    def tick(self, ticks):
        if(self._editingface!=None):
            (x, y, z) = watch.accel.accel_xyz()
            if(self._editingface==1):
                #I don't really understand why just setting this straight away didn't work.
                #but we set it here after the init signal instead because it didn't.
                #was just giving radically different accel numbers.
                self._editingface=(x,y,z)
            else:
                x=self._editingface[0]-x
                y=self._editingface[1]-y
                z=self._editingface[2]-z
                if(x>300):x=300
                if(x<-300):x=-300
                if(y>300):y=300
                if(y<-300):y=-300
                x=float(x)/300
                y=float(y)/300
                x=self._startedit[1]-x
                y=self._startedit[0]+y
                if(y<0):y=0
                if(y>1):y=1
                if(x<0):x=0
                if(x>1):x=1
                self._cacheentry[1] = int((int(y*1000) << 16) + int(x*1000))
                self._draw_mood_face(32,34,y,x)
                wasp.system.keep_awake()

    #Nothing here really changes without user-input so we do the updates on input instead.
    def _update(self):
        wasp.system.bar.update()


    def _draw_time_period(self):
        draw = wasp.watch.drawable
        if(self._viewid>self._topid):
          draw.set_color(_newcol)
        else:
          draw.set_color(_editcol)
        if(self._cacheprior!=None):
            cp = time.localtime(self._cacheprior[0])
            draw.string("{:04d}-{:02d}-{:02d}".format(
                    cp[0],cp[1],cp[2]), 2, 144,235)
            draw.string("From {:02d}:{:02d} to".format(
                    cp[3],cp[4]), 2, 176,235)
            draw.set_color(_edittimecol)
            cp = time.localtime(self._cacheentry[0])
            draw.string("{:02d}:{:02d}".format(cp[3],cp[4]), 80, 208,80)

    def _draw_save_button(self):
        draw = wasp.watch.drawable
        draw.set_color(0xffff,0x2304)
        if(self._viewid<=self._topid):
          draw.string("edit", 136, 44,100)
          draw.set_font(fonts.sans18)
          draw.string("{:d}".format(self._viewid), 136, 68,100)
          draw.set_font(fonts.sans24)
          if((self._viewid==self._topid)and(self._showdaydiff==0)):
            draw.set_color(0xffff,0x9000)
            draw.string("undo", 32, 160, 175)
        else:
          draw.string("save", 136, 44,100)
          draw.set_font(fonts.sans18)
          draw.string("+{:d}".format(self._viewid), 136, 68,100)
          draw.set_font(fonts.sans24)

    def _draw_mood_face(self,x,y,happy=None,awake=None,unlessCombo=None):
        x = int(x)
        y = int(y)
        if(happy==None):
          if((not hasattr(self,"_cacheentry")) or (self._cacheentry==None)):
            happy=0.5
          else:
            happy = (self._cacheentry[1] & 0xffff)/1000
        if(awake==None):
          if((not hasattr(self,"_cacheentry")) or (self._cacheentry==None)):
            awake=0.5
          else:
            awake = ((self._cacheentry[1] >> 16)&0xffff)/1000

        #If it's unchanged no need to redraw
        if(unlessCombo!=None):
          if((happy==unlessCombo[0])and(awake==unlessCombo[1])):
            #Nice, we can save the bother then. Already done.
            return([happy,awake])

        draw = wasp.watch.drawable
        draw.blit(self.ICON,   int(x), int(y))
        self._draw_mouth(x,y,happy,awake)
        self._draw_eyes(x,y,happy,awake)
        return([happy,awake])

    def _draw_mouth(self,x,y,happy,awake):
        draw = wasp.watch.drawable
        disp = int((0.5-happy) * 15)
        h = 44+y
        draw.line(x+13, h+disp,          x+23, h+int(disp/2), 3, 0x0000) 
        draw.line(x+23, h+int(disp/2),   x+32, h,             3, 0x0000) 
        draw.line(x+32, h,               x+41, h+int(disp/2), 3, 0x0000) 
        draw.line(x+41, h+int(disp/2),   x+51, h+disp,        3, 0x0000) 

    def _draw_eyes(self,x,y,happy,awake):
        draw = wasp.watch.drawable
        h = y+22
        e = 1+int(awake * 10)
        e2 = int(e/2)
        if(e2<1):
            e2=1
        for i in [15,43]:
          draw.line(x+i+0, h,   x+i+2, h,        e2, 0x0000) 
          draw.line(x+i+3, h,   x+i+6, h,        e, 0x0000) 
          draw.line(x+i+7, h,   x+i+9, h,        e2, 0x0000) 

    def _draw_act_selector(self):
        draw = wasp.watch.drawable
        col = _editcol
        if(self._viewid>self._topid):
          draw.set_color(0,_newcol)

        draw.set_color(0,col)
        draw.string("<" ,0, 208, 34)
        draw.string("-" ,40, 208, 34)
        draw.string(">" ,200, 208, 34)
        draw.string("+" ,160, 208, 34)

        try:
            i = self._cacheentry[2]
            col = COLS[i % len(COLS)]
            draw.set_color(0,col)
        except Exception as e:
            pass

        draw.string("<" ,0, 112, 34)
        draw.string(">" ,200, 112, 34)
        draw.set_color(col)
        if(self._cacheentry==None):
            actstring = ""
        else:
            actstring = self._activities[self._cacheentry[2]].strip()
        draw.string(actstring,40 , 112, 160)



    #Current time to within 5 minutes
    def _get_rounded_now_ts(self,rounded=5):
        rounded*=60
        ts = time.mktime(wasp.watch.rtc.get_localtime()+(0,))
        if(rounded!=0):
          r = ts%rounded
          if(r>rounded/2):
            r-=rounded
          ts = ts - r
        return ts

    def _get_rounded_now(self,rounded=5):
        ts = self._get_rounded_now_ts
        lt = time.localtime(ts)
        return lt

    #Load the log to find topid and cacheprior
    def _load(self):
        gc.collect()
        try:
            with open("/flash/logs/"+self._filediff+"moodlog.csv", 'r') as file:
              file.seek(0, 2)       #0 bytes from end
              length = file.tell()
              self._topid = (length>>6)-1     #divided by 64 bytes
              file.seek(length-64,0)
              dataLine = str(file.read(64))
              self._cacheprior = self._parse_data_line(dataLine)
        except Exception as ex:
            self._cacheprior = self._cacheentry = _blankentry
            self._topid = self._viewid = 0
            print("MoodLoadExcep"+str(ex))
        gc.collect()

    #Load a particular entry
    def _loadentry(self,id):
        gc.collect()
        try:
            with open("/flash/logs/"+self._filediff+"moodlog.csv", 'r') as file:
              if(id<=0):
                #no prior entry. Damn.
                self._cacheprior = _blankentry
              else:
                file.seek((id-1)<<6,0)
                dataline = str(file.read(64))
                self._cacheprior = self._parse_data_line(dataline)
              if(id<=self._topid):
                file.seek(id<<6,0)
                dataline = str(file.read(64))
                self._cacheentry = self._parse_data_line(dataline)
        except Exception as e:
            self._cacheprior = self._cacheentry = _blankentry
            self._topid = self._viewid = 0
            print("EntLoadExcp:"+str(e))
        gc.collect()

    #Clone a entry - otherwise we end up editing both last/cache at once
    def _clone_entry(self,entry):
        if(entry==None):
          return None
        gc.collect()
        return array.array("L",[entry[0],entry[1],entry[2]])

    #When the undo button is hit
    def _undobut(self):
        if((self._viewid!=self._topid)or(self._showdaydiff!=0)):
            #Not dealing with deleting older than most recent.
            pass
        else:
            self._editentry(self._topid,None)
            self._reset()
            self._draw()

    #When the save button is hit
    def _savebut(self):
        if(self._viewid > self._topid):
          #Great, just append
          stringline = self._entry_to_string(self._cacheentry)
          gc.collect()
          try:
              with open("/flash/logs/moodlog.csv", 'a') as file:
                file.write(stringline)
          except Exception as e:
              print("MooSaveExcep:"+str(e))
          self._cacheprior = self._clone_entry(self._cacheentry)
          self._topid+=1
          self._checkforlogrotate()
        else:
          self._editentry(self._viewid,self._cacheentry)
        self._reset()


    # The trouble with "edit" is that we can't
    # just seek to the location in the file and
    # write over the bytes there. :( I tried.
    #
    # So we gotta just make a new file and
    # copy the entire contents altering just
    # the line we needed. Hopefully we can
    # rename rather than having to copy twice.
    #
    # send details=None to delete
    def _editentry(self,editid,details):
        gc.collect()
        os.rename("/flash/logs/"+self._filediff+"moodlog.csv", "/flash/logs/moodlogediting.csv")
        n=0
        try:
            with open("/flash/logs/moodlogediting.csv", 'r') as source:
              with open("/flash/logs/"+self._filediff+"moodlog.csv", 'w') as dest:
                while(n<editid):
                  dataline = source.read(64)
                  dest.write(dataline)
                  n+=1
                if(details!=None):
                  dataline = source.read(64)
                  dataline = self._entry_to_string(details)
                  gc.collect()
                  dest.write(dataline)
                else:
                  self._topid-=1
                while(n<=self._topid):
                  dataline = source.read(64)
                  dest.write(dataline)
                  n+=1
            os.remove("/flash/logs/moodlogediting.csv")
        except Exception as e:
          print("EntrEditExcep:"+str(e))
          try:
            os.rename("/flash/logs/moodlogediting.csv", "/flash/logs/"+self._filediff+"moodlog.csv")
          except:
            print("EntrEditExcep2:"+str(e))
            pass
        self._showdaydiff=0
        self._filediff = ""
        self._load()
        self._reset()

    #Rotate the logs. 
    def _logrotate(self):
        now = self._get_rounded_now(60)
        s="/flash/logs"
        try:
          os.mkdir(s)
        except:
          pass
        s = s+("/{:04d}".format(now[0]))
        try:
          os.mkdir(s)
        except:
          pass
        s = s+"/mood"
        try:
          os.mkdir(s)
        except:
          pass
        logdate = self._delta_now(now,-(now[3]+24)*60*60)
        fn = "/flash/logs/{:04d}/mood/{:04d}-{:02d}-{:02d}_moodlog.csv".format(
                 logdate[0],logdate[0],logdate[1],logdate[2])
        os.rename("/flash/logs/moodlog.csv", fn)
        self._topid = -1
        self._lastlogrotate = time.mktime(wasp.watch.rtc.get_localtime()+(0,))

    #If the face doesn't do it, we should manually rotate sometimes.
    def _checkforlogrotate(self):
        ts = time.mktime(wasp.watch.rtc.get_localtime()+(0,))
        diff = ts - self._lastlogrotate
        if(diff>24*60*60+60):
          self._logrotate()
           

    #Parse a line from the 64-byte-wide special CSV into an entry
    def _parse_data_line(self, dataline):
        ts = int(time.mktime((int(dataline[0:4]),int(dataline[5:7]),int(dataline[8:10]), int(dataline[11:13]),int(dataline[14:16]),0,1,0,0)))
        e = int(float(dataline[17:21])*1000) + (int(float(dataline[22:26])*1000)<<16)
        try:
            c = self._activities.index(dataline[27:62].strip())
        except Exception as ex:
            print("Exept:"+str(ex))
            c=0
        return(array.array("L",[ts,e,c]))


    #Convert an entry in to 64-byte wide CSV row 
    def _entry_to_string(self,entry):
        padtopic = self._activities[entry[2]][:35]
        while(len(padtopic)<35):
          padtopic+=" "
        lt = time.localtime(entry[0])
        h = entry[1] & 0xffff
        a = (entry[1] >> 16) & 0xffff
        line = "{:04d}-{:02d}-{:02d} {:02d}:{:02d},{:0.2f},{:0.2f},{}.\n".format(
                    lt[0],lt[1],lt[2],
                    lt[3],lt[4],
                    h/1000,a/1000,
                    padtopic);
        return line
       
    #Change currently selected activity
    def _act_change(self,direction):
        if(hasattr(self,"_activities")):
            self._currentact+=direction
            if(self._currentact>=len(self._activities)):
              self._currentact=0
            if(self._currentact<0):
              self._currentact=len(self._activities)-1
            if(self._cacheentry==None):
              self._cacheentry = self._blankentry
            self._cacheentry[2] = self._currentact



    #Change the currently viewed day
    def _switch_day(self,direction):
        self._showdaydiff+=direction
        if(self._showdaydiff>0):
          self._showdaydiff=0
          self._filediff = ""
          return True
        else:
          n = self._get_rounded_now(0)
          t = self._delta_now(n,self._showdaydiff*24*60*60)
          self._filediff = "{:04d}/mood/{:04d}-{:02d}-{:02d}_".format(t[0],t[0],t[1],t[2])
        if(self._showdaydiff==0):
          wasp.system.bar.clock = True
          self._filediff = ""
        else:
          wasp.system.bar.clock = False
        self._load()
        self._reset()
        self._viewid = self._topid
        self._draw()
        return False
          
        


    #Change the currently viewed entry
    def _switch_entry(self,direction):
        newid = self._viewid + direction
        if(newid<0):
          newid=0;
          wasp.watch.vibrator.pulse(duty=90, ms=500)
        if(newid>self._topid+1):
          newid=self._topid+1;
          wasp.watch.vibrator.pulse(duty=90, ms=500)
        if((self._showdaydiff!=0)and(newid>self._topid)):
            newid=self._topid;
            wasp.watch.vibrator.pulse(duty=90, ms=500)
        if(newid!=self._viewid):
          self._viewid = newid
          self._loadentry(newid)
          self._draw()
        


    #How to add/subtract a tuple date?
    def _delta_now(self,now,diff):
        t = time.mktime(now)
        t+=diff
        return(time.localtime(t)) 

