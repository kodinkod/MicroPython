# Copyright (C) 2025 Hongyi Chen (BeanPieChen)
# Licensed under the MIT License

import dev

def TextH(ls,fh,gap):
    return len(ls)*(fh+gap)-gap

def TextW(ls,fw):
    w=0
    for l in ls:
        if len(l)>w:
            w=len(l)
    return w*fw


def DrawLine(l,f,fh,fw,c,x,py,fb,wx0,wy0,wx1,wy1):
    ll=len(l)
    if ll==0 or py+fh<wy0 or py>wy1:
        return
    x1=x+ll*fw
    if x1<wx0 or x>wx1:
        return
    s=0
    e=ll
    if x<wx0:
        s=int((wx0-x)/fw)
    if x1>wx1:
        e=int((wx1-x)/fw)+1
    if s==0 and e==ll:
        fb.Text(f,l,x,py,c)
    else:
        fb.Text(f,l[s:e],x+s*fw,py,c)

class TE:
    def __init__(self):
        self.ls=[""]
    
    def LN(self):
        return len(self.ls)
    
    def CheckP(self,l,c):
        ls=self.ls
        if l<0 or c<0:
            return 0,0
        if l>=len(ls):
            return len(ls)-1,len(len(ls)-1)
        if c>len(ls[l]):
            c=len(ls[l])
        return l,c
    
    def PopLine(self,l,c):
        ls=self.ls
        if len(ls)==1:
            ls[0]=""
            return 0,0
        else:
            ls.pop(0)
        if l==0:
            return 0,0
        else:
            return l-1,c
    
    def Replace(self,l,c,s):
        if not s:
            return l,c
        ls=self.ls
        head=ls[l][:c]
        tail=ls[l][c+len(s):]
        ls[l]=head+s+tail
        return l,c+len(s)
    
    def Trim(self,l,c):
        ls=self.ls
        ls[l]=ls[l][:c]
    
    def Insert(self,l,c,s):
        if not s:
            return l,c
        ls=self.ls
        nl=[]
        lb=0
        head=ls[l][:c]
        tail=ls[l][c:]
        for i in range(len(s)):
            if s[i]=="\n":
                if lb==0:
                    nl.append(s[0:i])
                else:
                    nl.append(s[lb:i])
                lb=i+1
        nl.append(s[lb:]+tail)
        for i in range(len(nl)):
            if i==0:
                ls[l]=head+nl[i]
            else:
                ls.insert(l+1,nl[i])
        if len(nl)==1:
            return l,c+len(s)
        else:
            return l+len(nl)-1,len(nl[-1])-len(tail)
    
    def LineFeed(self,l,s):
        l+=1
        self.ls.insert(l,"")
        c=0
        return l,c
    
    def Delete(self,lb,cb,le,ce):
        lb,cb=self.CheckP(lb,cb)
        le,ce=self.CheckP(le,ce)
        ls=self.ls
        if lb>le:
            le,lb=lb,le
            ce,cb=cb,ce
        elif lb==le:
            if cb==ce:
                return lb,ce
            elif cb>ce:
                ce,cb==cb,ce
        self.w=-1
        head=""
        i=cb
        while True:
            if lb==le:
                ls[lb]=head+ls[lb][0:i]+ls[lb][ce:]
                return lb,cb
            else:
                ls[lb]=ls[lb][0:i]
                if len(ls[lb])!=0:
                    head=ls[lb]
                ls.pop(lb)
                le=le-1
                i=0
    
    def Clear(self):
        self.ls=[""]
        self.w=-1

    def CLeft(self,l,c):
        l,c=self.CheckP(l,c)
        ls=self.ls
        if c==0:
            if l==0:
                return l,c
            else:
                return l-1,len(ls[l-1])
        else:
            return l,c-1
    
    def CRight(self,l,c):
        l,c=self.CheckP(l,c)
        ls=self.ls
        if c+1>len(ls[l]):
            if l+1>=len(ls):
                return l,c
            else:
                return l+1,0
        else:
            return l,c+1
    
    def CPos(self,f,l,c):
        fh=f.HEIGHT
        gap=int(fh/4)
        return c*f.WIDTH,l*(fh+gap)
    
    def End(self):
        ls=self.ls
        le=len(ls)-1
        ce=len(ls[le])
        return le,ce
    
    def GetText(self,*args):
        ls=self.ls
        lb=args[0]
        cb=args[1]
        le,ce=self.End()
        if len(args)>=4:
            le=args[2]
            ce=args[3]
        ret=""
        i=cb
        while True:
            if lb==le:
                return ret+ls[le][i:ce]
            else:
                ret+=ls[lb][i:]+"\n"
            lb+=1

    def Draw(self,f,gap,c,x,y,fb,wx0,wy0,wx1,wy1):
        ls=self.ls
        fh=f.HEIGHT
        fw=f.WIDTH
        py=y
        for l in ls:
            DrawLine(l,f,fh,fw,c,x,py,fb,wx0,wy0,wx1,wy1)
            py+=fh+gap

class TBox:
    def __init__(self,x,y,w,h,cs,f,bg,t="Text",ah=0,av=0):
        self.en=True
        self.focus=True
        self.ox=0
        self.oy=0
        self.x=x
        self.y=y
        self.w=w
        self.h=h
        self.cs=cs
        self.f=f
        self.fh=f.HEIGHT
        self.gap=int(self.fh/4)
        self.fw=f.WIDTH
        self.bg=bg
        self.t=t
        self.ls=[""]
        self.tw=0
        self.th=0
        self.ah=ah
        self.av=av
        self._UpdateText()
    
    def _UpdateText(self):
        w=self.w
        fw=self.f.WIDTH
        t=self.t
        ls=[]
        lb=0
        lw=0
        i=0
        l=len(t)
        while i<l:
            if t[i]=="\n":
                ls.append(t[lb:i])
                lb=i+1
                i=lb
                lw=0
            elif lw+fw>w:
                j=i-1
                while j>=lb:
                    if t[j]==" " or t[j]=="/":
                        break
                    j-=1
                if j>=lb:
                    ls.append(t[lb:j+1])
                    lb=j+1
                else:
                    ls.append(t[lb:i])
                    lb=i+1
                i=lb
                lw=0
            else:
                lw+=fw
                i+=1
        ls.append(t[lb:i])
        self.ls=ls
        self.tw=TextW(self.ls,self.fw)
        self.th=TextH(self.ls,self.fh,self.gap)

    def SetText(self,s):
        self.t=s
        self._UpdateText()

    def MinW(self):
        return self.tw

    def MinH(self):
        return self.th

    def MaxW(self):
        return None
    
    def MaxH(self):
        return None

    def SetEnable(self,en):
        self.en=en

    def SetFocus(self,focus):
        self.focus=focus

    def SetOffset(self,ox,oy):
        self.ox=ox
        self.oy=oy

    def SetBox(self,x,y,w,h):
        self.x=x
        self.y=y
        self.w=w
        self.h=h
        self._UpdateText()

    def SetCS(self,cs):
        self.cs=cs

    def Draw(self,fb,win):
        wx0=self.x+self.ox
        wy0=self.y+self.oy
        w=self.w
        wx1=wx0+w-1
        h=self.h
        wy1=wy0+h-1
        if wx0>wx1 or wy0>wy1:
            return
        win=win.I(wx0,wy0,wx1,wy1)
        if win is None:
            return
        fb.Window(win.x0,win.y0,win.x1,win.y1)
        f=self.f
        fh=self.fh
        gap=self.gap
        fw=self.fw
        fg,bg=self.cs.EF(self.en,self.focus)
        if self.bg:
            fb.FRect(wx0,wy0,self.w,self.h,bg)
        py=wy0
        if self.av==2:
            py=wy1-self.th
        elif self.av==1:
            py=wy0+round(h/2)-round(self.th/2)
        if self.ah==2:
            for l in self.ls:
                DrawLine(l,f,fh,fw,fg,wx1-len(l)*fw,py,fb,wx0,wy0,wx1,wy1)
                py+=fh+gap
        elif self.ah==1:
            for l in self.ls:
                DrawLine(l,f,fh,fw,fg,wx0+round((w-len(l)*fw)/2),py,fb,wx0,wy0,wx1,wy1)
                py+=fh+gap
        else:
            for l in self.ls:
                DrawLine(l,f,fh,fw,fg,wx0,py,fb,wx0,wy0,wx1,wy1)
                py+=fh+gap

    def OnKBE(self,e,d0,d1):
        return False


class TEdit:
    def __init__(self,x,y,w,h,cs,f,bg):
        self.ox=0
        self.oy=0
        self.x=x
        self.y=y
        self.w=w
        self.h=h
        self.cs=cs
        self.f=f
        self.fh=f.HEIGHT
        self.gap=int(self.fh/4)
        self.fw=f.WIDTH
        self.bg=bg
        self.te=TE()
        self.sx=0
        self.sy=0
        self.ctrl=False
        self.l=0
        self.c=0
        self.cx=0
        self.cy=0
        self.rx=0
        self.ry=0
        self.mc=0
        self.tw=TextW(self.te.ls,self.fw)
        self.th=TextH(self.te.ls,self.fh,self.gap)
        self.cursor=True
        self.change=False
        self.p=None
    
    def _UpdateOR(self):
        self.tw=TextW(self.te.ls,self.fw)
        self.th=TextH(self.te.ls,self.fh,self.gap)
        self.ry=max(self.th+self.gap-self.h,0)
        self.rx=max(self.tw+self.fw-(self.w-(1 if self.ry else 0)),0)
    
    def _SetScroll(self,sx,sy):     
        self.sx=sx if sx<self.rx else self.rx
        self.sx=0 if self.sx<0 else self.sx
        self.sy=sy if sy<self.ry else self.ry
        self.sy=0 if self.sy<0 else self.sy
    
    def _UpdateCP(self,sx,sy):
        cx=self.c*self.fw
        cy=self.l*(self.fh+self.gap)
        self.cx=cx
        self.cy=cy
        if cx-sx<0:
            sx=cx
        elif cx-sx>=self.w:
            sx=cx-self.w+1
        if cy-sy<0:
            sy=cy
        elif cy+self.fh-sy>=self.h:
            sy=cy+self.fh-self.h
        return sx,sy

    def LN(self):
        return self.te.LN()
    
    def PopLine(self):
        self.l,self.c=self.te.PopLine(self.l,self.c)
        self._UpdateOR()
        sx,sy=self._UpdateCP(self.sx,self.sy)
        self._SetScroll(sx,sy)
        self.change=True
    
    def Replace(self,s):
        l=self.l
        c=self.c
        l,c=self.te.Replace(l,c,s)
        if (l,c)!=(self.l,self.c):
            self.mc=c
            self._UpdateOR()
            self.l=l
            self.c=c
            sx,sy=self._UpdateCP(self.sx,self.sy)
            self._SetScroll(sx,sy)
            self.change=True
    
    def Trim(self):
        self.te.Trim(self.l,self.c)
        self.change=True
    
    def Insert(self,s):
        l=self.l
        c=self.c
        l,c=self.te.Insert(l,c,s)
        if (l,c)!=(self.l,self.c):
            self.mc=c
            self._UpdateOR()
            self.l=l
            self.c=c
            sx,sy=self._UpdateCP(self.sx,self.sy)
            self._SetScroll(sx,sy)
            self.change=True
    
    def LineFeed(self):
        self.l,self.c=self.te.LineFeed(self.l,self.c)
        self.mc=self.c
        self._UpdateOR()
        sx,sy=self._UpdateCP(self.sx,self.sy)
        self._SetScroll(sx,sy)
        self.change=True
    
    def Delete(self,lb,cb):
        l=self.l
        c=self.c
        l,c=self.te.Delete(lb,cb,l,c)
        if (l,c)!=(self.l,self.c):
            self.mc=c
            self._UpdateOR()
            self.l=l
            self.c=c
            sx,sy=self._UpdateCP(self.sx,self.sy)
            self._SetScroll(sx,sy)
            self.change=True
    
    def Clear(self):
        self.te.Clear()
        self.l=0
        self.c=0
        self.mc=0
        self._UpdateOR()
        sx,sy=self._UpdateCP(self.sx,self.sy)
        self._SetScroll(sx,sy)
        self.change=True
        
    def Left(self,n):
        if n<=0:
            return
        for _ in range(n):
            self.l,self.c=self.te.CLeft(self.l,self.c)
        self.mc=self.c
        sx,sy=self._UpdateCP(self.sx,self.sy)
        self._SetScroll(sx,sy)

    def Right(self,n):
        if n<=0:
            return
        for _ in range(n):
            self.l,self.c=self.te.CRight(self.l,self.c)
        self.mc=self.c
        sx,sy=self._UpdateCP(self.sx,self.sy)
        self._SetScroll(sx,sy)

    def ToBegin(self):
        self.l=0
        self.c=0
        sx,sy=self._UpdateCP(self.sx,self.sy)
        self._SetScroll(sx,sy)

    def ToLB(self):
        self.c=0
        self.mc=self.c
        sx,sy=self._UpdateCP(self.sx,self.sy)
        self._SetScroll(sx,sy)
    
    def ToEnd(self):
        self.l,self.c=self.te.End()
        self.mc=self.c
        sx,sy=self._UpdateCP(self.sx,self.sy)
        self._SetScroll(sx,sy)
    
    def GetText(self,*args):
        return self.te.GetText(*args)
    
    def ShowCursor(self,show):
        self.cursor=show

    def MinW(self):
        return self.fw
    
    def MinH(self):
        return self.fh+self.gap

    def MaxW(self):
        return None
    
    def MaxH(self):
        return None

    def SetOffset(self,ox,oy):
        self.ox=ox
        self.oy=oy

    def SetBox(self,x,y,w,h):
        self.x=x
        self.y=y
        if (w,h)!=(self,w,self.h):
            sxp=self.sx/self.rx if self.rx>0 else 0
            syp=self.sy/self.ry if self.ry>0 else 0
            self.w=w
            self.h=h
            self._UpdateOR()
            self._SetScroll(int(sxp*self.rx),int(syp*self.ry))

    def SetCS(self,cs):
        self.cs=cs

    def Draw(self,fb,win):
        wx0=self.x+self.ox
        wx1=wx0+self.w-1
        wy0=self.y+self.oy
        wy1=wy0+self.h-1
        win=win.I(wx0,wy0,wx1,wy1)
        if win is None:
            return
        fb.Window(win.x0,win.y0,win.x1,win.y1)
        if self.bg:
            fb.FRect(wx0,wy0,self.w,self.h,self.cs.bg_en)
        self.te.Draw(self.f,self.gap,self.cs.fg_en,wx0-self.sx,wy0-self.sy,fb,wx0,wy0,wx1,wy1)
        if self.ry:
            fb.VLine(wx1,wy0,self.h,self.cs.bg_en)
            sb_h=max(round(self.h*self.h/(self.ry+self.h)),1)
            sb_o=round(self.sy/self.ry*(self.h-sb_h))
            fb.VLine(wx1,wy0+sb_o,sb_h,self.cs.fg_en)
        if self.cursor:
            fb.VLine(wx0+self.cx-self.sx,wy0+self.cy-self.sy,self.fh,self.cs.fg_en)

    def OnKBE(self,e,d0,d1):
        te=self.te
        l=self.l
        c=self.c
        tdirty=False
        sx=self.sx
        sy=self.sy
        if e==dev.KBE_DOWN:
            if d1==dev.KSC_CTRL:
                self.ctrl=True
            elif d1==dev.KSC_TAB:
                i=4-c%4
                l,c=te.Insert(l,c," "*i)
                self.mc=c
                tdirty=True
                self.change=True
            elif d1==dev.KSC_BS:
                lb,cb=te.CLeft(l,c)
                if (l,c)!=(lb,cb):
                    self.change=True
                l,c=te.Delete(lb,cb,l,c)
                self.mc=c
                tdirty=True
            elif d1==dev.KSC_ENTER:
                l,c=te.Insert(l,c,"\n")
                self.mc=c
                tdirty=True
                self.change=True
            elif d1==dev.KV_DEL:
                le,ce=te.CRight(l,c)
                if (l,c)!=(le,ce):
                    self.change=True
                l,c=te.Delete(l,c,le,ce)
                self.mc=c
                tdirty=True
            elif d1==dev.KV_UP:
                if l>0:
                    l=l-1
                    c=min(self.mc,len(te.ls[l]))
                    tdirty=True
            elif d1==dev.KV_DOWN:
                if l+1<len(te.ls):
                    l=l+1
                    c=min(self.mc,len(te.ls[l]))
                    tdirty=True
            elif d1==dev.KV_LEFT:
                l,c=te.CLeft(l,c)
                self.mc=c
                tdirty=True
            elif d1==dev.KV_RIGHT:
                l,c=te.CRight(l,c)
                self.mc=c
                tdirty=True
            if self.ctrl:
                if d1==dev.KSC_SEMI:
                    sy-=self.fh+self.gap
                elif d1==dev.KSC_FS:
                    sy+=self.fh+self.gap
                elif d1==dev.KSC_COMMA:
                    sx-=self.fw
                elif d1==dev.KSC_SLASH:
                    sx+=self.fw
        elif e==dev.KBE_UP:
            if d0==dev.KSC_CTRL:
                self.ctrl=False
        elif e==dev.KBE_INPUT:
            if not self.ctrl:
                l,c=te.Insert(l,c,chr(d0))
                self.mc=c
                tdirty=True
                self.change=True
        if tdirty or (sx,sy)!=(self.sx,self.sy):
            if tdirty:
                self.l=l
                self.c=c
                self._UpdateOR()
                sx,sy=self._UpdateCP(sx,sy)
            self._SetScroll(sx,sy)
            return True
        return False

class TLEdit:
    def __init__(self,x,y,w,h,m,cs,f):
        self.en=True
        self.focus=True
        self.grab=False
        self.x=x
        self.y=y
        self.w=w
        self.h=h
        self.m=m
        self.ox=0
        self.oy=0
        self.cs=cs
        self.te=TEdit(x+m,y+m,w-2*m,y-2*m,cs,f,False)
        self.te.ShowCursor(False)
    
    def GetText(self):
        return self.te.GetText(0,0)

    def SetText(self,t):
        self.te.Clear()
        self.te.Insert(t)

    def Clear(self):
        self.te.Clear()

    def MinW(self):
        return self.te.MinW()+2*self.m+2
    
    def MinH(self):
        return self.te.MinH()+2*self.m+2

    def MaxW(self):
        return self.MinW()
    
    def MaxH(self):
        return self.MinH()
    
    def SetEnable(self,en):
        self.en=en

    def SetFocus(self,focus):
        self.focus=focus
    
    def SetBox(self,x,y,w,h):
        self.x=x
        self.y=y
        self.w=w
        self.h=h
        self.te.SetBox(x+self.m+1,y+self.m+1,w-2*(self.m+1),h-2*(self.m+1))
    
    def SetCS(self,cs):
        self.cs=cs
        self.te.SetCS(cs)

    def SetOffset(self,ox,oy):
        self.ox=ox
        self.oy=oy
        self.te.SetOffset(ox,oy)
    
    def SetMargin(self,m):
        self.m=m
        self.te.SetBox(self.x+m+1,self.y+m+1,self.w-2*(m+1),self.h-2*(m+1))
    
    def Draw(self,fb,win):
        wx0=self.x+self.ox
        wx1=wx0+self.w-1
        wy0=self.y+self.oy
        wy1=wy0+self.h-1
        win=win.I(wx0,wy0,wx1,wy1)
        if win is None:
            return
        fb.Window(win.x0,win.y0,win.x1,win.y1)
        if self.focus:
            fb.Rect(wx0,wy0,self.w,self.h,self.cs.fg_en)
        self.te.Draw(fb,win)
    
    def OnKBE(self,e,d0,d1):
        if self.focus:
            if self.grab:
                if e==dev.KBE_DOWN and d1==dev.KSC_ENTER:
                    self.grab=False
                    self.te.ShowCursor(False)
                    return True
            else:
                if e==dev.KBE_DOWN and d1==dev.KSC_ENTER:
                    self.grab=True
                    self.te.ShowCursor(True)
                    return True
        if not self.grab:
            return False
        if e==dev.KBE_DOWN and d1==dev.KSC_ENTER:
            return False
        return self.te.OnKBE(e,d0,d1)