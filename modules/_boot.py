import gc
import vfs
from flashbdev import bdev

try:
    if bdev:
        vfs.mount(bdev, "/")
except OSError:
    import inisetup

    inisetup.setup()

import os
from os import mkdir,rename,rmdir
import dev
import shell

def ls(path=None):
    ret=None
    if path:
        ret=os.listdir(path)
    else:
        ret=os.listdir()
    if path:
        if path[-1]!=os.sep:
            path+=os.sep
    for e in ret:
        if os.stat(path+e if path else e)[0]&0x4000:
            print("d "+e)
        else:
            print("  "+e)


def cd(path):
    os.chdir(path)

def cwd():
    print(os.getcwd())

def rm(path):
    os.remove(path)

def run(path):
    with open(path,"r") as f:
        exec(f.read())

def edit(path=None):
    shell._OpenEditor(path)

def batt():
    print(str(dev.batt_uv())+"V")

dev._Init()
shell._Init()

gc.collect()
