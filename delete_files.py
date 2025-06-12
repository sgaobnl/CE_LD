# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: 5/23/2025 3:52:31 PM
"""

#defaut setting for scientific caculation
#import numpy
#import scipy
#from numpy import *
import numpy as np
#import scipy as sp
#import pylab as pl

import sys 
import os
import string
import time
from datetime import datetime
import pickle
import shutil
import numpy as np


def delete_folder(path):
    """
    Delete the folder at `path` and all its contents.
    Raises FileNotFoundError if path doesn't exist,
    or NotADirectoryError if path isn't a directory.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"No such file or directory: '{path}'")
    if not os.path.isdir(path):
        raise NotADirectoryError(f"Not a directory: '{path}'")

    # Recursively delete everything under `path`, then the folder itself.
    shutil.rmtree(path)
    print(f"Deleted folder and contents: {path}")


srcdir = """H:/SiPM/"""
for root, dirs, files in os.walk(srcdir):
    break

for rawd in dirs:
    if "Result_" in rawd:
        print (rawd)
        for root, dirs, files in os.walk(srcdir+rawd):
            break
        for onedir in dirs:
            print (onedir)
            delete_folder(srcdir+rawd+"/" + onedir)





