# Copyright (C) 2025 Hongyi Chen (BeanPieChen)
# Licensed under the MIT License

import network
from Text import TBox,TLEdit
from UI import UIList,UIBtn
from binascii import hexlify

WLAN_SEC=["Open","WEP","WPA_PSK","WPA2-PSK","WPA/WPA2-PSK"]

def OnWLANMgrBtn(args):
    args[0].OnBtn(args[1])

def MacAddr(b):
    return "{:x}:{:x}:{:x}:{:x}:{:x}:{:x}".format(b[0],b[1],b[2],b[3],b[4],b[5])

class WLANM:
    def __init__(self,x,y,w,h,cs,f,on_exit):
        self.on_exit=on_exit
        self.on_repeat=None
        self.f=f
        self.cs=cs
        self.w=w
        self.wlan=network.WLAN()
        self.mode=0
        self.ui_scan=TBox(x,y,w,h,cs,f,True,"Scanning...")
        self.ui_scan.SetEnable(False)
        self.t_status=TBox(x,y,w,h,cs,f,True,"Not connected")
        self.t_status.SetEnable(False)
        self.btn_back=UIBtn(0,0,w,50,2,cs,f,"Back",OnWLANMgrBtn,(self,"back"))
        self.btn_switch=UIBtn(0,0,w,50,2,cs,f,"Turn on",OnWLANMgrBtn,(self,"switch"))
        self.btn_scan=UIBtn(0,0,w,50,2,cs,f,"Scan",OnWLANMgrBtn,(self,"scan"))
        self.btn_discon=UIBtn(0,0,w,50,2,cs,f,"Disconnect",OnWLANMgrBtn,(self,"discon"))
        self.ui_main=UIList(x,y,w,h,cs)
        self.t_con=TBox(x,y,w,h,cs,f,False)
        self.t_con.SetEnable(False)
        self.tle_pwd=TLEdit(x,y,w,h,2,cs,f)
        self.btn_con=UIBtn(0,0,w,50,2,cs,f,"Connect",OnWLANMgrBtn,(self,"con"))
        self.ui_con=UIList(x,y,w,h,cs)
        self.ret=[]
        self.pending=-1
        self.p=None
        self._SetMode(0)
    
    def _UpdateState(self):
        if self.wlan.isconnected():
            self.btn_discon.SetEnable(True)
            con_name=self.wlan.config("ssid")
            con_addr=self.wlan.ipconfig("addr4")
            self.t_status.SetText("Connected\n"+con_name+"\n"+con_addr[0]+"/"+con_addr[1])
        else:
            self.btn_discon.SetEnable(False)
            if self.wlan.status()==network.STAT_CONNECTING:
                self.t_status.SetText("Connecting...\n\n")
            else:
                self.t_status.SetText("Not connected\n\n")
        self.ui_main.SetChildren(self.ui_main.children)
    
    def _UpdateMainUI(self):
        if self.wlan.active():
            self.btn_switch.SetText("Turn off")
            self.btn_scan.SetEnable(True)
        else:
            self.btn_switch.SetText("Turn on")
            self.btn_scan.SetEnable(False)
        c=[self.btn_back,self.t_status,self.btn_switch,self.btn_scan,self.btn_discon]
        for i in range(len(self.ret)):
            show=self.ret[i][0].decode()
            if not show:
                show=MacAddr(self.ret[i][1])
                show="[{}]".format(show)
            c.append(UIBtn(0,0,self.w,50,2,self.cs,self.f,show,OnWLANMgrBtn,(self,i)))
        self.ui_main.children=c
        self._UpdateState()
    
    def _SetMode(self,mode):
        if self.mode==0:
            if self.on_repeat:
                self.on_repeat(False)
        elif self.mode==2:
            self.tle_pwd.Clear()
        self.mode=mode
        if mode==0:
            self._UpdateMainUI()
            if self.on_repeat and self.wlan.active():
                self.on_repeat(True)
        elif mode==1:
            pass
        elif mode==2:
            p=self.ret[self.pending]
            self.t_con.SetText(p[0].decode()+"\n"+MacAddr(p[1])+"\n"+WLAN_SEC[p[-2]])
            self.ui_con.SetChildren([self.t_con,self.tle_pwd,self.btn_con,self.btn_back])
            self.ui_con.SetSelected(1)
    
    def OnBtn(self,btn):
        if self.mode==0:
            if btn=="back":
                if self.on_repeat:
                    self.on_repeat(False)
                self.on_exit()
                return
            elif btn=="switch":
                if self.wlan.active():
                    self.wlan.active(False)
                    self.ret=[]
                else:
                    self.wlan.active(True)
                self._SetMode(0)
            elif btn=="discon":
                self.wlan.disconnect()
                self._SetMode(0)
            elif btn=="scan":
                if self.wlan.active():
                    self._SetMode(1)
                    if self.p:
                        self.p.OnCChange()
                    self.ret=self.wlan.scan()
                    self._SetMode(0)
                else:
                    return
            elif type(btn)==int:
                self.pending=btn
                self._SetMode(2)
            else:
                return
        elif self.mode==1:
            return
        else:
            if btn=="con":
                try:
                    self.wlan.connect(self.ret[self.pending][0].decode(),self.tle_pwd.GetText(),bssid=self.ret[self.pending][1])
                except:
                    pass
                self._SetMode(0)
            elif btn=="back":
                self.pending=-1
                self._SetMode(0)
            else:
                return
        if self.p:
            self.p.OnCChange()

    def SetBox(self,x,y,w,h):
        self.ui_main.SetBox(x,y,w,h)
        self.ui_scan.SetBox(x,y,w,h)
        self.ui_con.SetBox(x,y,w,h)

    def Draw(self,fb,win):
        if self.mode==0:
            self.ui_main.Draw(fb,win)
        elif self.mode==1:
            self.ui_scan.Draw(fb,win)
        else:
            self.ui_con.Draw(fb,win)
    
    def OnKBE(self,e,d0,d1):
        if self.mode==0:
            return self.ui_main.OnKBE(e,d0,d1)
        elif self.mode==1:
            return False
        elif self.mode==2:
            return self.ui_con.OnKBE(e,d0,d1)