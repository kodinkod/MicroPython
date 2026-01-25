# Copyright (C) 2025 Hongyi Chen (BeanPieChen)
# Licensed under the MIT License

import dev
from Text import TEdit,TBox,TLEdit
from UI import UIList,UIBtn
import os

def _OnEditorBtn(args):
    args[0].OnBtn(args[1])

class Editor:
    def __init__(self,x,y,w,h,cs,f,on_exit):
        self.mode=0
        self.te=TEdit(x,y,w,h,cs,f,True)
        self.path=None
        self.t_path=TBox(x,y,w,h,cs,f,False)
        self.t_path.SetEnable(False)
        self.t_path.SetText(self._PathText())
        self.b_save_as=UIBtn(x,y,w,h,2,cs,f,"Save As...",_OnEditorBtn,(self,"save_as"))
        self.ui_menu=UIList(x,y,w,h,cs)
        self.ui_menu.SetChildren([
            self.t_path,
            UIBtn(x,y,w,h,2,cs,f,"Back",_OnEditorBtn,(self,"back")),
            UIBtn(x,y,w,h,2,cs,f,"Save",_OnEditorBtn,(self,"save")),
            self.b_save_as,
            UIBtn(x,y,w,h,2,cs,f,"Exit",_OnEditorBtn,(self,"exit"))
        ])
        self.ui_path=UIList(x,y,w,h,cs)
        t=TBox(x,y,w,h,cs,f,False)
        t.SetText("Save to...")
        t.SetEnable(False)
        self.tle_path=TLEdit(x,y,w,h,2,cs,f)
        self.ui_path.SetChildren([
            t,
            self.tle_path,
            UIBtn(x,y,w,h,2,cs,f,"OK",_OnEditorBtn,(self,"ok")),
            UIBtn(x,y,w,h,2,cs,f,"Cancel",_OnEditorBtn,(self,"cancel"))
        ])
        t=TBox(x,y,w,h,cs,f,False)
        t.SetText("Unsave change will be discarded, proceed?")
        t.SetEnable(False)
        self.ui_quest=UIList(x,y,w,h,cs)
        self.ui_quest.SetChildren([
            t,
            UIBtn(x,y,w,h,2,cs,f,"Yes",_OnEditorBtn,(self,"yes")),
            UIBtn(x,y,w,h,2,cs,f,"No",_OnEditorBtn,(self,"no"))
        ])
        self.ui_error=UIList(x,y,w,h,cs)
        self.t_error=TBox(x,y,w,h,cs,f,False)
        self.t_error.SetEnable(False)
        self.ui_error.SetChildren([
            self.t_error,
            UIBtn(x,y,w,h,2,cs,f,"OK",_OnEditorBtn,(self,"ok"))
        ])
        self.on_exit=on_exit
        self.p=None

    def _PathText(self):
        ret=self.path
        if not ret:
            ret="[New]"
        if self.te.change:
            ret+="*"
        return ret
    
    def _SetMode(self,mode):
        if mode==self.mode:
            return
        self.mode=mode
        if mode==1:
            self.ui_menu.SetSelected(1)
            self.t_path.SetText(self._PathText())
            if self.path:
                self.b_save_as.SetEnable(True)
            else:
                self.b_save_as.SetEnable(False)
        elif mode==2:
            self.ui_path.SetSelected(1)
            if self.path:
                self.tle_path.SetText(self.path)
            else:
                self.tle_path.SetText(os.getcwd())

    def Open(self,path):
        self.Clear()
        f=open(path,"r")
        l=f.readline()
        while l:
            self.te.Insert(l)
            l=f.readline()
        f.close()
        self.te.ToBegin()
        self.path=path
        self.te.change=False

    def Save(self,path):
        try:
            with open(path,"w") as f:
                ls=self.te.te.ls
                l=len(ls)-1
                for i in range(l+1):
                    f.write(ls[i])
                    if i<l:
                        f.write("\n")
            self.te.change=False
            self.path=path
            self.t_path.SetText(self._PathText())
            return True
        except Exception as e:
            self.t_error.SetText(str(e))
            return False

    def Clear(self):
        self.path=None
        self.te.Clear()
        self.te.change=False
        self.ui_menu.children[0].SetText(self._PathText())

    def OnBtn(self,btn):
        if self.mode==0:
            return
        elif self.mode==1:
            if btn=="back":
                self._SetMode(0)
            elif btn=="save":
                if self.path:
                    if self.Save(self.path):
                        self._SetMode(0)
                    else:
                        self._SetMode(4)
                else:
                    self._SetMode(2)
            elif btn=="save_as":
                self._SetMode(2)
            elif btn=="exit":
                if self.te.change:
                    self._SetMode(3)
                else:
                    self.Clear()
                    self._SetMode(0)
                    self.on_exit()
            else:
                return
        elif self.mode==2:
            if btn=="ok":
                if self.Save(self.tle_path.GetText()):
                    self._SetMode(0)
                else:
                    self._SetMode(4)
            elif btn=="cancel":
                self._SetMode(0)
            else:
                return
        elif self.mode==3:
            if btn=="yes":
                self.Clear()
                self._SetMode(0)
                self.on_exit()
            elif btn=="no":
                self._SetMode(0)
            else:
                return
        else:
            self.SetMode(0)
        if self.p:
            self.p.OnCChange()

    def SetBox(self,x,y,w,h):
        self.te.SetBox(x,y,w,h)
        self.ui_menu.SetBox(x,y,w,h)
        self.ui_path.SetBox(x,y,w,h)
        self.ui_quest.SetBox(x,y,w,h)
        self.ui_error.SetBox(x,y,w,h)
    
    def Draw(self,fb,win):
        if self.mode==0:
            self.te.Draw(fb,win)
        elif self.mode==1:
            self.ui_menu.Draw(fb,win)
        elif self.mode==2:
            self.ui_path.Draw(fb,win)
        elif self.mode==3:
            self.ui_quest.Draw(fb,win)
        else:
            self.ui_error.Draw(fb,win)

    def OnKBE(self,e,d0,d1):
        if self.mode==0:
            if e==dev.KBE_DOWN and d1==dev.KV_ESC:
                self._SetMode(1)
                return True
            ret=self.te.OnKBE(e,d0,d1)
            return ret
        elif self.mode==1:
            return self.ui_menu.OnKBE(e,d0,d1)
        elif self.mode==2:
            return self.ui_path.OnKBE(e,d0,d1)
        elif self.mode==3:
            return self.ui_quest.OnKBE(e,d0,d1)
        else:
            return self.ui_error.OnKBE(e,d0,d1)