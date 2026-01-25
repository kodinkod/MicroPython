# Copyright (C) 2025 Hongyi Chen (BeanPieChen)
# Licensed under the MIT License

import dev
import io
import os
from Text import TEdit
from micropython import schedule

DK=[dev.KV_UP,dev.KV_DOWN,dev.KV_LEFT,dev.KV_RIGHT]

EOL=b'\r\n'
ESC_UP=b'\x1B[A'
ESC_DOWN=b'\x1B[B'
ESC_RIGHT=b'\x1B[C'
ESC_LEFT=b'\x1B[D'
ESC_TRIM=b'\x1B[K'

MAXL=const(50)

RN=hasattr(os, "dupterm_notify")

def TRInfo(a):
    os.dupterm_notify(None)

class Terminal(io.IOBase):
    def __init__(self,x,y,w,h,cs,f,bg):
        self.t=TEdit(x,y,w,h,cs,f,bg)
        self.t.p=self
        self.ctrl=False
        self.p=None
        self.q=[]
        self.esc=0
        self.esc_arg=0
        
    def readinto(self,buf):
        if not self.q:
            return None
        l=min(len(buf),len(self.q))
        for i in range(l):
            buf[i]=self.q.pop(0)
        return l
    
    def write(self,buf):
        l=len(buf)
        dirty=False
        for c in buf:
            if self.esc==0 and c==27:
                self.esc=1
            elif self.esc==1 and c==91:
                self.esc=2
            elif self.esc==2 and c==75:
                self.esc=0
                self.t.Trim()
                dirty=True
            elif self.esc==2 and c>=48 and c<=57:
                self.esc_arg=self.esc_arg*10+c-48
            elif self.esc==2 and c==68:
                self.esc=0
                self.t.Left(self.esc_arg)
                self.esc_arg=0
                dirty=True
            else:
                self.esc=0
                self.esc_arg=0
                if c==EOL[0]:
                    self.t.ToLB()
                    dirty=True
                elif c==EOL[1]:
                    self.t.LineFeed()
                    if self.t.LN()>MAXL:
                        self.t.PopLine()
                    dirty=True
                elif c==8:
                    self.t.OnKBE(dev.KBE_DOWN,None,dev.KV_LEFT)
                    dirty=True
                else:
                    self.t.Replace(chr(c))
                    dirty=True
        if dirty:
            if self.p:
                self.p.OnCChange()
        return l
    
    def MinW(self):
        return self.t.MinW()
    
    def MinW(self):
        return self.t.MinW()

    def MaxW(self):
        return self.t.MaxW()
    
    def MaxH(self):
        return self.t.MaxH()

    def SetBox(self,x,y,w,h):
        self.t.SetBox(x,y,w,h)
    
    def SetCS(self,cs):
        self.t.SetCS(cs)

    def SetOffset(self,ox,oy):
        self.t.SetOffset(ox,oy)

    def Draw(self,fb,win):
        self.t.Draw(fb,win)
    
    def OnKBE(self,e,d0,d1):
        t=self.t
        if e==dev.KBE_DOWN:
            if d1==dev.KSC_CTRL:
                self.ctrl=True
                return t.OnKBE(e,d0,d1)
            if d1==dev.KSC_ENTER:
                for c in EOL:
                    self.q.append(c)
            elif d1==dev.KSC_TAB:
                self.q.append(9)
            elif d1==dev.KV_UP:
               for c in ESC_UP:
                   self.q.append(c)
            elif d1==dev.KV_DOWN:
                for c in ESC_DOWN:
                   self.q.append(c)
            elif d1==dev.KV_LEFT:
                for c in ESC_LEFT:
                   self.q.append(c)
            elif d1==dev.KV_RIGHT:
                for c in ESC_RIGHT:
                   self.q.append(c)
            elif d1==dev.KSC_BS:
                self.q.append(8)
            else:
                if self.ctrl:
                    if d1==dev.KSC_A:
                        self.q.append(1)
                    elif d1==dev.KSC_B:
                        self.q.append(2)
                    elif d1==dev.KSC_C:
                        self.q.append(3)
                    elif d1==dev.KSC_D:
                        self.q.append(4)
                    else:
                        return self.t.OnKBE(e,d0,d1)
            if RN:
                schedule(TRInfo,None)
            return False
        elif e==dev.KBE_UP:
            if d0==dev.KSC_CTRL:
                self.ctrl=False
            return t.OnKBE(e,d0,d1)
        else:
            if self.ctrl:
                return False
            self.q.append(d0)
            if RN:
                schedule(TRInfo,None)
            return False
        