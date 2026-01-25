# Copyright (C) 2025 Hongyi Chen (BeanPieChen)
# Licensed under the MIT License

from machine import Pin

R_CFG=const(0x01)             # Configuration register
R_INT_STAT=const(0x02)        # Interrupt status
R_KEY_LCK_EC=const(0x03)      # Key lock and event counter
R_KEY_EVENT_A=const(0x04)     # Key event register A
R_KP_GPIO_1=const(0x1D)       # Keypad/GPIO select 1
R_KP_GPIO_2=const(0x1E)       # Keypad/GPIO select 2
R_KP_GPIO_3=const(0x1F)       # Keypad/GPIO select 3

class Keyboard:
    def __init__(self,i2c,r,c,int_pin,addr=0x34):
        self.i2c=i2c
        self.addr=addr
        self.b=bytearray(1)
        self._Matrix(r,c)
        self._WriteR(R_CFG,0x01)
        self.Flush()
        self.p_int=Pin(int_pin,Pin.IN)

    def _WriteR(self,r,v):
        self.b[0]=v
        self.i2c.writeto_mem(self.addr,r,self.b)

    def _ReadR(self,r):
        return self.i2c.readfrom_mem(self.addr,r,1)[0]
            
    def _Matrix(self,r,c):
        if (r > 8) or (c > 10):
            return False
        # MATRIX
        # skip zero size matrix
        if (r != 0) and (c != 0):
            # setup the keypad matrix.
            m=0x00
            for _ in range(r):
                m <<= 1
                m |= 1
            self._WriteR(R_KP_GPIO_1,m)

            m=0x00
            i=0
            while i < c and i < 8:
                m <<= 1
                m |= 1
                i=i+1
            self._WriteR(R_KP_GPIO_2,m)

            if c > 8:
                if c==9:
                    m = 0x01
                else:
                    m = 0x03
                self._WriteR(R_KP_GPIO_3,m)
        return True

    def Flush(self):
        while self._ReadR(R_KEY_LCK_EC)&0x0F:
            self._ReadR(R_KEY_EVENT_A)
        self._WriteR(R_INT_STAT,0x1)
    
    def GetKEN(self):
        return self._ReadR(R_KEY_LCK_EC)&0x0F
    
    def ReadKE(self):
        e=self._ReadR(R_KEY_EVENT_A)
        is_down=False
        if e>>7:
            is_down=True
        return is_down,e&0x7F
    
    def SetKIH(self,f):
        self.p_int.irq(f)