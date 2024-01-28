"""Monolith clock
~~~~~~~~~~~~~~~~

It's Pre's mega-face! We do it all
and use lots of ram to do it. You
will be limited how many other apps
you can run along side this one.
 
.. figure:: res/screenshots/MonolithApp.png
    :width: 179
"""

# * Clock
#   * Funky font time, using companion font apps
#   * day, date, month, year
#   * seconds
#   * Half-second flashing colon
#   * Change color
#   * Keep-alive during charging to act as a clock
# * built-in stopwatch and timer
# * show heart-rate 
#   * allows regular sampling and logging
# * Show step-counts
#   * allows setting a lap-counter for specific trips
#   * change reset-schedule (Will need to disable default step-logger)
#   * log in 5/15/60 minute chunks to a daily csv
# * Stats-page 
#   * free-storage,
#   * free-ram, 
#   * battery-percent
#   * Shows scheduled reset/log-rotate time
# * Integration with the mood logging app to show
#   the latest mood as a face too.
# * Compensates for steps missed before reboot

import wasp
import time
import array
import gc
from micropython import const

#We use a word-array for as many vars as possible for memory reasons
#Consts seem to come without taking any RAM at all.
#the vars up till _maxsaved are saved in preferences.
_FONTNUM      = const(0) 
_CLOCKCOL     = const(1) 
_STEPLOGFREQ  = const(2)
_HEARTONOFF   = const(3)
_HEARTINTERVAL= const(4)
_LOGROTTIME   = const(5) 
_SHOWMOOD     = const(6) 
_SHAKEWAKE    = const(7) 
_MAXSAVED     = const(8)

_HEARTHASH    = const(8)
_TICKCOUNT    = const(9)
_ISAWAKE      = const(10)
_SCREEN       = const(11) 
_SCREENCNT    = const(12) 
_STOPWATCHRUN = const(13) 
_SETTIME      = const(14)
_SETTIMEH     = const(15)
_ZACCEL       = const(16)
_FLASHBUZZTIME= const(17)
_LASTHEARTRATE= const(18)
_LOADATSTART  = const(19)
_MAXVARS      = const(20) 

#Longs too
_TIMESTAMP                = const(0)
_TOUCHTIME                = const(1)
_STOPWATCHTIME            = const(2)
_ALARM                    = const(3)
_CDOWN                    = const(4)
_LASTHEARTRATETIME        = const(5)
_STEPCOUNT                = const(6)
_LASTSTEPS                = const(7)
_MISSEDSTEPS              = const(8)
_STEPSSINCE               = const(9)        #The lap-mode
_STEPSATLASTLOG           = const(10)       #How many steps last time we wrote to the log?
_NEXTHEARTMEASUREMENTTIME = const(11)
_MAXLONGVARS              = const(12) 


#16 bytes to define these two strings,
#8 to define them in one along with any other TLAs
#We go go with one string with them all:
_TLASTRING = 'JanFebMarAprMayJunJulAugSepOctNovDecMonTueWedThuFriSatSun'
_MONTHSTART = const(0)
_DAYSTART   = const(3*12)

class MonolithApp():
    """Pre's monolithic watch face."""
    NAME = 'MonolithApp'

    ##
    # Sys stuff
    ##
    def __init__(self):
        wasp.system.bar.clock = False
        #sys
        try:
            self._lastnow = self._now = wasp.watch.rtc.get_localtime()+(0,)
            self._fontref = None
            self._wordvars = array.array("H",range(_MAXVARS))
            self._longvars = array.array("L",range(_MAXLONGVARS))

            self._wordvars[_TICKCOUNT]=0
            self._wordvars[_CLOCKCOL]=0xffff
            self._wordvars[_LOGROTTIME]=4
            self._wordvars[_SHOWMOOD]=1
            self._wordvars[_STEPLOGFREQ]=15
            self._wordvars[_STOPWATCHRUN]=0
            self._wordvars[_FLASHBUZZTIME]=10
            self._wordvars[_HEARTONOFF]=0
            self._wordvars[_HEARTINTERVAL]=0
            self._wordvars[_LASTHEARTRATE]=0
            self._wordvars[_LOADATSTART]=1
            self._wordvars[_SHAKEWAKE]=1

            self._longvars[_TIMESTAMP] = 0
            self._longvars[_STOPWATCHTIME] = 0
            self._longvars[_ALARM] = 0
            self._longvars[_CDOWN] = 0
            self._longvars[_STEPCOUNT] = 0
            self._longvars[_MISSEDSTEPS] = 0
            self._longvars[_STEPSSINCE] = 0
            self._longvars[_STEPSATLASTLOG] = 0
            self._longvars[_LASTHEARTRATETIME] = 0 
            self._longvars[_NEXTHEARTMEASUREMENTTIME] = 0 

            self._flashbuzz  = ""
            self._timesetfun = None
            self._hrdata     = None
            self._reset()
    

            #ui
            self._wakeupcheck()
            self._switchscreen(0)
            self._longvars[_TOUCHTIME]= 0
        except Exception as e:
            print("Except:"+str(e))


    def _reset(self):
        #Invalidate things cached to avoid redrawing
        self._wordvars[_HEARTHASH]=65534
        self._lastnow = (-1,-1,-1,-1,-1,-1)
        self._shownmood = [-1,-1]
        self._laststeps = -1
        self._longvars[_LASTSTEPS] = 65535*32768


    def foreground(self):
        self._wordvars[_ISAWAKE] = 1
        wasp.system.bar.clock = False
        wasp.system.request_tick(500)
        wasp.system.request_event(wasp.EventMask.TOUCH)
        if(self._wordvars[_LOADATSTART]==1):
            self._wordvars[_LOADATSTART]=0
            self._load()
        self._draw()


    def background(self):    
        self._wordvars[_ISAWAKE] = 0


    def sleep(self):
        self._wordvars[_ISAWAKE] = 0
        return True

    def wake(self):
        self._wordvars[_ISAWAKE] = 1
        self._update()

    ##
    # Tick stuff
    ##

    #Ticking while awake
    def tick(self, ticks):
        self._wordvars[_TICKCOUNT] =(self._wordvars[_TICKCOUNT]+1)%65535
        if(self._wordvars[_TICKCOUNT]%2==1):
          #Half-second tick to flash the colon
          self._flashColon(False)
        else:
          #On-second tick to update every second
          if(self._wordvars[_STOPWATCHRUN]==1):
            self._longvars[_STOPWATCHTIME]+=1
          self._update()
          self._flashColon(True)
          self._lastnow = self._now


    #Ticking while asleep
    def _wakeupcheck(self):
        self._now = wasp.watch.rtc.get_localtime()+(0,)
        self._longvars[_TIMESTAMP] =  int(time.mktime(self._now))
        wasp.system.set_alarm(self._longvars[_TIMESTAMP]+1,self._wakeupcheck)
        wake=False

        if(self._hrdata!=None):
          self._takeheartsamples()
        elif((self._longvars[_NEXTHEARTMEASUREMENTTIME]>0) and 
             (self._longvars[_TIMESTAMP] >= self._longvars[_NEXTHEARTMEASUREMENTTIME])):
          self._startnewheartmeasurement()
          wake=True

        accel = wasp.watch.accel.accel_xyz()
        if(self._wordvars[_SHAKEWAKE]!=0):
            if(((int(self._wordvars[_ZACCEL])-2000)>300)and(accel[2]<-800)):
              wake=True
              if(self._wordvars[_SHAKEWAKE]==2):
                wasp.watch.vibrator.pulse(duty=80, ms=80)
              elif(self._wordvars[_SHAKEWAKE]==3):
                wasp.watch.vibrator.pulse(duty=20, ms=150)
        self._wordvars[_ZACCEL] = int(accel[2]+2000)

        if((self._longvars[_ALARM]>0)and(self._longvars[_TIMESTAMP] >= self._longvars[_ALARM])):
          self._soundalarm()
          wake=True

        if((self._longvars[_CDOWN]>0)and(self._longvars[_TIMESTAMP] >= self._longvars[_CDOWN])):
          self._endcdown()
          wake=True

        if((wake)and(self._wordvars[_ISAWAKE]==0)):
            wasp.system.wake()
            wasp.system.switch(self)

        #Update step-counter and maybe save a log
        self._updatestepcount()
        if(self._wordvars[_STEPLOGFREQ]>0):
            if((self._now[5]==0)and((self._now[4]%self._wordvars[_STEPLOGFREQ])==0)):
                self._writesteplog()

    ##
    # Step counter
    ##

    # get a number from the device
    def _updatestepcount(self):
        try:
          self._longvars[_STEPCOUNT] = wasp.watch.accel.steps
        except Exception as e:
          #If it excepts, it probably needs to be resets. Maybe we uninstalled step-logger.
          if(self._longvars[_STEPCOUNT]!=3):
            self._longvars[_STEPCOUNT]=3
            res = wasp.watch.accel.reset()

    #Write a string to the step-log.
    #We create a new one with a date-header if it's blank
    def _writesteplog(self,strtowrite=None,timestowrite=1):
        self._mkdirs()
        if(strtowrite==None):
          strtowrite = self._longvars[_STEPCOUNT]
          if(strtowrite>=self._longvars[_STEPSATLASTLOG]):
            strtowrite = "{:d},".format(self._longvars[_STEPCOUNT] - self._longvars[_STEPSATLASTLOG])
        try:
          with open(self._steplogname(), 'a') as file:
              file.seek(0, 2)       #0 bytes from end
              length = file.tell()
              if(length==0):
                self._writestepheader(file)
              for i in range(0,timestowrite):
                file.write(strtowrite)
        except Exception as e:  # Didn't exist?
            print("StepLogExcep3:"+str(e))
            wasp.system.notify(wasp.watch.rtc.get_uptime_ms(),{"title":"LogFail","body":"Can't write step-log file:"+str(e)})
        self._longvars[_STEPSATLASTLOG] = self._longvars[_STEPCOUNT]
        gc.collect()

    #Saving the step-log: filename 
    def _steplogname(self):
        return "/flash/logs/{:04d}/steps/{:04d}-{:02d}-{:02d}_stepslog.csv".format(self._now[0],self._now[0],self._now[1],self._now[2])


    #Saving the step-log, header col
    def _writestepheader(self,file): 
        file.write("{:04d}-{:02d}-{:02d},".format(self._now[0],self._now[1],self._now[2]))


    ###
    # Heart stuff
    ###

    #Starting the heart measurement
    def _startnewheartmeasurement(self):
        if((self._wordvars[_HEARTONOFF]==1) and (self._wordvars[_HEARTINTERVAL]>0)):
          self._longvars[_NEXTHEARTMEASUREMENTTIME] = self._longvars[_TIMESTAMP]+self._wordvars[_HEARTINTERVAL]
        if(self._wordvars[_HEARTONOFF]>0):
          import ppg
          wasp.watch.hrs.enable()
          self._hrdata = ppg.PPG(wasp.watch.hrs.read_hrs())
          del ppg
          gc.collect()

    def _takeheartsamples(self):
        import machine
        t = machine.Timer(2, period=8000000)
        t.start()
        i=0
        while(i<24):
          while(t.time() < i*41666):
            pass
          spl = self._hrdata.preprocess(wasp.watch.hrs.read_hrs())
          i=i+1
        t.stop()
        del t
        del machine

        if(len(self._hrdata.data)>=10*24):
          x = self._hrdata.get_heart_rate();
          if(x==None):
            x=0
          self._wordvars[_LASTHEARTRATE]=x
          self._longvars[_LASTHEARTRATETIME] = self._longvars[_TIMESTAMP]
          self._saveheartlog()
          self._stopheartrecording()
        gc.collect()

    def _saveheartlog(self):
        self._mkdirs()
        if((self._wordvars[_LASTHEARTRATE]!=None)and(self._wordvars[_LASTHEARTRATE]>10)and(self._wordvars[_LASTHEARTRATE]<500)):
            try:
              fn = "/flash/logs/{:04d}/heart/{:04d}-{:02d}-{:02d}_heartlog.csv".format(self._now[0],self._now[0],self._now[1],self._now[2])
              with open(fn, 'a') as file:
                file.write("{:04d}-{:02d}-{:02d} {:02d}:{:02d},{:03d}\n".format(
                            self._now[0],self._now[1],self._now[2],self._now[3],self._now[4],self._wordvars[_LASTHEARTRATE]))
            except Exception as e:
                wasp.system.notify(wasp.watch.rtc.get_uptime_ms(),{"title":"Exception","body":"Can't write heart log: "+str(e)})
                print("HeartSaveExcep:"+str(e))

        gc.collect()

    def _stopheartrecording(self):
        wasp.watch.hrs.disable()
        self._hrdata = None
        gc.collect()


    ##
    # Touch stuff
    ##

    def touch(self, event):
        if(self._wordvars[_SCREEN]==0):
          #Normal face, double-tap required
          if(self._longvars[_TIMESTAMP]>self._longvars[_TOUCHTIME]+2):
            self._longvars[_TOUCHTIME] = self._longvars[_TIMESTAMP]
          else:
              self._cornertouches(event[1],event[2],(self._taptopleft, self._taptopright, self._tapbotleft, self._tapbotright),False)
        elif(self._wordvars[_SCREEN]==2):
          self._timesettouches(event[1],event[2])
        elif(self._wordvars[_SCREEN]==3):
          self._datesettouches(event[1],event[2])
        else:
          self._cornertouches(event[1],event[2],self._buttonfuns)


    def _cornertouches(self,x,y,funs,showChoice=True):
      if((funs==()) or (funs==None)):
        return
      wasp.watch.vibrator.pulse(duty=50, ms=30)
      if(y<120):
        if(x<120):
          if(showChoice): self._cornerfills(0)
          return funs[0]()
        else:
          if(showChoice): self._cornerfills(1)
          return funs[1]()
      else:
        if(x<120):
          if(showChoice): self._cornerfills(2)
          return funs[2]()
        else:
          if(showChoice): self._cornerfills(3)
          return funs[3]()


    # Switch to a screen. 0=default face. 1=corner-buttons.
    def _switchscreen(self,val=0,wait=1):
        self._wordvars[_SCREENCNT] = wait
        if(val!=self._wordvars[_SCREEN]):
            self._wordvars[_SCREEN]=val
            if(val==0):
                self._draw()
        

    ##
    # Draw stuff
    ##

    #Preview the clock
    def preview(self):
        wasp.system.bar.clock = False
        self._draw()
        self._flashColon(True)


    #Draw from scratch, blank the update
    def _draw(self):
        wasp.watch.drawable.set_color(0)
        wasp.watch.drawable.fill()
        self._reset()
        wasp.system.bar.draw()
        self._update()

    #Flash the colon
    def _flashColon(self,onOff):
        if(self._wordvars[_SCREEN]==0):
            if(onOff):
                if(self._fontref!=None):
                    wasp.watch.drawable.blit(self._fontref[10], 96, 68,fg=self._wordvars[_CLOCKCOL])
                else:
                    wasp.watch.drawable.set_color(self._wordvars[_CLOCKCOL])
                    wasp.watch.drawable.string(":", 96, 80, width=5)
                    
            else:
                wasp.watch.drawable.fill(0x0000, 96, 68, 5, 45)



    #Normal watch-face drawing, update only what changed.
    def _update(self):
        wasp.system.bar.update()

        #Stay-awake as a clock when I'm charging it in bed
        if wasp.watch.battery.charging():
          wasp.system.keep_awake()

        #Check for log-rotation
        if((self._now[5]==1)and(self._now[4]==0)and(self._now[3]==self._wordvars[_LOGROTTIME])):
          self._logrotate()

        #modal updates
        if(self._wordvars[_SCREEN]==0):
            self._updatewatch()
        else:
            self._updatewait()

        #Alarm or countdown flash a buzzing message
        if(self._flashbuzz!=""):
          self._wordvars[_FLASHBUZZTIME]-=1
          wasp.system.keep_awake()
          if(self._wordvars[_FLASHBUZZTIME]>0):
            if(self._wordvars[_FLASHBUZZTIME]%2==1):
              wasp.watch.vibrator.pulse(duty=80, ms=100)
              wasp.watch.drawable.set_color(0xffff,0x7000)
              wasp.watch.drawable.string(self._flashbuzz, 50, 0, width=139)
            else:
              wasp.watch.vibrator.pulse(duty=20, ms=500)
              wasp.watch.drawable.fill(0x7000,50,0,139,25)
          else:
            self._flashbuzz=""
            self._wordvars[_FLASHBUZZTIME]=10
            self._draw()


    #Update when we are waiting on a full-screen button-input, no drawing to do.
    def _updatewait(self):
        if(self._wordvars[_SCREENCNT]<=1):
            self._wordvars[_SCREENCNT]=0
            self._switchscreen(0)
            self._draw()
        else:
          self._wordvars[_SCREENCNT]-=1
          

    #Update when in watch-face
    def _updatewatch(self):
        wasp.watch.drawable.set_color(self._wordvars[_CLOCKCOL])

        #Main big clock-face
        if(self._fontref!=None):
            if(self._lastnow[3] != self._now[3]):
              wasp.watch.drawable.blit(self._fontref[self._now[3] // 10],  0, 70, fg=self._wordvars[_CLOCKCOL])
              wasp.watch.drawable.blit(self._fontref[self._now[3]  % 10], 45, 70, fg=self._wordvars[_CLOCKCOL])
            if(self._lastnow[4] != self._now[4]):
              wasp.watch.drawable.blit(self._fontref[self._now[4] // 10], 110, 70, fg=self._wordvars[_CLOCKCOL])
              wasp.watch.drawable.blit(self._fontref[self._now[4]  % 10], 155, 70, fg=self._wordvars[_CLOCKCOL])
        else:
            wasp.watch.drawable.string("{:02d}".format(self._now[3]),  23, 80, width=45)
            wasp.watch.drawable.string("{:02d}".format(self._now[4]), 123, 80, width=45)


        #Cdown/Stop-Watch/Alarm times below
        y=130
        if(self._longvars[_STOPWATCHTIME]>0):
            self._drawtimer(130,self._longvars[_STOPWATCHTIME])
            wasp.watch.drawable.blit(stopwatchicon,  0, y-4, fg=0x1B7A)
            y+=32
        if(self._longvars[_CDOWN] > 0):
            diff = self._longvars[_CDOWN] - self._longvars[_TIMESTAMP]
            self._drawtimer(y,diff)
            wasp.watch.drawable.blit(timericon,  0, y-4, fg=0x2DEF)
            y+=32
        if((y<170)and(self._longvars[_ALARM] >0)):
          wasp.watch.drawable.string("{:02d}:{:02d}".format(
            int((self._longvars[_ALARM]/60/60)%24),
            int((self._longvars[_ALARM]/60)%60),
          ), 24, y, width=191)
          wasp.watch.drawable.blit(alarmicon,  0, y-4, fg=0xB8C4)
          y+=32

        #seconds & date-string a bit darker
        wasp.watch.drawable.set_color(wasp.watch.drawable.darken(self._wordvars[_CLOCKCOL],8))
        wasp.watch.drawable.string("{:02d}".format(self._now[5]), 200, 94, width=40)
        if(self._lastnow[5] != self._now[5]):
          wasp.watch.drawable.string(self._day_string(self._now), 0, 38, width=240)

        #Mood display?
        if((y==130) and (self._wordvars[_SHOWMOOD]==1) and (hasattr(wasp,'mood_draw'))):
            y+=64
            self._shownmood = wasp.mood_draw(88,130,None,None,self._shownmood)
        if(y==130):
          self._shownmood = [-1,-1]
        #draw.fill(0,0,y,239,50-(y-130))


        self._updatestepsdisplay()
        self._updateheartdisplay()

    #Draw a number as seconds/mins etc
    def _drawtimer(self,y,val):
        secs = int(val%60)
        val=int(val/60)
        mins = int(val%60)
        val=int(val/60)
        hours = int(val%60)
        val=int(val/24)
        if(val>0):
          wasp.watch.drawable.string("{:02d} {:02d}:{:02d}:{:02d}".format(
            val,hours,mins,secs
          ), 24, y, width=191)
        else:
          wasp.watch.drawable.string("{:02d}:{:02d}:{:02d}".format(
            hours,mins,secs
          ), 24, y, width=191)
        
    #Draw the heart-counter
    def _updateheartdisplay(self):
        s = ss = ""
        col = 0xffff
        remain=0
        hhash = 0
        if(self._wordvars[_HEARTONOFF]==0):
          s = "off"
          col = 0x1af5
          hhash+= 1
        else:
          if(self._hrdata==None):
            if((self._wordvars[_LASTHEARTRATE]!=None)and(int(self._wordvars[_LASTHEARTRATE])>=0)):
              hhash+= 2
              s = "{:02d}".format(int(self._wordvars[_LASTHEARTRATE]))
              col = 0xee85
              if(self._wordvars[_HEARTINTERVAL]>0):
                col = 0xf800
              diff = self._longvars[_TIMESTAMP] - self._longvars[_LASTHEARTRATETIME]
              hhash+=diff*60*60
              if(diff>30):
                if(diff>60):
                  if(diff>60*60):
                    if(diff>24*60*60):
                      ss = "-{:2d}d".format(int(diff/(24*60*60)))
                    else:
                      ss = "-{:2d}h".format(int(diff/(60*60)))
                  else:
                    ss = "-{:2d}m".format(int(diff/60))
                else:
                  ss = "-{:2d}s".format(int(diff))
            else:
              s = "."
          else:
            remain = int(10 - (len(self._hrdata.data)/24))
            hhash+= 4 +  remain*60
            s = "-{:02d}".format(remain)
            col = 0xbaf8
        hhash = hhash%63356
        col2 = wasp.watch.drawable.darken(col, 16)
        if(self._wordvars[_HEARTHASH]!=hhash):
          self._wordvars[_HEARTHASH] = hhash
          wasp.watch.drawable.set_color(col)
          wasp.watch.drawable.blit(heartpulse, 216, 210,fg=col)
          wasp.watch.drawable.string( s, 161, 210, width=55, right=True)
          wasp.watch.drawable.set_color(col2)
          wasp.watch.drawable.string(ss, 184, 187, width=55,  right=True)

          wasp.watch.drawable.fill(0   ,209,        234,32,3)
          if(self._wordvars[_HEARTINTERVAL] >=60):
            wasp.watch.drawable.fill(col ,233,        234,6,3)
          if(self._wordvars[_HEARTINTERVAL] >=5*60):
            wasp.watch.drawable.fill(col ,225,        234,6,3)
          if(self._wordvars[_HEARTINTERVAL] >=15*60):
            wasp.watch.drawable.fill(col ,217,        234,6,3)
          if(self._wordvars[_HEARTINTERVAL] >=60*60):
            wasp.watch.drawable.fill(col ,209,        234,6,3)

        bar = 0
        if(remain==0):
          #Countdown to next measurement
          remain = self._longvars[_NEXTHEARTMEASUREMENTTIME] - self._longvars[_TIMESTAMP]
          if(self._wordvars[_HEARTINTERVAL]!=0):
            bar = int((float(remain) / self._wordvars[_HEARTINTERVAL]) * 100)
        else:
          #Countdown to end of this measurement
          bar = int(float(remain) / 10 * 100 )

        if(bar==0): col2=0;
        wasp.watch.drawable.fill(col ,239-bar,238,    bar,2)
        wasp.watch.drawable.fill(col2,139,        238,100-bar,2)


    #Draw the step-counter
    def _updatestepsdisplay(self):
        if(self._longvars[_LASTSTEPS]!=self._longvars[_STEPCOUNT]):
          col = 0x1DE3
          col2 = wasp.watch.drawable.darken(col, 16)
          self._longvars[_LASTSTEPS] = self._longvars[_STEPCOUNT]
          wasp.watch.drawable.set_color(col)
          wasp.watch.drawable.blit(footsteps, 0, 208,fg=col)
          wasp.watch.drawable.string("{}".format(self._longvars[_STEPCOUNT] + self._longvars[_MISSEDSTEPS]), 24, 210)
          if(self._longvars[_STEPSSINCE]>0):
            wasp.watch.drawable.set_color(wasp.watch.drawable.darken(col,16))
            wasp.watch.drawable.string("{}".format(self._longvars[_STEPCOUNT] - self._longvars[_STEPSSINCE]), 0, 184)

          bar = int((float(self._longvars[_STEPCOUNT]) / 10000) * 100 )
          if(bar>100):
            bar=100
            col = wasp.watch.drawable.lighten(col, 16)
          wasp.watch.drawable.fill(col ,  0,   238,    bar,2)
          wasp.watch.drawable.fill(col2,bar+1, 238, 99-bar,2)


    #A string representation of the day
    def _day_string(self, now):
        month = now[1] - 1
        month = _TLASTRING[month*3:(month+1)*3]
        wday = now[6]
        wday = _TLASTRING[_DAYSTART+wday*3:_DAYSTART+(+wday+1)*3]
        return '{} {:d} {} {:04d}'.format(wday, now[2], month, now[0])



    ###
    # File stff
    ###
 
    # Starup load functions, load prefs and
    # try for step-log catchup.
    def _load(self):
        gc.collect()
        self._loadpreferences()
        gc.collect()
        self._catchupsteps()
        gc.collect()
        self._draw()
        gc.collect()


    # Catchup-steps.
    # We load today's step-log and if there's been steps
    # since log-rotate-time we fake-add them to the 
    # counter. Then we write any missing values as zeros
    # to pad it up to the correct length.
    # Obviously none of this will work if you change
    # the frequency in the middle of the day.
    def _catchupsteps(self):
      #Load and correct step-logs only if step-logger turned on. Otherwise at what freq man?
      if(self._wordvars[_STEPLOGFREQ]>0):
        tsptr = []
        tsptr.extend(self._now)
        tsptr[3]= tsptr[4]= tsptr[5]=0
        tsptr = int(time.mktime(tuple(tsptr)))
        sec=0
        self._longvars[_MISSEDSTEPS]=0
        try:
            try:
                with open(self._steplogname(), 'r') as file:
                    field = 'd'
                    while True:
                        gc.collect()
                        char = file.read(1)
                        if char == '' or char == ',':  # End of file or comma
                            if(field[0]=='d'):
                                pass    #skip date-field
                            else:
                                if((sec/60/60)>=self._wordvars[_LOGROTTIME]):
                                    self._longvars[_MISSEDSTEPS]+=int(field)
                            tsptr +=self._wordvars[_STEPLOGFREQ]*60
                            sec+=self._wordvars[_STEPLOGFREQ]*60
                            field = '0'
                            if char == '': break  #eof
                        else:
                            field += char
            except Exception as e:
                print("StepLoadExcep:"+str(e))
                pass
            if(self._longvars[_MISSEDSTEPS]<=self._longvars[_STEPCOUNT]):
                #Obviously it's already counted
                self._longvars[_MISSEDSTEPS]=0
            diff=int((self._longvars[_TIMESTAMP] - tsptr)/(self._wordvars[_STEPLOGFREQ]*60))
            #print("Missed {} steps, filling in {} blocks".format(self._longvars[_MISSEDSTEPS],diff))
            wasp.system.notify(wasp.watch.rtc.get_uptime_ms(),{"title":"Reboot","body":"Restarted.\n\nMissed {} steps\n\nFilled in empty log for {} missing blocks".format(self._longvars[_MISSEDSTEPS],diff)})
            if(diff>=0):
                 self._writesteplog("0,",diff)
        except Exception as e:
            print("StepLoadExcep2:"+str(e))
    
    

    #
    # All prefs are word vars and they are the wordvars at the start of the array
    # We just save a single line CSV and read them in till _MAXSAVED or EOF
    def _loadpreferences(self):
      try:
        with open("/flash/preferences.csv", 'r') as file:
            i = 0
            field = ''
            while(i < _MAXSAVED):
                char = file.read(1)
                if char == '' or char == ',':  # End of file or comma
                    self._wordvars[i]=int(field)
                    i+=1
                    field = ''
                    if char == '': break  #eof
                else:
                    field += char
        self._updatefont(self._wordvars[_FONTNUM])
      except Exception as e:
        print("PrefLoadExcep:"+str(e))
        pass


    def _mkdirs(self):
        gc.collect()
        s = '/flash/logs/{:04d}'.format(self._now[0])
        import os
        try:
          os.mkdir(s)
        except Exception as e:
          pass
        try:
          os.mkdir(s+'/heart')
        except Exception as e:
          pass
        try:
          os.mkdir(s+'/steps')
        except Exception as e:
          pass
        del(os)
        gc.collect()

    def _savepreferences(self):
        #Make sure log dirs exist.
        self._mkdirs()
        with open("/flash/preferences.csv", 'w') as dest:
          for i in range(0,_MAXSAVED):
            dest.write(str(self._wordvars[i]))
            dest.write(",")
            i+=1
        gc.collect()
        

    ##
    # UI stuff
    #
    def _cornerbuttons(self,labels,funs,bgcol=0x88e,fgcol=0xffff,wait=5):
        if(bgcol==None): bgcol = 0x88e
        if(fgcol==None): fgcol = 0xffff
        self._buttonfuns = funs
        draw = wasp.watch.drawable
        draw.fill(bgcol, 0, 32, 239, 176)
        draw.set_color(fgcol,bgcol)
        draw.line(1,  120, 237, 120, 4, 0x0000) 
        draw.line(120,  4, 120, 235, 4, 0x0000)
        if(len(labels)>0):
          draw.string(labels[0],0,   65, width=116)
        if(len(labels)>1):
          draw.string(labels[1],123, 65, width=116)
        if(len(labels)>2):
          draw.string(labels[2],0,   155, width=116)
        if(len(labels)>3):
          draw.string(labels[3],123, 155, width=116)
        self._switchscreen(1,wait)
  

    #time-setting buttons, for alarms and countdowns etc.
    def _timesetbuttons(self,label,bgcol=0x88e,fgcol=0xffff,newscreen=2):
        wasp.watch.drawable.fill(bgcol, 0, 32, 239, 176)
        wasp.watch.drawable.set_color(fgcol,bgcol)
        wasp.watch.drawable.line(1,  120, 237, 120, 4, 0x0000) 
        wasp.watch.drawable.line( 60, 122,  60, 238, 4, 0x0000) 
        wasp.watch.drawable.line(120, 122, 120, 238, 4, 0x0000) 
        wasp.watch.drawable.line(180, 122, 180, 238, 4, 0x0000) 
        wasp.watch.drawable.string(label,0, 55, width=239)
        wasp.watch.drawable.string("<<",4, 150, width=54)
        wasp.watch.drawable.string("<",64, 150, width=54)
        wasp.watch.drawable.string(">",124, 150, width=54)
        wasp.watch.drawable.string(">>",184, 150, width=54)
        self._switchscreen(newscreen,60)

    def _drawtimesetvalues(self):
        wasp.watch.drawable.string("{:02d}:{:02d}".format(
            self._wordvars[_SETTIMEH],
            self._wordvars[_SETTIME ]),0, 85, width=239)

    def _drawdatesetvalues(self):
        wasp.watch.drawable.string(self._day_string(self._dateset),0, 85, width=239)
        
    def _timesettouches(self,x,y):
      wasp.watch.vibrator.pulse(duty=50, ms=30)
      if(y<120):
        self._timesetfun()
      else:
        if(x<60):
          if(self._wordvars[_SETTIMEH]==0):
            self._wordvars[_SETTIMEH]=23
          else:
            self._wordvars[_SETTIMEH]-=1
        elif(x<120):
          if(self._wordvars[_SETTIME]==0):
            self._wordvars[_SETTIME]=59
          else:
            self._wordvars[_SETTIME]-=1
        elif(x<180):
          self._wordvars[_SETTIME]+=1
          if(self._wordvars[_SETTIME]>59):
            self._wordvars[_SETTIME]=0
        else:
          self._wordvars[_SETTIMEH]+=1
          if(self._wordvars[_SETTIMEH]>23):
            self._wordvars[_SETTIMEH]=0
        self._drawtimesetvalues()


    def _datesettouches(self,x,y):
      wasp.watch.vibrator.pulse(duty=50, ms=30)
      if(y<120):
        self._timesetfun()
      else:
        ts = int(time.mktime((self._dateset[0], self._dateset[1], self._dateset[2], self._dateset[3], self._dateset[4], self._dateset[5], 0, 0, 0)))
        if(x<60):
           ts-=28*24*60*60
        elif(x<120):
           ts-=24*60*60
        elif(x<180):
           ts+=24*60*60
        else:
           ts+=28*24*60*60
        self._dateset = time.localtime(ts)
        self._drawdatesetvalues()

 
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
      self._switchscreen(1,0)


    def _taptopleft(self):
       self._cornerbuttons(("Colour","Stats",
                            "Font","File"),
                         (self._butpickcol, self._butstats,
                          self._butfont, self._butfile))

    def _taptopright(self):
        stsp = "Start"
        if(self._longvars[_STOPWATCHTIME]>0):
            if(self._wordvars[_STOPWATCHRUN]==1):
              stsp = "Stop"
            else:
              stsp = "Reset"
        cdown = "Cdown"
        if(self._longvars[_CDOWN] > 0):
          cdown = "Cancel"

        self._cornerbuttons(("Shake",stsp,
                            "Alarm",cdown),
                         (self._butshake, self._butstopwatch,
                          self._butalarm, self._butcdown))

    def _tapbotleft(self):
        s = "Show"
        if(self._wordvars[_SHOWMOOD]==1):
            s="Hide"
        self._cornerbuttons(("Steplog",s,
                             "Lap","Reset"),
                          (self._butsteplogfreq,self._butmoodshow,
                           self._butlap, self._butreset))
          
    def _tapbotright(self):
        if(self._wordvars[_HEARTONOFF]==0):
          self._cornerbuttons(("Once","1m","5m","15m"),
                            (self._butheartnever,self._butheart1m,
                             self._butheart5m   ,self._butheart15m))
        else:
            self._wordvars[_HEARTONOFF]=0
            self._wordvars[_HEARTINTERVAL]=0
            self._longvars[_NEXTHEARTMEASUREMENTTIME]=0 
 
    ##Default/empty button does nothing 
    def _but(self):
        self._switchscreen(0)

    # Control the shake-to-wake setting
    def _butshake(self):
       self._cornerbuttons(("Off","On", "Vibrate","Strong"),
                         (self._butshake0,self._butshake1,
                          self._butshake2,self._butshake3))
    def _butshake0(self):
        self._wordvars[_SHAKEWAKE] = 0
    def _butshake1(self):
        self._wordvars[_SHAKEWAKE] = 1
    def _butshake2(self):
        self._wordvars[_SHAKEWAKE] = 2
    def _butshake3(self):
        self._wordvars[_SHAKEWAKE] = 3

    #Heart-buttons
    def _butheartnever(self):
        self._butheart(0)
    def _butheart1m(self):
        self._butheart(60)
    def _butheart5m(self):
        self._butheart(5*60)
    def _butheart15m(self):
        self._butheart(15*60)
    def _butheart(self,x):
        self._wordvars[_HEARTONOFF]=1
        self._wordvars[_HEARTINTERVAL] = x
        self._startnewheartmeasurement()
        if(x>0):
          self._longvars[_NEXTHEARTMEASUREMENTTIME] = self._longvars[_TIMESTAMP]+x
        else:
          self._longvars[_NEXTHEARTMEASUREMENTTIME] = 0
 
 
    # Lap counter
    def _butlap(self):
        if(self._longvars[_STEPSSINCE]==0):
          self._longvars[_STEPSSINCE] = self._longvars[_STEPCOUNT]
        else:
          self._longvars[_STEPSSINCE] = 0
        #print("Steps since set to "+str(self._longvars[_STEPSSINCE]))


    def _butreset(self):
        self._longvars[_STEPSSINCE] = 0
        self._logrotate()


    #When to reset step-counter and rotate the logs in the apps that want it
    def _logrotate(self):
        wasp.watch.accel.steps = 0
        if(hasattr(wasp,'mood_logrotate')):
          wasp.mood_logrotate()

    # Countdown
    def _butcdown(self):
        if(self._longvars[_CDOWN] > 0):
            self._longvars[_CDOWN] = 0 
        else:
            now = self._now
            self._wordvars[_SETTIME]  = 10
            self._wordvars[_SETTIMEH] = 0
            self._timesetfun = self._setcdown
            self._timesetbuttons("cdown",0x7000,0xffff)
            self._drawtimesetvalues()

    def _setcdown(self):
        self._longvars[_CDOWN] = self._longvars[_TIMESTAMP] + self._wordvars[_SETTIMEH]*60*60 + self._wordvars[_SETTIME]*60
        self._switchscreen(0)

    def _endcdown(self):
        self._longvars[_CDOWN] = 0 
        self._flashbuzz = "cdown"

    # Alarm
    def _butalarm(self):
        now = self._now
        self._wordvars[_SETTIME]  = now[4]
        self._wordvars[_SETTIMEH] = now[3]
        self._timesetfun = self._setalarm
        self._timesetbuttons("alarm",0x7000,0xffff)
        self._drawtimesetvalues()

    def _setalarm(self):
        now = []
        now.extend(self._now)
        if(now[3] < self._wordvars[_SETTIMEH]):
          now[2]+=1
        now[3] = self._wordvars[_SETTIMEH]
        now[4] = self._wordvars[_SETTIME]
        now[5] = 0
        ts = int(time.mktime(tuple(now)))
        self._longvars[_ALARM] = ts 
        self._switchscreen(0)
        self._draw()


    def _soundalarm(self):
        self._longvars[_ALARM] = 0 
        self._flashbuzz = "alarm"

    # Stopwatch
    def _butstopwatch(self):
        if(self._longvars[_STOPWATCHTIME]==0):
            self._wordvars[_STOPWATCHRUN] =1
        elif(self._wordvars[_STOPWATCHRUN]==1):
            self._wordvars[_STOPWATCHRUN]=0
        else:
            self._longvars[_STOPWATCHTIME]=0
       
    ## Load the prefs/logs - probably ought to be automatic instead of a button when it works.
    def _butload(self):
        self._load()
        self._draw();

    ## Save the prefs/logs
    def _butsave(self):
        self._savepreferences()
        self._draw();

    def _butfile(self):
       self._cornerbuttons(("Save","Load", "Bright","SetTime"),
                         (self._butsave,self._butload,
                          self._butbright,self._butsetdate))

    
    ##Font stuff
    def _butfont(self):
        names = ["","","",""]
        i=0
        if(hasattr(wasp,"fonts")):
            for k in wasp.fonts.keys():
                names[i]=k
                i+=1
                if(i>=4):
                    break
        self._cornerbuttons((names[0],names[1],
                           names[2],names[3]),
                          (self._butfontseta,self._butfontsetb,
                           self._butfontsetc,self._butfontsetd))
        wasp.watch.drawable.string(str(self._wordvars[_FONTNUM]), 0, 211, width=239)
    

    def _butfontseta(self):
        if((not hasattr(wasp,"fonts")) or (len(list(wasp.fonts.keys()))<=0)):
            self._setfont(None)
        else:
            self._setfont(wasp.fonts[list(wasp.fonts.keys())[0]])
    def _butfontsetb(self):
        if((not hasattr(wasp,"fonts")) or (len(list(wasp.fonts.keys()))<=1)):
            self._setfont(None)
        else:
            self._setfont(wasp.fonts[list(wasp.fonts.keys())[1]])
    def _butfontsetc(self):
        if((not hasattr(wasp,"fonts")) or (len(list(wasp.fonts.keys()))<=2)):
            self._setfont(None)
        else:
            self._setfont(wasp.fonts[list(wasp.fonts.keys())[2]])
    def _butfontsetd(self):
        if((not hasattr(wasp,"fonts")) or (len(list(wasp.fonts.keys()))<=3)):
            self._setfont(None)
        else:
            self._setfont(wasp.fonts[list(wasp.fonts.keys())[3]])

    def _setfont(self,fontref):
        if(fontref!=None):
            self._fontref = fontref[1]
            self._wordvars[_FONTNUM] = fontref[0]
        else:
            self._fontref = None
            self._wordvars[_FONTNUM] = 0


    #Find the best font for an ID num, set it.
    def _updatefont(self,idnum):
        if(hasattr(wasp,"fonts")):
            for i in wasp.fonts.keys():
                if(wasp.fonts[i][0]==idnum):
                    self._setfont(wasp.fonts[i])
                    return
            if(len(list(wasp.fonts.keys()))>0):
               self._setfont(wasp.fonts[list(wasp.fonts.keys())[0]])
               return  
        self._setfont(None)

    ## Show/Hide mood
    def _butmoodshow(self):
        self._wordvars[_SHOWMOOD] = 1-self._wordvars[_SHOWMOOD]


    ## Setting the time/date
    def _butsetdate(self):
        self._dateset = self._now
        self._timesetbuttons("date",0x7000,0xffff,newscreen=3)
        self._drawdatesetvalues()
        self._timesetfun = self._setdatefinished


    def _setdatefinished(self):
        self._wordvars[_SETTIME]  = self._dateset[4]
        self._wordvars[_SETTIMEH] = self._dateset[3]
        self._timesetfun = self._settimefinished
        self._timesetbuttons("now",0x7000,0xffff)
        self._drawtimesetvalues()

    def _settimefinished(self):
        self._dateset = list(self._dateset)
        self._dateset[4] = self._wordvars[_SETTIME]
        self._dateset[3] = self._wordvars[_SETTIMEH]
        wasp.watch.rtc.set_localtime(self._dateset)
        del(self._dateset)
        self._reset()
        self._switchscreen(0)
    

    ##Stats Page
    def _butstats(self):
        mem = disk = bat = dayend = "?"
        try:
            mem = str(int(gc.mem_free()/1024))+"k"
        except:
            mem = "x"
            pass

        try:
            bat = "B:"+str(wasp.watch.battery.level())+"%"
        except:
            bat = "x"
            pass

        try:
            import os
            fs = os.statvfs("/flash")
            free = fs[0] * fs[4]
            total = fs[0] * fs[4]
            disk = "D:"+str(100-int(100.0*(free/total)))+"%"
            del os
            gc.collect()
        except:
            disk = "x"
            pass
        self._cornerbuttons((mem,disk,bat,str(self._wordvars[_LOGROTTIME])+"am"),
                          (self._but, self._but,
                           self._but, self._butsetlogrottime))


    # Change screen brightness
    def _butbright(self):
       self._cornerbuttons(("Low","Med",
                          "High",""),
                         (self._butbrightset1,self._butbrightset2,
                          self._butbrightset3,self._but))
    def _butbrightset1(self):
         wasp.system.brightness = 1
    def _butbrightset2(self):
         wasp.system.brightness = 2
    def _butbrightset3(self):
         wasp.system.brightness = 3



    # Change step-log frequency
    def _butsteplogfreq(self):
       self._cornerbuttons(("5m","15m",
                          "1h","Off"),
                         (self._butsteplogfreqset5,self._butsteplogfreqset15,
                          self._butsteplogfreqset60,self._butsteplogfreqset0))
       wasp.watch.drawable.string(str(self._wordvars[_STEPLOGFREQ]), 0, 211, width=239)
    def _butsteplogfreqset5(self):
         self._wordvars[_STEPLOGFREQ] = 5
    def _butsteplogfreqset15(self):
         self._wordvars[_STEPLOGFREQ] = 15
    def _butsteplogfreqset60(self):
         self._wordvars[_STEPLOGFREQ] = 60
    def _butsteplogfreqset0(self):
         self._wordvars[_STEPLOGFREQ] = 0


    # Change log-rot time
    def _butsetlogrottime(self): 
       self._cornerbuttons(("Midnight","4am",
                          "2am","6am"),
                         (self._butlogrot0, self._butlogrot4,
                          self._butlogrot2,  self._butlogrot6))
       wasp.watch.drawable.string("{}".format(self._wordvars[_LOGROTTIME]), 0, 211, width=239)
    def _butlogrot0(self):
        self._wordvars[_LOGROTTIME] = 0
    def _butlogrot2(self):
        self._wordvars[_LOGROTTIME] = 2
    def _butlogrot4(self):
        self._wordvars[_LOGROTTIME] = 4
    def _butlogrot6(self):
        self._wordvars[_LOGROTTIME] = 6


    ##Picking color 
    def _butpickcol(self):
        self._cornerbuttons(("Red","Green","Blue","More"),
                          (self._butcolred, self._butcolgreen,
                           self._butcolblue,self._butcolmore))

    def _butcolmore(self):
        self._cornerbuttons(("Yellow","Cyan","Purple","White"),
                          (self._butcolyellow,self._butcolcyan,
                           self._butcolpurple,self._butcolwhite))
     
    def _butcolwhite(self):
        self._wordvars[_CLOCKCOL] = 0xffff
        self._switchscreen(0)

    def _butcolred(self):
        self._wordvars[_CLOCKCOL] = 0xc000
        self._switchscreen(0)

    def _butcolblue(self):
        self._wordvars[_CLOCKCOL] = 0x0018
        self._switchscreen(0)

    def _butcolgreen(self):
        self._wordvars[_CLOCKCOL] = 0x0620
        self._switchscreen(0)

    def _butcolyellow(self):
        self._wordvars[_CLOCKCOL] = 0xc620
        self._switchscreen(0)

    def _butcolcyan(self):
        self._wordvars[_CLOCKCOL] = 0x0638
        self._switchscreen(0)

    def _butcolpurple(self):
        self._wordvars[_CLOCKCOL] = 0xc018
        self._switchscreen(0)



##
# Icons Etc.

#Icons all by me, pre, CC0
# 1-bit RLE, 24x24, generated from res/heartpulse.png, 45 bytes
heartpulse = (
    24, 24,
    b'\x1c\x06\x04\x06\x06\t\x02\t\x04\t\x02\t\x03\x16\x02\x16'
    b'\x02\x16\x02\x16\x02\x16\x03\x14\x04\x14\x05\x12\x07\x10\t\x0e'
    b'\x0b\x0c\r\n\x0f\x08\x11\x06\x13\x04\x15\x02k'
)

# 1-bit RLE, 24x24, generated from res/footsteps.png, 69 bytes
footsteps = (
    24, 24,
    b'\r\x03\x13\x06\x11\x08\x0f\n\r\x0b\x0c\x0b\r\n\x0e\t'
    b'\r\x02\x01\x07\r\x04\x01\x05\r\x06\x01\x02\x04\x03\x08\x07'
    b'\x04\x06\x07\x06\x04\x08\x07\x04\x04\n\r\x0b\x0c\x0b\r\n'
    b'\x0e\t\r\x02\x01\x07\r\x04\x01\x05\r\x06\x01\x02\x0f\x07'
    b'\x11\x06\x13\x04\r'
)
# 1-bit RLE, 24x24, generated from res/alarmicon.png, 97 bytes
alarmicon = (
    24, 24,
    b'L\x03\x04\x01\x04\x03\x08\x01\x07\x01\x07\x01\x07\x01\x04\x07'
    b'\x04\x01\x07\x01\x03\x03\x03\x03\x03\x01\n\x02\x07\x02\x0b\x02'
    b'\x05\x01\x05\x02\t\x02\x05\x01\x05\x02\t\x01\x06\x01\x06\x01'
    b'\t\x01\x06\x01\x06\x01\x08\x01\x07\x01\x07\x01\x07\x01\x07\x07'
    b'\x01\x01\x07\x01\x0f\x01\x08\x01\r\x01\t\x01\r\x01\t\x02'
    b'\x0b\x02\n\x01\x0b\x01\x0c\x02\x07\x02\x0e\x03\x03\x03\x12\x03'
    b';'
)
# 1-bit RLE, 24x24, generated from res/stopwatchicon.png, 75 bytes
stopwatchicon = (
    24, 24,
    b'P\x07\x14\x01\x17\x01\x16\x03\x12\t\x0e\x03\x05\x03\x0c\x02'
    b'\t\x02\n\x02\x0b\x02\t\x02\x08\x01\x02\x02\t\x01\x08\x01'
    b'\x04\x01\x08\x02\x07\x01\x05\x02\x07\x02\x06\x01\x06\x02\x07\x02'
    b'\r\x02\x08\x01\r\x01\t\x02\x0b\x02\t\x02\x0b\x02\n\x02'
    b'\t\x02\x0c\x03\x05\x03\x0e\t\x12\x03#'
)
# 1-bit RLE, 24x24, generated from res/timericon.png, 159 bytes
timericon = (
    24, 24,
    b'\x06\r\x0b\x01\x04\x03\x04\x01\x0b\x01\x02\x02\x03\x02\x02\x01'
    b'\x0b\x01\x01\x01\x07\x01\x01\x01\x0b\x01\x01\x01\x07\x01\x01\x01'
    b'\x0b\x02\t\x02\x0b\x02\t\x02\x0b\x01\x01\t\x01\x01\x0b\x01'
    b'\x01\t\x01\x01\x0b\x01\x02\x07\x02\x01\x0b\x01\x04\x01\x01\x01'
    b'\x04\x01\x0b\x01\x04\x01\x01\x01\x04\x01\x0b\x01\x04\x01\x01\x01'
    b'\x04\x01\x0b\x01\x04\x01\x01\x01\x04\x01\x0b\x01\x02\x02\x01\x01'
    b'\x01\x02\x02\x01\x0b\x01\x01\x01\x03\x01\x03\x01\x01\x01\x0b\x01'
    b'\x01\x01\x03\x01\x03\x01\x01\x01\x0b\x02\x04\x01\x04\x02\x0b\x02'
    b'\x04\x01\x04\x02\x0b\x01\x01\t\x01\x01\x0b\x01\x01\t\x01\x01'
    b'\x0b\x01\x02\x07\x02\x01\x0b\x01\x04\x03\x04\x01\x0b\r\x05'
)

