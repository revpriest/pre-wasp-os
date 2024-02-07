# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2024 Adam Priest pre@dalliance.net

"""Milestone
~~~~~~~~~~~~~

An app to track the occurrences of milestones. Suggested use is
tracking what food & drink is consumed but it's not proscriptive.

.. figure:: res/screenshots/MilestoneApp.png
    :width: 179
"""

#
# We wanna work entirely through the filesystem really,
# very very few RAM vars if we can help it.
#
# So the filesystem as currently implimented is bullshit.
# Why so complex? Why put the timestamps on the same files
# as the menu-names? WTF were you thinking? Trying to be all
# fancy.
# 
# Four lines in the index file, plus a _stamps that has the
# times of the actual milestones in it.
#

#
# 

import wasp
import array
import fonts
import gc
from micropython import const
import time

class MilestoneApp():
    NAME = "Milestone"

    def __init__(self):
        import os
        try:
            os.mkdir("/flash/logs")
        except:
            pass
        try:
            os.mkdir("/flash/logs/mile")
        except:
            pass
        try:
            os.mkdir("/flash/logs/milelog")
        except:
            pass
        del(os)
        wasp.mile_logrotate = self._logrotate


    def foreground(self):
        wasp.system.request_event(wasp.EventMask.SWIPE_UPDOWN | wasp.EventMask.TOUCH)
        self._fullpath = []
        self._cornerbuttons("index")


    def background(self):
        gc.collect()
        if(hasattr(self,"_data")):
            del(self._data)
        if(hasattr(self,"_fullpath")):
            del(self._fullpath)
        pass


    def unregister(self):
        del(wasp.mile_logrotate)
        pass


    def swipe(self, event):
        if event[0] == wasp.EventType.DOWN:
            self._cornerbuttons("opt")
            return False
        return True 


    def touch(self, event):
        if(event[2]<120):
            if(event[1]<120):
                return self._touched(0)
            else:
                return self._touched(1)
        else:
            if(event[1]<120):
                return self._touched(2)
            else:
                return self._touched(3)

    def _draw(self):
        pass


    def _cornerbuttons(self,fname,bgcol=0x59af,fgcol=0xffff):
        (fname,xcol) = self._splitname(fname,bgcol)
        draw = wasp.watch.drawable
        draw.fill(0, 0, 0, 240, 32)
        wasp.system.bar.clock = True
        wasp.system.bar.draw()
        draw.set_color(fgcol,bgcol)
        self._loaddata(fname)
        if(hasattr(self,"_data")):
            self._fullpath.append(fname)
            if(self._data==0):
                #No more buttons, we hit the leaf
                return self._addtimestamps()
            else:
                if(len(self._data)>4):
                    draw.fill(fgcol, 0, 220, 240, 5)
                    draw.set_font(fonts.sans18)
                    draw.set_color(0x0000,0xffff)
                    draw.string(self._tstostr(self._data[4])[0:16],0, 222, width=240)
                if(len(self._data)>0):
                    self._cornerbutton(0,0,32,120,93,bgcol,fgcol)
                if(len(self._data)>1):
                    self._cornerbutton(1,120,32,120,93,bgcol,fgcol)
                if(len(self._data)>2):
                    self._cornerbutton(2,0,129,120,93,bgcol,fgcol)
                if(len(self._data)>3):
                    self._cornerbutton(3,120,129,120,93,bgcol,fgcol)
            draw.line(  1,  127, 238, 127, 4, 0x0000) 
            draw.line(119,   1,  119, 219, 4, 0x0000)


    def _cornerbutton(self,n,x,y,w,h,col,fgcol):
        draw = wasp.watch.drawable
        s = self._data[n]
        if isinstance(s, str):
            (s,col) = self._splitname(s,col)
            ll = self._loadts(s)
        else:
          ll = [s[1],s[2]]
          s = s[0]
        draw.fill(col, x, y, w, h)
        draw.set_font(fonts.sans24)
        draw.set_color(fgcol,col)
        draw.string(s.capitalize(),  x,   y+11, width=117)
        draw.set_font(fonts.sans18)
        draw.set_color(fgcol,col)
        draw.string(ll[0],           x,   y+46, width=117)
        draw.string(ll[1],           x,   y+64, width=117)


    def _splitname(self,tosplit,defaultcol):
        """ If the node-name has a comma then its probably got a color """
        col = -1
        try:
            bits = tosplit.split(",")
            if(len(bits)<=1):
                return (tosplit,defaultcol)
            try:
                col = int(bits[1],16)
            except:
                pass
            if((col <= 16777215)and(col>=0)):
                return (bits[0],col)
            return(bits[0],0)
        except Exception as e:
            print("Except:"+str(e)+":"+str(tosplit)) 
        return(tosplit,defaultcol)


    # Blank out all but the touched button 
    def _cornerfills(self,idx):
      draw = wasp.watch.drawable
      if(idx!=0):
        draw.fill(0x0000,   0,  32, 120, 93)
      if(idx!=1):
        draw.fill(0x0000, 120,  32, 120, 93)
      if(idx!=2):
        draw.fill(0x0000,   0, 129, 120, 93)
      if(idx!=3):
        draw.fill(0x0000, 120, 129, 120, 93)


    #Our screen is touched at an index number
    def _touched(self,idx):
        self._cornerfills(idx)
        if(hasattr(self,"_data")):
            if(len(self._data)>idx):
                if isinstance(self._data[0], str):
                    return self._cornerbuttons(self._data[idx])
                else:
                    return self._execute_option(self._data[idx]) 
        wasp.system.switch(wasp.system.quick_ring[0])


    def _execute_option(self,opt):
        if(opt[0]=="log"):
            self._logrotate()
        else:
            pass
        self._cornerbuttons("index")
        

    # We have 3 files for each milestone type,
    # the "main" is in /mile/{name} and tells us what buttons to draw
    # the "now" is in /milelog/{name}_latest and is the most recent timestamp
    # the "log" is in /milelog/{name}_log and is appended at each milestone
    # The "log" is rotated into a directory each night (or week?)
    # so the latest count for "done today (or this week?) is the size of the record file.
    # there are good reasons to expect any of these files to be empty,
    # either for leaf nodes with no buttons or but buttons never
    # yet pressed or for buttons pressed but not yet today (or week?)
    #
    def _fullname(self,fname,x="m"):
        if(x=="m"): #main
            return "/flash/logs/mile/{}.csv".format(fname.lower())
        elif(x=="n"):   #now
            return "/flash/logs/milelog/{}_now.csv".format(fname.lower())
        else:   #Implied "l" for log record
            return "/flash/logs/milelog/{}_log.csv".format(fname.lower())


    def _savemilepassed(self,fname,tstr):
        """ we append a timestamp to the file, it's been immantized """
        rfname = self._fullname(fname,"l")
        try:
            with open(rfname, 'a') as file:
                file.seek(0, 2)       #0 bytes from end
                file.write(tstr)
        except Exception as e:
            pass

        rfname = self._fullname(fname,"n")
        try:
            with open(rfname, 'w') as file:
                file.write(tstr)
        except Exception as e:
            pass


    def _loadts(self,fname):
        """ two display strings for the latest timestamp, diff and count """
        s="??"
        d = time.mktime(wasp.watch.rtc.get_localtime()+(0,))
        d2 = self._loadt(fname) - d
        if(abs(d2)<60):
          s="{}s".format(int(d2))
        elif(abs(d2)<60*60):
          s="{}m".format(int(d2/60))
        elif(abs(d2)<24*60*60):
          s="{}h".format(int(d2/60/60))
        elif(abs(d2)<7*60*60):
          s="{}d".format(int(d2/24/60/60))
        elif(abs(d2)<7*60*60):
          s="{}w".format(int(d2/7/24/60/60))
        elif(abs(d2)<7*60*60):
          s="{}y".format(int(d2/365/24/60/60))

        cnt=0
        tfname = self._fullname(fname,"l")
        try:
            with open(tfname, 'r') as file:
                file.seek(0, 2)       #0 bytes from end
                length = file.tell()
                cnt = int(length/20)
        except Exception as e:
            pass
        return("{}".format(cnt),s)


    def _loadt(self,fname):
        """ Get the unix timestamp for the latest milestone event """
        tfname = self._fullname(fname,"n")
        d = time.mktime(wasp.watch.rtc.get_localtime()+(0,))
        try:
            with open(tfname, 'r') as file:
                 return self._parsedate(file.read(20).strip())
        except Exception as e:
            pass
        return 0
        
        

    #4 rows, comma-separated. Name, then col.
    def _loaddata(self,fname):
        if(fname=="opt"):
            self._data = [["log","rotate","now"],[" "," "," "],[" "," "," "],[" "," "," "]]
            return self._data
        d = []
        tfname = self._fullname(fname,"m")
        self._data = None
        try:
            with open(tfname, 'r') as file:
                for i in range(0,4):
                    s = file.readline()
                    d.append(s)
            d.append(self._loadt(fname))
            self._data = d
        except:
            #No file? Leaf node!
            self._data = 0
        return self._data


    def _addtimestamps(self):
        tstr = self._nowstr()
        for fn in self._fullpath:
            gc.collect()
            self._savemilepassed(fn,tstr)
        wasp.watch.drawable.fill(0x03, 0, 0, 240, 240)
        wasp.system.switch(wasp.system.quick_ring[0])
            
       
    def _nowstr(self):
        now = wasp.watch.rtc.get_localtime()
        return("{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}\n".format(now[0],now[1],now[2],now[3],now[4],now[5]))
    
    def _tstostr(self,ts):
        ttuple = time.localtime(ts)
        return("{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(ttuple[0], ttuple[1], ttuple[2], ttuple[3], ttuple[4],ttuple[5]))

 
    def _parsedate(self,dstring):
        if((dstring==None)or(dstring=="")):
            return 0
        date_tuple = tuple(map(int, dstring.replace(":", "-").replace(" ", "-").split("-"))) + (0, 0, 0)
        dt = time.mktime(date_tuple)
        return dt

    def _logrotate(self):
        """ Bank all the logs and start afresh with a zero count """
        gc.collect()
        from shell import mv
        import os
        now = wasp.watch.rtc.get_localtime()
        dest = "/flash/logs/{:04d}".format(now[0])
        try:
          os.mkdir(dest)
        except Exception:
            pass
        dest += "/mile"
        try:
          os.mkdir(dest)
        except Exception:
            pass
        dest +="/{:04d}-{:02d}-{:02d}_{:02d}".format(now[0],now[1],now[2],now[3])
        try:
          os.mkdir(dest)
        except Exception:
            pass
        dest+="/"
        files = wasp.watch.os.listdir("/flash/logs/milelog/")
        for file in files:
            if(file.endswith("_log.csv")):
                print("Rotating log file:"+file)
                mv("/flash/logs/milelog/"+file,dest+file)
            else:
                print("Skipping non-log file "+file)
            gc.collect()
        del(mv)
        del(os)
        gc.collect()



