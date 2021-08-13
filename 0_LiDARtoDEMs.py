from __future__ import print_function
import os
import sys
sys.path.insert(1, 'Y:/Sidd/WBT') #
import urllib.request
from whitebox_tools import WhiteboxTools

wbt = WhiteboxTools()
wbt.exe_path = 'Y:/Sidd/WBT/'
wbt.verbose = True

#Poland
wbt.work_dir = 'Y:/William/DeepLearning/DitchnetProduction/DitchDataDelivery/Latvia/Latvia_LAS/'
wbt.lidar_tin_gridding(
    i=None,
    output=None,
    parameter='elevation',
    returns='last',
    resolution=0.5,
    exclude_cls='0,1,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18',
    minz=None,
    maxz=None,
    max_triangle_edge_length=None,
    )
