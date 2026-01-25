# Copyright (C) 2025 Hongyi Chen (BeanPieChen)
# Licensed under the MIT License

import dev
from UI import UI,UIList,UIBtn,UISlider,UICombo
from Text import TBox
import CS
import t5200c_8x16 as f
import Terminal
import Editor
import WLANM
from os import dupterm
from esp32 import wake_on_ext0
from machine import Pin,lightsleep,deepsleep,Timer,RTC

_show=True
_p0=None
_main=None
_ui=None
_wlanm=None
_timer=None
_rtc=None
_css=[CS.WHITE,CS.GREEN,CS.ORANGE,CS.CYAN,CS.PURPLE,CS.YELLOW,CS.RED]
_csn=["White","Green","Orange","Cyan","Purple","Yellow","Red"]
_cs=1

def _OnWake(pin):
    global _ui
    _p0.irq(None)
    dev.add_kbl(_ui)
    _ui.Draw()

def _lsleep():
    global _ui
    global _p0
    dev.remove_kbl(_ui)
    _p0.irq(_OnWake)
    wake_on_ext0(0)
    lightsleep()

def _OnMenuBtn(btn):
    global _ui
    global _main
    global _wlanm
    global _css
    global _cs
    if btn=="back":
        if _main.mode==1:
            _main._SetMode(0)
        else:
            _main._SetMode(1)
        _ui.Draw()
    elif btn=="edit":
        _main._SetMode(0)
        _OpenEditor()
    elif btn=="wlan":
        _main._SetMode(0)
        _wlanm=WLANM.WLANM(0,0,240,135,_css[_cs],f,_OnWLANMExit)
        _wlanm.on_repeat=_OnWLANMR
        _wlanm._SetMode(0)
        _ui.SetChild(_wlanm)
    elif btn=="sleep":
        _main._SetMode(0)
        _lsleep()
    elif btn=="deep_sleep":
        wake_on_ext0(0)
        deepsleep()
    elif btn=="stop":
        dupterm(None)
    elif btn=="start":
        dupterm(_main.term)
    elif btn=="about":
        _main._SetMode(2)
        _ui.Draw()

def _OnT(t):
    global _main
    global _ui
    _main._UpdateTime()
    _ui.Draw()

def _OnBL(arg,v):
    dev._pwm.duty(dev._bld[v])
    dev._bl=v

def _OnCS(arg,v):
    global _cs
    global _css
    global _main
    _cs=v
    _main.SetCS(_css[_cs])

class MainUI:
    def __init__(self):
        global _css
        global _cs
        self.p=None
        self.mode=0
        self.term=Terminal.Terminal(0,0,240,135,_css[_cs],f,True)
        self.term.p=self
        self.status=None
        self.menu=None
        self.time=None
        self.uv=None
        self.about=None

    def _UpdateTime(self):
        global _rtc
        if not (self.time and self.uv):
            return
        dt=_rtc.datetime()
        self.time.SetText("{:0>2d}:{:0>2d}".format(dt[4],dt[5]))
        self.uv.SetText("{:.2f}V".format(dev.batt_uv()))

    def _SetMode(self,mode):
        global _timer
        global _css
        global _csn
        global _cs
        if mode==self.mode:
            return
        if self.mode==1:
            _timer.deinit()
            self.time=None
            self.uv=None
            self.status=None
            self.menu=None
        elif self.mode==2:
            self.about=None
        self.mode=mode
        if mode==1:
            status=UIList(0,0,240,135,_css[_cs],False)
            self.time=TBox(0,0,20,50,_css[_cs],f,False,"12:00")
            self.uv=TBox(0,0,20,50,_css[_cs],f,False,"2.00V",2)
            self.time.SetEnable(False)
            self.uv.SetEnable(False)
            self._UpdateTime()
            status.SetChildren([
                self.time,self.uv
            ])
            s_min_h=status.MinH()+2
            status.SetBox(0,0,240,s_min_h)
            status.SetEnable(False)
            menu=UIList(0,s_min_h,240,135-s_min_h,_css[_cs])
            menu.SetChildren([
                UIBtn(0,0,200,100,2,_css[_cs],f,"Back",_OnMenuBtn,"back"),
                UIBtn(0,0,200,100,2,_css[_cs],f,"Text Editor",_OnMenuBtn,"edit"),
                UIBtn(0,0,200,100,2,_css[_cs],f,"WLAN Configure",_OnMenuBtn,"wlan"),
                UIBtn(0,0,200,100,2,_css[_cs],f,"Sleep",_OnMenuBtn,"sleep"),
                UIBtn(0,0,200,100,2,_css[_cs],f,"Deep Sleep",_OnMenuBtn,"deep_sleep"),
                UISlider(0,0,200,100,2,_css[_cs],f,"Brightness",6,dev._bl,_OnBL,"bl"),
                UICombo(0,0,200,100,2,_css[_cs],f,"UI Color",_csn,_cs,_OnCS,"cs"),
                UIBtn(0,0,200,100,2,_css[_cs],f,"dupterm() Stop",_OnMenuBtn,"stop"),
                UIBtn(0,0,200,100,2,_css[_cs],f,"dupterm() Start",_OnMenuBtn,"start"),
                UIBtn(0,0,200,100,2,_css[_cs],f,"About",_OnMenuBtn,"about")
            ])
            status.p=self
            menu.p=self
            self.status=status
            self.menu=menu
            _timer.init(mode=Timer.PERIODIC,period=1000,callback=_OnT)
        elif mode==2:
            about=UIList(0,0,240,135,_css[_cs])
            about.SetChildren([
                TBox(0,0,200,100,_css[_cs],f,False,"MicroPython Shell\nv1.2\nBy BeanPieChen"),
                UIBtn(0,0,200,100,2,_css[_cs],f,"Back",_OnMenuBtn,"back")
            ])
            about.children[0].SetEnable(False)
            about.SetSelected(1)
            about.p=self
            self.about=about

    def OnCChange(self):
        if self.p:
            self.p.OnCChange()

    def SetBox(self,x,y,w,h):
        self.term.SetBox(x,y,w,h)
        if self.menu:
            self.menu.SetBox(x,y,w,h)
        if self.about:
            self.about.SetBox(x,y,w,h)
    
    def SetCS(self,cs):
        if self.term:
            self.term.SetCS(cs)
        if self.menu:
            self.menu.SetCS(cs)
        if self.status:
            self.status.SetCS(cs)
        if self.about:
            self.about.SetCS(cs)

    def Draw(self,fb,win):
        if self.mode==0:
            self.term.Draw(fb,win)
        elif self.mode==1:
            self.status.Draw(fb,win)
            self.menu.Draw(fb,win)
        else:
            self.about.Draw(fb,win)
    
    def OnKBE(self,e,d0,d1):
        if self.mode==0:
            if e==dev.KBE_DOWN and d1==dev.KV_ESC:
                self._SetMode(1)
                return True
            return self.term.OnKBE(e,d0,d1)
        elif self.mode==1:
            return self.menu.OnKBE(e,d0,d1)
        else:
            return self.about.OnKBE(e,d0,d1)

def _OnEditorExit():
    global _ui
    global _main
    global _edit
    _ui.SetChild(_main)
    _edit=None

def _OpenEditor(path=None):
    global _ui
    global _edit
    global _css
    global _cs
    _edit=Editor.Editor(0,0,240,135,_css[_cs],f,_OnEditorExit)
    if path:
        try:
            _edit.Open(path)
        except:
            _edit=None
            raise
    _ui.SetChild(_edit)

def _OnWLANMExit():
    global _ui
    global _main
    global _wlanm
    _ui.SetChild(_main)
    _wlanm=None

def _OnWLANMT(t):
    global _wlanm
    _wlanm._UpdateState()
    if _wlanm.p:
        _wlanm.p.OnCChange()

def _OnWLANMR(en):
    global _timer
    if en:
        _timer.init(mode=Timer.PERIODIC,period=1000,callback=_OnWLANMT)
    else:
        _timer.deinit()

def _Init():
    global _p0
    global _main
    global _ui
    global _edit
    global _wlanm
    global _timer
    global _rtc
    _p0=Pin(0,Pin.IN)
    _main=MainUI()
    _ui=UI()
    _ui.SetChild(_main)
    dev.add_kbl(_ui)
    dupterm(_main.term)
    _timer=Timer(1)
    _rtc=RTC()

def datetime(*args):
    return _rtc.datetime(*args)

def hide():
    global _show
    global _ui
    if not _show:
        return
    _ui.SetChild(None)
    dev.remove_kbl(_ui)
    _show=False

def show():
    global _show
    global _ui
    global _main
    if _show:
        return
    _ui.SetChild(_main)
    dev.add_kbl(_ui)
    _show=True