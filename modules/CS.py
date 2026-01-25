# Copyright (C) 2025 Hongyi Chen (BeanPieChen)
# Licensed under the MIT License

import dev

class CS:
    def __init__(self,fg_dis,bg_dis,fg_en,bg_en,fg_hl,bg_hl,fg_dim,bg_dim):
        self.fg_dis=fg_dis
        self.bg_dis=bg_dis
        self.fg_en=fg_en
        self.bg_en=bg_en
        self.fg_hl=fg_hl
        self.bg_hl=bg_hl
        self.fg_dim=fg_dim
        self.bg_dim=bg_dim
    
    def E(self,en):
        if en:
            return self.fg_en,self.bg_en
        else:
            return self.fg_dis,self.bg_dis
    
    def EF(self,en,focus):
        if not en:
            return self.fg_dis,self.bg_dis
        else:
            if focus:
                return self.fg_hl,self.bg_hl
            else:
                return self.fg_en,self.bg_en
    
    def EFD(self,en,focus,down):
        if not en:
            return self.fg_dis,self.bg_dis
        else:
            if focus:
                if down:
                    return self.fg_dim,self.bg_dim
                else:
                    return self.fg_hl,self.bg_hl
            else:
                return self.fg_en,self.bg_en

WHITE=CS(dev.DPC_GR,dev.DPC_X,dev.DPC_W,dev.DPC_X,dev.DPC_X,dev.DPC_W,dev.DPC_X,dev.DPC_GR)
GREEN=CS(dev.DPC_DG,dev.DPC_X,dev.DPC_G,dev.DPC_X,dev.DPC_X,dev.DPC_G,dev.DPC_X,dev.DPC_DG)
ORANGE=CS(dev.DPC_DOR,dev.DPC_X,dev.DPC_OR,dev.DPC_X,dev.DPC_X,dev.DPC_OR,dev.DPC_X,dev.DPC_DOR)
CYAN=CS(dev.DPC_DC,dev.DPC_X,dev.DPC_C,dev.DPC_X,dev.DPC_X,dev.DPC_C,dev.DPC_X,dev.DPC_DC)
PURPLE=CS(dev.DPC_DPU,dev.DPC_X,dev.DPC_PU,dev.DPC_X,dev.DPC_X,dev.DPC_PU,dev.DPC_X,dev.DPC_DPU)
YELLOW=CS(dev.DPC_DY,dev.DPC_X,dev.DPC_Y,dev.DPC_X,dev.DPC_X,dev.DPC_Y,dev.DPC_X,dev.DPC_DY)
RED=CS(dev.DPC_DR,dev.DPC_X,dev.DPC_R,dev.DPC_X,dev.DPC_X,dev.DPC_R,dev.DPC_X,dev.DPC_DR)