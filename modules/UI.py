# Copyright (C) 2025 Hongyi Chen (BeanPieChen)
# Licensed under the MIT License

import dev
from Text import TBox

class UIFB:
    def __init__(self,fb=None):
        self.fb=fb

    def Width(self):
        if self.fb:
            return self.fb.width()
        else:
            return dev.DP_WIDTH
    
    def Height(self):
        if self.fb:
            return self.fb.height()
        else:
            return dev.DP_HEIGHT
    
    def Window(self,x0,y0,x1,y1):
        if self.fb:
            self.fb.set_window(x0,y0,x1,y1)
        else:
            dev.fb_window(x0,y0,x1,y1)
    
    def Fill(self,c):
        if self.fb:
            self.fb.fill(c)
        else:
            return dev.fb_fill(c)
    
    def Pix(self,x,y,c):
        if self.fb:
            self.fb.set_pixel(x,y,c)
        else:
            dev.fb_pix(x,y,c)
    
    def HLine(self,x,y,l,c):
        if self.fb:
            self.fb.hline(x,y,l,c)
        else:
            dev.fb_hline(x,y,l,c)
    
    def VLine(self,x,y,l,c):
        if self.fb:
            self.fb.vline(x,y,l,c)
        else:
            dev.fb_vline(x,y,l,c)
    
    def Line(self,x0,y0,x1,y1,c):
        if self.fb:
            self.fb.line(x0,y0,x1,y1,c)
        else:
            dev.fb_line(x0,y0,x1,y1,c)
    
    def Rect(self,x,y,w,h,c):
        if self.fb:
            self.fb.rect(x,y,w,h,c)
        else:
            dev.fb_rect(x,y,w,h,c)
    
    def FRect(self,x,y,w,h,c):
        if self.fb:
            self.fb.fill_rect(x,y,w,h,c)
        else:
            dev.fb_frect(x,y,w,h,c)

    def Circle(self,x,y,r,c):
        if self.fb:
            self.fb.circle(x,y,r,c)
        else:
            dev.fb_circle(x,y,r,c)
    
    def FCircle(self,x,y,r,c):
        if self.fb:
            self.fb.fill_circle(x,y,r,c)
        else:
            dev.fb_fcircle(x,y,r,c)
    
    def Text(self,f,s,x,y,c):
        if self.fb:
            self.fb.text(f,s,x,y,c)
        else:
            dev.fb_text(f,s,x,y,c)
    
    def Present(self):
        if self.fb:
            dev.dp_blit(self,0,0,dev.dp_w(),dev.dp_h())
        else:
            dev.fb_present()

class UIW:
    def __init__(self,x0,y0,x1,y1):
        self.x0=x0
        self.y0=y0
        self.x1=x1
        self.y1=y1
    
    def I(self,x0,y0,x1,y1):
        if self.x0>x1 or x0>self.x1:
            return None
        if self.y0>y1 or y0>self.y1:
            return None
        return UIW(max(x0,self.x0),max(y0,self.y0),min(x1,self.x1),min(y1,self.y1))
        
class UI:
    def __init__(self,clear=dev.DPC_X,fb=None):
        self.fb=UIFB(fb)
        self.uie=None
        self.clear=clear
    
    def OnCChange(self):
        if self.uie:
            self.Draw()
    
    def Draw(self):
        if self.uie:
            self.uie.Draw(self.fb,UIW(0,0,self.fb.Width()-1,self.fb.Height()-1))
            self.fb.Present()
    
    def SetChild(self,uie):
        if self.uie:
            self.uie.p=None
        self.uie=uie
        if self.uie:
            self.uie.p=self
            self.uie.SetBox(0,0,self.fb.Width(),self.fb.Height())
        self.Draw()
    
    def on_kbe(self,e,d0,d1):
        if self.uie:
            if self.uie.OnKBE(e,d0,d1):
                self.Draw()

class UIBtn:
    def __init__(self,x,y,w,h,m,cs,f,t,cb,cb_arg):
        self.en=True
        self.focus=True
        self.down=False
        self.cb=cb
        self.cb_arg=cb_arg
        self.x=x
        self.y=y
        self.w=w
        self.h=h
        self.ox=0
        self.oy=0
        self.m=m
        self.tb=TBox(self.x+m,self.y+m,self.w-2*m,self.h-2*m,cs,f,False,t)
        self.cs=cs
        self.p=None
    
    def _ResetBox(self):
        self.tb.SetBox(self.x+self.m,self.y+self.m,self.w-2*self.m,self.h-2*self.m)

    def SetText(self,t):
        self.tb.SetText(t)

    def SetMargin(self,m):
        self.m=m
        self._ResetBox()

    def SetState(self,s):
        self.s=s
        self.tb.SetState(s)

    def OnCChange(self):
        if self.p:
            self.p.OnCChange()

    def MinW(self):
        return self.tb.MinW()+self.m*2

    def MinH(self):
        return self.tb.MinH()+self.m*2
    
    def MaxW(self):
        return self.MinW()
    
    def MaxH(self):
        return self.MinH()

    def SetEnable(self,en):
        self.en=en
        self.tb.SetEnable(en)

    def SetFocus(self,focus):
        self.focus=focus
        self.tb.SetFocus(focus)
        if not focus:
            self.down=False

    def SetBox(self,x,y,w,h):
        self.x=x
        self.y=y
        self.w=w
        self.h=h
        self._ResetBox()

    def SetCS(self,cs):
        self.cs=cs
        self.tb.SetCS(cs)

    def SetOffset(self,ox,oy):
        self.ox=ox
        self.oy=oy
        self.tb.SetOffset(ox,oy)

    def Draw(self,fb,win):
        x0=self.x+self.ox
        y0=self.y+self.oy
        win=win.I(x0,y0,x0+self.w-1,y0+self.h-1)
        if win is None:
            return
        fb.Window(win.x0,win.y0,win.x1,win.y1)
        fg,bg=self.cs.EFD(self.en,self.focus,self.down)
        fb.FRect(x0,y0,self.w,self.h,bg)
        self.tb.Draw(fb,win)

    def OnKBE(self,e,d0,d1):
        if not self.en:
            return False
        if self.down:
            if e==dev.KBE_UP and d0==dev.KSC_ENTER:
                self.down=False
                self.cb(self.cb_arg)
                return True
        else:
            if e==dev.KBE_DOWN and d0==dev.KSC_ENTER:
                self.down=True
                return True

class UISlider:
    def __init__(self,x,y,w,h,m,cs,f,t,l,v,cb,cb_arg):
        self.en=True
        self.focus=True
        self.cb=cb
        self.cb_arg=cb_arg
        self.l=0
        self.v=0
        self.SetLen(l)
        self.SetValue(v)
        self.x=x
        self.y=y
        self.w=w
        self.h=h
        self.ox=0
        self.oy=0
        self.m=m
        self.tb=TBox(x+m,y+m,w-2*m,round((h-2*m)/2),cs,f,False,t)
        self.cs=cs
        self.p=None

    def _ResetBox(self):
        self.tb.SetBox(self.x+self.m,self.y+self.m,self.w-2*self.m,round((self.h-2*self.m)/2))

    def SetLen(self,l):
        self.l=max(2,l)
    
    def GetValue(self):
        return self.v

    def SetValue(self,v):
        self.v=min(self.l-1,max(0,v))

    def SetText(self,t):
        self.tb.SetText(t)

    def SetMargin(self,m):
        self.m=m
        self._ResetBox()

    def SetState(self,s):
        self.s=s
        self.tb.SetState(s)

    def OnCChange(self):
        if self.p:
            self.p.OnCChange()

    def MinW(self):
        return self.tb.MinW()+self.m*2

    def MinH(self):
        return self.tb.MinH()*2+self.m*2
    
    def MaxW(self):
        return self.MinW()
    
    def MaxH(self):
        return self.MinH()

    def SetEnable(self,en):
        self.en=en
        self.tb.SetEnable(en)

    def SetFocus(self,focus):
        self.focus=focus
        self.tb.SetFocus(focus)

    def SetBox(self,x,y,w,h):
        self.x=x
        self.y=y
        self.w=w
        self.h=h
        self._ResetBox()

    def SetCS(self,cs):
        self.cs=cs
        self.tb.SetCS(cs)

    def SetOffset(self,ox,oy):
        self.ox=ox
        self.oy=oy
        self.tb.SetOffset(ox,oy)
    
    def Draw(self,fb,win):
        x0=self.x+self.ox
        y0=self.y+self.oy
        win=win.I(x0,y0,x0+self.w-1,y0+self.h-1)
        if win is None:
            return
        fb.Window(win.x0,win.y0,win.x1,win.y1)
        fg,bg=self.cs.EF(self.en,self.focus)
        fb.FRect(x0,y0,self.w,self.h,bg)
        self.tb.Draw(fb,win)
        fb.Window(win.x0,win.y0,win.x1,win.y1)
        sw=round(self.w*(2/3))
        sx=x0+round((self.w-sw)/2)
        sy=y0+round(self.h*(2/3))
        fb.HLine(sx,sy,sw,self.cs.fg_dis)
        l=self.l
        v=self.v
        sc=sx
        dt=round(sw/(l-1))
        for i in range(l):
            if i==l-1:
                sc=sx+sw-1
            if i==v:
                fb.VLine(sc,sy-3,6,fg)
            else:
                fb.VLine(sc,sy-2,2,self.cs.fg_dis)
            sc+=dt


    def OnKBE(self,e,d0,d1):
        if self.en:
            if e==dev.KBE_DOWN:
                if d0==dev.KSC_COMMA:
                    if self.v>0:
                        self.v-=1
                        self.cb(self.cb_arg,self.v)
                        return True
                elif d0==dev.KSC_SLASH:
                    if self.v<self.l-1:
                        self.v+=1
                        self.cb(self.cb_arg,self.v)
                        return True
        return False

class UICombo:
    def __init__(self,x,y,w,h,m,cs,f,t,s,v,cb,cb_arg):
        self.en=True
        self.focus=True
        self.cb=cb
        self.cb_arg=cb_arg
        self.s=s
        self.v=v
        self.x=x
        self.y=y
        self.w=w
        self.h=h
        self.ox=0
        self.oy=0
        self.m=m
        self.tb=TBox(x+m,y+m,w-2*m,round((h-3*m)/2),cs,f,False,t)
        self.curr=TBox(x+m,y+m*2+self.tb.h,w-2*m,round((h-3*m)/2),cs,f,False,s[v],1)
        self.cs=cs
        self.p=None

    def _ResetBox(self):
        x,y,w,h,m=self.x,self.y,self.w,self.h,self.m
        self.tb.SetBox(x+m,y+m,w-2*m,round((h-3*m)/2))
        self.curr.SetBox(x+m,y+m*2+self.tb.h,w-2*m,round((h-3*m)/2))
    
    def GetValue(self):
        return self.v

    def SetValue(self,v):
        self.v=min(self.l-1,max(0,v))

    def SetText(self,t):
        self.tb.SetText(t)

    def SetMargin(self,m):
        self.m=m
        self._ResetBox()

    def SetState(self,s):
        self.s=s
        self.tb.SetState(s)

    def OnCChange(self):
        if self.p:
            self.p.OnCChange()

    def MinW(self):
        return self.tb.MinW()+self.m*2

    def MinH(self):
        return self.tb.MinH()*2+self.m*3
    
    def MaxW(self):
        return self.MinW()
    
    def MaxH(self):
        return self.MinH()

    def SetEnable(self,en):
        self.en=en
        self.tb.SetEnable(en)
        self.curr.SetEnable(en)

    def SetFocus(self,focus):
        self.focus=focus
        self.tb.SetFocus(focus)
        self.curr.SetFocus(focus)

    def SetBox(self,x,y,w,h):
        self.x=x
        self.y=y
        self.w=w
        self.h=h
        self._ResetBox()

    def SetCS(self,cs):
        self.cs=cs
        self.tb.SetCS(cs)
        self.curr.SetCS(cs)

    def SetOffset(self,ox,oy):
        self.ox=ox
        self.oy=oy
        self.tb.SetOffset(ox,oy)
        self.curr.SetOffset(ox,oy)
    
    def Draw(self,fb,win):
        x0=self.x+self.ox
        y0=self.y+self.oy
        win=win.I(x0,y0,x0+self.w-1,y0+self.h-1)
        if win is None:
            return
        fb.Window(win.x0,win.y0,win.x1,win.y1)
        fg,bg=self.cs.EF(self.en,self.focus)
        fb.FRect(x0,y0,self.w,self.h,bg)
        self.tb.Draw(fb,win)
        self.curr.Draw(fb,win)
        m=self.m
        ly0=y0+2*m+self.tb.h+round(self.curr.h/2)
        if self.v>0:
            lx0=x0+4*m
            fb.Line(lx0,ly0,lx0+4,ly0-4,fg)
            fb.Line(lx0,ly0,lx0+4,ly0+4,fg)
        if self.v<len(self.s)-1:
            lx0=x0+self.w-4*m
            fb.Line(lx0,ly0,lx0-4,ly0-4,fg)
            fb.Line(lx0,ly0,lx0-4,ly0+4,fg)

    def OnKBE(self,e,d0,d1):
        if self.en:
            if e==dev.KBE_DOWN:
                if d0==dev.KSC_COMMA:
                    if self.v>0:
                        self.v-=1
                        self.curr.SetText(self.s[self.v])
                        self.cb(self.cb_arg,self.v)
                        return True
                elif d0==dev.KSC_SLASH:
                    if self.v<len(self.s)-1:
                        self.v+=1
                        self.curr.SetText(self.s[self.v])
                        self.cb(self.cb_arg,self.v)
                        return True
        return False

class UIList:
    def __init__(self,x,y,w,h,cs,vertical=True):
        self.en=True
        self.focus=True
        self.x=x
        self.y=y
        self.w=w
        self.h=h
        self.ox=0
        self.oy=0
        self.r=0
        self.s=0
        self.cs=cs
        self.v=vertical
        self.children=[]
        self.curr=-1
    
    def _SloveLO(self):
        min_l=[]
        min_l_sum=0
        expand_l=[]
        expand_sum=0
        expand_num=0
        no_max_num=0
        for c in self.children:
            _min_l=c.MinH() if self.v else c.MinW()
            _max_l=c.MaxH() if self.v else c.MaxW()
            min_l.append(_min_l)
            min_l_sum+=_min_l
            if _max_l:
                expand=_max_l-_min_l
                if expand>0:
                    expand_num+=1
                expand_l.append(expand)
                expand_sum+=expand
            else:
                no_max_num+=1
                expand_l.append(None)
        if min_l_sum>(self.h if self.v else self.w):
            self.r=min_l_sum-(self.h if self.v else self.w)
            p=self.y if self.v else self.x
            for c,l in zip(self.children,min_l):
                if self.v:
                    c.SetBox(self.x,p,self.w,l)
                else:
                    c.SetBox(p,self.y,l,self.h)
                p+=l
        else:
            self.r=0
            p=self.y if self.v else self.x
            _extent=(self.h if self.v else self.w)-min_l_sum
            if no_max_num:
                expand=round(_extent/no_max_num)
                for c,l,e in zip(self.children,min_l,expand_l):
                    if e is None:
                        _l=l
                        if no_max_num==1:
                            _l+=_extent
                            _extent=0
                        else:
                            _l+=expand
                            _extent-=expand
                        no_max_num-=1
                        if self.v:
                            c.SetBox(self.x,p,self.w,_l)
                        else:
                            c.SetBox(p,self.y,_l,self.h)
                        p+=_l
                    else:
                        if self.v:
                            c.SetBox(self.x,p,self.w,l)
                        else:
                            c.SetBox(p,self.y,l,self.h)
                        p+=l
            else:
                children=self.children
                for i in range(len(children)):
                    _l=min_l[i]
                    if expand_l[i]:
                        if expand_num==1:
                            _l+=_extent
                            _extent=0
                        else:
                            expand=min(round(self.r*expand_l[i]/expand_sum),expand_l[i])
                            _l+=expand
                            _extent-=expand
                        expand_num-=1
                    if self.v:
                        children[i].SetBox(self.x,p,self.w,_l)
                    else:
                        children[i].SetBox(p,self.y,_l,self.h)
                    p+=_l

    def _UpdateCState(self):
        for i in range(len(self.children)):
            if i==self.curr:
                self.children[i].SetFocus(True)
            else:
                self.children[i].SetFocus(False)

    def _UpdateScroll(self):
        if self.curr==-1:
            self.s=0
        else:
            curr=self.children[self.curr]
            if (curr.y if self.v else curr.x)-self.s<(self.y if self.v else self.x):
                self.s=(curr.y-self.y) if self.v else (curr.x-self.x)
            elif ((curr.y+curr.h) if self.v else (curr.x+curr.w))-self.s>((self.y+self.h) if self.v else (self.x+self.w)):
                self.s=(curr.y+curr.h-self.y-self.h) if self.v else (curr.x+curr.w-self.x-self.w)
            self.s=min(max(self.s,0),self.r)
        for c in self.children:
            if self.v:
                c.SetOffset(self.ox,self.oy-self.s)
            else:
                c.SetOffset(self.ox-self.s,self.oy)
    
    def _CheckSelected(self):
        if self.curr<len(self.children) and self.curr>0 and self.children[self.curr].en:
            pass
        else:
            for i in range(len(self.children)):
                if self.children[i].en:
                    self.curr=i
                    break
    
    def SetSelected(self,i):
        self.curr=i
        self._CheckSelected()
        self._UpdateScroll()
        self._UpdateCState()

    def SetChildren(self,children):
        self.children=children
        self._SloveLO()
        self._CheckSelected()
        self._UpdateScroll()
        self._UpdateCState()

    def MinW(self):
        if self.v:
            min_w=None
            for c in self.children:
                c_min_w=c.MinW()
                if min_w is None:
                    min_w=c_min_w
                else:
                    if c_min_w<min_w:
                        min_w=c_min_w
            return min_w
        else:
            sum_w=0
            for c in self.children:
                sum_w+=c.MinW()
            return sum_w

    def MinH(self):
        if self.v:
            sum_h=0
            for c in self.children:
                sum_h+=c.MinW()
            return sum_h
        else:
            min_h=None
            for c in self.children:
                c_min_h=c.MinH()
                if min_h is None:
                    min_h=c_min_h
                else:
                    if c_min_h<min_h:
                        min_h=c_min_h
            return min_h
    
    def MaxW(self):
        return None
    
    def MaxH(self):
        return None

    def SetEnable(self,en):
        self.en=en

    def SetFocus(self,focus):
        self.focus=focus

    def SetBox(self,x,y,w,h):
        self.x=x
        self.y=y
        self.w=w
        self.h=h
        self._SloveLO()
        self._UpdateScroll()

    def SetCS(self,cs):
        self.cs=cs
        for c in self.children:
            c.SetCS(cs)

    def SetOffset(self,ox,oy):
        self.ox=ox
        self.oy=oy
        for c in self.children:
            if self.v:
                c.SetOffset(ox,oy-self.s)
            else:
                c.SetOffset(ox-self.s,oy)

    def Draw(self,fb,win):
        wx0=self.x+self.ox
        wy0=self.y+self.oy
        win=win.I(wx0,wy0,self.x+self.ox+self.w-1,self.y+self.oy+self.h-1)
        if win is None:
            return
        fb.Window(win.x0,win.y0,win.x1,win.y1)
        fg,bg=self.cs.E(self.en)
        wx1=wx0+self.w-1
        wy1=wy0+self.h-1
        fb.FRect(wx0,wy0,self.w,self.h,bg)
        for c in self.children:
            c.Draw(fb,win)
        fb.Window(win.x0,win.y0,win.x1,win.y1)
        if self.r:
            if self.v:
                fb.VLine(wx1,wy0,self.h,bg)
                sb_h=max(round(self.h*self.h/(self.r+self.h)),1)
                sb_o=round(self.s/self.r*(self.h-sb_h))
                fb.VLine(wx1,wy0+sb_o,sb_h,fg)
            else:
                fb.HLine(wx0,wy1,self.w,bg)
                sb_h=max(round(self.h*self.h/(self.r+self.h)),1)
                sb_o=round(self.s/self.r*(self.h-sb_h))
                fb.VLine(wx1,wy0+sb_o,sb_h,fg)
    
    def OnKBE(self,e,d0,d1):
        if not self.en:
            return False
        if self.curr>=0:
            if hasattr(self.children[self.curr],"grab") and self.children[self.curr].grab:
                pass
            else:
                if e==dev.KBE_DOWN:
                    if d0==dev.KSC_SEMI:
                        _curr=self.curr-1
                        while _curr>=0:
                            if self.children[_curr].en:
                                break
                            _curr-=1
                        if _curr>=0:
                            self.curr=_curr
                            self._UpdateCState()
                            self._UpdateScroll()
                            return True
                        else:
                            return False
                    elif d0==dev.KSC_FS:
                        _curr=self.curr+1
                        mc=len(self.children)
                        while _curr<mc:
                            if self.children[_curr].en:
                                break
                            _curr+=1
                        if _curr<mc:
                            self.curr=_curr
                            self._UpdateCState()
                            self._UpdateScroll()
                            return True
                        else:
                            return False
            return self.children[self.curr].OnKBE(e,d0,d1)
