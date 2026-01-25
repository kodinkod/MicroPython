# Copyright (C) 2025 Hongyi Chen (BeanPieChen)
# Licensed under the MIT License

from micropython import schedule
from machine import Pin,SPI,SoftI2C,Timer,SDCard,ADC,RTC,PWM
import os
import st7789
import Keyboard

KSC_GRAVE=const(1)
KSC_TAB=const(2)
KSC_FN=const(3)
KSC_CTRL=const(4)
KSC_1=const(5)
KSC_Q=const(6)
KSC_SHIFT=const(7)
KSC_OPT=const(8)
KSC_2=const(11)
KSC_W=const(12)
KSC_A=const(13)
KSC_ALT=const(14)
KSC_3=const(15)
KSC_E=const(16)
KSC_S=const(17)
KSC_Z=const(18)
KSC_4=const(21)
KSC_R=const(22)
KSC_D=const(23)
KSC_X=const(24)
KSC_5=const(25)
KSC_T=const(26)
KSC_F=const(27)
KSC_C=const(28)
KSC_6=const(31)
KSC_Y=const(32)
KSC_G=const(33)
KSC_V=const(34)
KSC_7=const(35)
KSC_U=const(36)
KSC_H=const(37)
KSC_B=const(38)
KSC_8=const(41)
KSC_I=const(42)
KSC_J=const(43)
KSC_N=const(44)
KSC_9=const(45)
KSC_O=const(46)
KSC_K=const(47)
KSC_M=const(48)
KSC_0=const(51)
KSC_P=const(52)
KSC_L=const(53)
KSC_COMMA=const(54)
KSC_MINUS=const(55)
KSC_LSB=const(56)
KSC_SEMI=const(57)
KSC_FS=const(58)
KSC_EQUAL=const(61)
KSC_RSB=const(62)
KSC_APOS=const(63)
KSC_SLASH=const(64)
KSC_BS=const(65)
KSC_BSLASH=const(66)
KSC_ENTER=const(67)
KSC_SPACE=const(68)

KV_ESC=const(101)
KV_DEL=const(102)
KV_UP=const(103)
KV_DOWN=const(104)
KV_LEFT=const(105)
KV_RIGHT=const(106)

KBE_DOWN=const(0)
KBE_UP=const(1)
KBE_INPUT=const(2)

KR_TRIGGER=const(300)
KR_INTERVAL=const(80)

DP_WIDTH=const(240)
DP_HEIGHT=const(135)

_k_ch_map=(
    b'`~\x00\x00\x00\x00\x00\x001!qQ\x00\x00\x00\x00',
    b'2@wWaA\x00\x003#eEsSzZ',
    b'4$rRdDxX5%tTfFcC',
    b'6^yYgGvV7&uUhHbB',
    b'8*iIjJnN9(oOkKmM',
    b'0)pPlL,<_-[{;:.>',
    b'=+]}\'\"/?\x00\x00\\|\x00\x00  '
)

_kv_map=[
    [KSC_GRAVE,KV_ESC],
    [KSC_BS,KV_DEL],
    [KSC_SEMI,KV_UP],
    [KSC_COMMA,KV_LEFT],
    [KSC_FS,KV_DOWN],
    [KSC_SLASH,KV_RIGHT]
]

_batt_adc=None
_spi=None
_i2c=None
_dp=None
_fb=None
_kb=None
_kbls=[]
_con_k_c=[KSC_FN,KSC_CTRL,KSC_SHIFT,KSC_OPT,KSC_ALT]
_con_k_down=[False,False,False,False,False]
_kr=None
_kr_mod=None
_krt=None
_bld=[512,614,716,818,921,1023]
_bl=5
_pwm=None

def _TellKBLS(e,d0,d1):
    global _kbls
    for l in _kbls:
        l.on_kbe(e,d0,d1)

def _HandleKIN(ksc):
    global _k_ch_map
    global _con_k_down
    if _con_k_down[0]:
        return
    r,c=_GetKeyRC(ksc)
    ch=_k_ch_map[r][c*2+(1 if _con_k_down[2] else 0)]
    if ch!=0:
        _TellKBLS(KBE_INPUT,ch,None)

def _OnKR(t):
    global _kr
    global _kr_mod
    if _kr:
        _TellKBLS(KBE_DOWN,_kr,_kr_mod)
        _HandleKIN(_kr)
    else:
        t.deinit()

def _OnKRTimer(t):
    global _kr
    if _kr:
        t.init(mode=Timer.PERIODIC,period=KR_INTERVAL,callback=_OnKR)
    else:
        t.deinit()

def _SetKRTimer(ksc,kv):
    global _kr
    global _kr_mod
    if kv==KV_ESC:
        return
    _kr=ksc
    _kr_mod=kv
    _krt.init(mode=Timer.ONE_SHOT,period=KR_TRIGGER,callback=_OnKRTimer)

def _CancleKRTimer():
    global _kr
    global _kr_mod
    _krt.deinit()
    _kr=None
    _kr_mod=None

def _GetKeyRC(ksc):
    ksc-=1
    return int(ksc/10),ksc%10

def _OnKeyChange(is_down,ksc):
    global _kb
    global _con_k_c
    global _con_k_down
    global _kv_map
    is_con=False
    for i in range(len(_con_k_c)):
        if ksc==_con_k_c[i]:
            _con_k_down[i]=is_down
            is_con=True
            break
    k_mod=ksc
    if _con_k_down[0]:
        for kv in _kv_map:
            if kv[0]==ksc:
                k_mod=kv[1]
                break
    if is_down:
        _TellKBLS(KBE_DOWN,ksc,k_mod)
        _CancleKRTimer()
        if not is_con:
            _SetKRTimer(ksc,k_mod)
            _HandleKIN(ksc)
    else:
        _CancleKRTimer()
        _TellKBLS(KBE_UP,ksc,None)

def _OnKI(a):
    global _kb
    try:
        while _kb.GetKEN():
            is_down,ksc=_kb.ReadKE()
            _OnKeyChange(is_down,ksc)
        _kb.Flush()
    except Exception:
        _kb.Flush()
        raise

def KIRQ(pin):
    schedule(_OnKI,None)

def _Init():
    global _batt_adc
    global _spi
    global _i2c
    global _dp
    global _fb
    global _kb
    global _krt
    global _pwm
    global _bld
    global _bl
    _batt_adc=ADC(10)
    try:
        sd=SDCard(slot=3,cs=Pin(12),mosi=Pin(14),sck=Pin(40),miso=Pin(39))
        os.mount(sd,'/sd')
    except:
        pass

    _spi = SPI(
        2,
        baudrate=40000000,
        sck=Pin(36,Pin.OUT),
        mosi=Pin(35,Pin.OUT),
        miso=None
        )

    _i2c=SoftI2C(scl=Pin(9),sda=Pin(8),freq=400000)

    _dp = st7789.ST7789(
        _spi,
        DP_HEIGHT, DP_WIDTH,
        reset=Pin(33, Pin.OUT),
        dc=Pin(34, Pin.OUT),
        cs=Pin(37, Pin.OUT),
        rotation=1
        )

    _dp.init()

    _pwm=PWM(Pin(38,Pin.OUT))
    _pwm.freq(1000)
    _pwm.duty(_bld[_bl])

    _fb=st7789.FB(DP_WIDTH,DP_HEIGHT)

    _kb=Keyboard.Keyboard(_i2c,7,8,11,0x34)
    _krt=Timer(0)
    _kb.SetKIH(KIRQ)

def batt_uv():
    global _batt_adc
    return _batt_adc.read_uv()/1000000

def add_kbl(l):
    global _kbls
    _kbls.append(l)
    
def remove_kbl(l):
    global _kbls
    _kbls.remove(l)

DPC_X=st7789.BLACK
DPC_W=st7789.WHITE
DPC_R=st7789.RED
DPC_G=st7789.GREEN
DPC_B=st7789.BLUE
DPC_C=st7789.CYAN
DPC_Y=st7789.YELLOW
DPC_M=st7789.MAGENTA
DPC_GR=st7789.color565(127,127,127)
DPC_DR=st7789.color565(127,0,0)
DPC_DG=st7789.color565(0,127,0)
DPC_DB=st7789.color565(0,0,127)
DPC_DC=st7789.color565(0,127,127)
DPC_DY=st7789.color565(127,127,0)
DPC_DM=st7789.color565(127,0,127)
DPC_OR=st7789.color565(255,127,0)
DPC_PU=st7789.color565(192,0,255)
DPC_DOR=st7789.color565(127,64,0)
DPC_DPU=st7789.color565(96,0,127)

def dp_bl(on):
    global _dp
    _dp.on() if on else _dp.off()
    
def dp_sleep(s):
    global _dp
    _dp.sleep_mode(s)

def dp_window(x0,y0,x1,y1):
    global _dp
    _dp.set_window(x0,y0,x1,y1)

def fb_window(x0,y0,x1,y1):
    global _fb
    _fb.set_window(x0,y0,x1,y1)

def dp_fill(c):
    global _dp
    _dp.fill(c)

def fb_fill(c):
    global _fb
    _fb.fill(c)

def dp_pix(x,y,c):
    global _dp
    _dp.pixel(x,y,c)

def fb_pix(x,y,c):
    global _fb
    _fb.set_pixel(x,y,c)
    
def dp_line(x0,y0,x1,y1,c):
    global _dp
    _dp.line(x0,y0,x1,y1,c)

def fb_line(x0,y0,x1,y1,c):
    global _fb
    _fb.line(x0,y0,x1,y1,c)

def dp_hline(x,y,l,c):
    global _dp
    _dp.hline(x,y,l,c)

def fb_hline(x,y,l,c):
    global _fb
    _fb.hline(x,y,l,c)

def dp_vline(x,y,l,c):
    global _dp
    _dp.vline(x,y,l,c)

def fb_vline(x,y,l,c):
    global _fb
    _fb.vline(x,y,l,c)

def dp_rect(x,y,w,h,c):
    global _dp
    _dp.rect(x,y,w,h,c)

def fb_rect(x,y,w,h,c):
    global _fb
    _fb.rect(x,y,w,h,c)

def dp_frect(x,y,w,h,c):
    global _dp
    _dp.fill_rect(x,y,w,h,c)

def fb_frect(x,y,w,h,c):
    global _fb
    _fb.fill_rect(x,y,w,h,c)

def dp_circle(x,y,r,c):
    global _dp
    _dp.circle(x,y,r,c)

def fb_circle(x,y,r,c):
    global _fb
    _fb.circle(x,y,r,c)

def dp_fcircle(x,y,r,c):
    global _dp
    _dp.fill_circle(x,y,r,c)

def fb_fcircle(x,y,r,c):
    global _fb
    _fb.fill_circle(x,y,r,c)
    
def dp_polygon(*args):
    global _dp
    _dp.polygon(*args)

def fb_polygon(*args):
    global _fb
    _fb.polygon(*args)

def dp_fpolygon(*args):
    global _dp
    _dp.fill_polygon(*args)

def fb_fpolygon(*args):
    global _fb
    _fb.fill_polygon(*args)

def dp_text(f,s,x,y,fg=DPC_W,bg=DPC_X):
    global _dp
    _dp.text(f,s,x,y,fg,bg)

def fb_text(*args):
    global _fb
    _fb.text(*args)

def dp_blit(fb,x,y,w,h):
    global _dp
    _dp.blit_buffer(fb,x,y,w,h)

def fb_present():
    global _dp
    global _fb
    _dp.blit_buffer(_fb,0,0,DP_WIDTH,DP_HEIGHT)

def rgb565(r,g,b):
    return st7789.color565(r,g,b)