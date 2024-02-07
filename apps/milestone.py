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
# We call 'em csv but there's only one column so no actual commas.
# start with index.csv
# Every row is 16 chars long
# first 4 rows are names/topics.
# next X rows are timestamps
# 
# We can open the file read the first 64
# bytes as button-headers and skip to the
# end-16 to get the most recent timestamp
# and /16-4 is the number of entries.
#
# So, logrotation. Hummm.
#
# Every day with a way to view prior days
# I guess, so we can have some kinda date-prefix
# directory on all but today.
#
# Log-rotate can copy the first 4 lines of all
# files into a new skeleton, and also the last
# line so that we always know where to look back
# for prior.
#
# Generally ignore first line in counts?
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
        pass

    def foreground(self):
        wasp.system.request_event(wasp.EventMask.TOUCH)
        self._fullpath = []
        self._cornerbuttons("index")

    def background(self):
        if(hasattr(self,"_data")):
            del(self._data)
        if(hasattr(self,"_fullpath")):
            del(self._fullpath)
        pass

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
        if(fname=="MJ"):
            self._logrotate()
        wasp.system.bar.clock = True
        wasp.system.bar.draw()
        draw = wasp.watch.drawable
        draw.fill(0, 0, 0, 240, 32)
        draw.fill(bgcol, 0, 32, 240, 208)
        draw.set_color(fgcol,bgcol)
        draw.line(  1,  120, 238, 120, 4, 0x0000) 
        draw.line(120,   1,  120, 214, 4, 0x0000)
        self._loaddata(fname)
        if(hasattr(self,"_data")):
            self._fullpath.append(fname)
            if(self._data[0]=="--==leafnode==--"):
                self._addtimestamps()
            else:
                if(len(self._data)>4):
                    draw.set_color(bgcol,fgcol)
                    draw.set_font(fonts.sans18)
                    draw.string(self._tstostr(self._data[4])[0:16],0, 220, width=240)
                if(len(self._data)>0):
                    ll = self._loadlast(self._data[0])
                    draw.set_font(fonts.sans24)
                    draw.set_color(fgcol,bgcol)
                    draw.string(self._data[0],               0,   47, width=116)
                    draw.set_font(fonts.sans18)
                    draw.set_color(fgcol,bgcol)
                    draw.string(ll[0],0,   71, width=116)
                    draw.string(ll[1],0,   96, width=116)
                if(len(self._data)>1):
                    ll = self._loadlast(self._data[1])
                    draw.set_font(fonts.sans24)
                    draw.set_color(fgcol,bgcol)
                    draw.string(self._data[1],123, 47, width=116)
                    draw.set_font(fonts.sans18)
                    draw.set_color(fgcol,bgcol)
                    draw.string(ll[0],123,   71, width=116)
                    draw.string(ll[1],123,   96, width=116)
                if(len(self._data)>2):
                    ll = self._loadlast(self._data[2])
                    draw.set_font(fonts.sans24)
                    draw.set_color(fgcol,bgcol)
                    draw.string(self._data[2],0,   145, width=116)
                    draw.set_font(fonts.sans18)
                    draw.set_color(fgcol,bgcol)
                    draw.string(ll[0],0,   169, width=116)
                    draw.string(ll[1],0,   194, width=116)
                if(len(self._data)>3):
                    ll = self._loadlast(self._data[3])
                    draw.set_font(fonts.sans24)
                    draw.set_color(fgcol,bgcol)
                    draw.string("{}".format(self._data[3]),123, 145, width=116)
                    draw.set_font(fonts.sans18)
                    draw.set_color(fgcol,bgcol)
                    draw.string(ll[0],123, 169, width=116)
                    draw.string(ll[1],123, 194, width=116)


    # Blank out all but the touched button 
    def _cornerfills(self,idx):
      draw = wasp.watch.drawable
      if(idx!=0):
        draw.fill(0x0000,   0,  32, 119, 88)
      if(idx!=1):
        draw.fill(0x0000, 120,  32, 119, 88)
      if(idx!=2):
        draw.fill(0x0000,   0, 120, 119, 88)
      if(idx!=3):
        draw.fill(0x0000, 120, 120, 119, 88)


    #Our screen is touched at an index number
    def _touched(self,idx):
        self._cornerfills(idx)
        if(hasattr(self,"_data")):
            if(len(self._data)>idx):
               return self._cornerbuttons(self._data[idx])
        wasp.system.switch(wasp.system.quick_ring[0])


    def _fullname(self,fname):
        return "/flash/logs/mile/{}.csv".format(fname)


    def _savelast(self,tfname,tstr):
        """ we append a timestamp to the file, it's been immantized """
        try:
            with open(tfname, 'a') as file:
                file.seek(0, 2)       #0 bytes from end
                file.write(tstr)
        except FileNotFoundError as e:
            print("nonode:"+str(fname))
            pass

    def _loadlast(self,fname):
        """ A display string for the node based on it's final line """
        tfname = self._fullname(fname)
        d = time.time()
        try:
            with open(tfname, 'r') as file:
                file.seek(0, 2)       #0 bytes from end
                length = file.tell()
                num = int((length/17)-5)    #4 names, plus one hang-over date from previous logrotate
                if(num>=0):
                    file.seek(length-17, 0)
                    d2 = self._parsedate(file.read(17).strip())
                    d2 = d2-d
                    s="??"
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
                    return("{}".format(num),s)
                else:
                    return("{:d}".format(num),"??");
        except FileNotFoundError as e:
            pass
        return "0","-0s"
        
        

    #Each row is 17 bytes including the \n at the end of the row
    def _loaddata(self,fname):
        d = []
        tfname = self._fullname(fname)

        try: 
            with open(tfname, 'r') as file:
                print(tfname+" exists, boring")
                pass
        except FileNotFoundError as e:
            lf = "--==leafnode==--"
            try:
                with open(tfname, 'w') as file:
                    file.write(lf+"\n")
                    file.write(fname.ljust(16)+"\n")
                    file.write(("".ljust(16))+"\n")
                    file.write(lf+"\n")
                    file.write(self._nowstr())
            except Exception as e:
                print("Can't create leaf milestone "+tfname)
                pass

        with open(tfname, 'r') as file:
            file.seek(0, 2)       #0 bytes from end
            length = file.tell()
            file.seek(0, 0)
            for i in range(0,4):
                d.append(file.read(17).strip())   #Four corner names
            file.seek(length-17, 0)     
            d.append(self._parsedate(file.read(17).strip()))
            self._data = d


    def _addtimestamps(self):
        tstr = self._nowstr()
        for fn in self._fullpath:
            self._savelast(self._fullname(fn),tstr)
        wasp.system.switch(wasp.system.quick_ring[0])
            
       
    def _nowstr(self):
        now = wasp.watch.rtc.get_localtime()
        return("{:04d}-{:02d}-{:02d} {:02d}:{:02d}\n".format(now[0],now[1],now[2],now[3],now[4]))
    
    def _tstostr(self,ts):
        ttuple = time.localtime(ts)
        return("{:04d}-{:02d}-{:02d} {:02d}:{:02d}".format(ttuple[0], ttuple[1], ttuple[2], ttuple[3], ttuple[4]))

 
    def _parsedate(self,dstring):
        if((dstring==None)or(dstring=="")):
            return 0
        date_tuple = tuple(map(int, dstring.replace(":", "-").replace(" ", "-").split("-"))) + (0, 0, 0, 0)
        dt = time.mktime(date_tuple)
        return dt

    def _logrotate(self):
        """ Bank all the logs and start afresh with a zero count """
        gc.collect()
        from shell import mv
        import os
        now = wasp.watch.rtc.get_localtime()
        dest = "/flash/logs/milelog"
        try:
          os.mkdir(dest)
        except FileExistsError:
            pass
        dest+= "/{:04d}-{:02d}-{:02d}_{:02d}".format(now[0],now[1],now[2],now[3])
        try:
            os.mkdir(dest)
        except FileExistsError:
            pass
        dest+="/"
        files = wasp.watch.os.listdir("/flash/logs/mile/")
        for file in files:
            print("Rotating log file:"+file)
            mv("/flash/logs/mile/"+file,dest+file)
            with open(dest+file, 'r') as sfile:
                sfile.seek(0, 2)
                length = sfile.tell()
                sfile.seek(0, 0)
                with open("/flash/logs/mile/"+file, 'w') as dfile:
                    for i in range(0,4):
                        l = sfile.read(17)
                        dfile.write(l)
                    sfile.seek(length-17, 0)
                    l = sfile.read(17)
                    dfile.write(l)
            gc.collect()
        del(mv)
        del(os)
        gc.collect()



