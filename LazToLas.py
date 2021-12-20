from __future__ import print_function
import threading
import os
import sys
import subprocess
import glob


lasdir = 'Y:/William/DeepLearning/Implementation/LiDAR/lasfiles/'

maxThreads = 60      #threads
activeThreads = 0

class workerThread(threading.Thread):
    def __init__(self, indata):
        threading.Thread.__init__(self)
        self.file = indata

    def run(self):
        global activeThreads
        activeThreads += 1

        #################################
        ##### Start here #####
        #################################
        global lasdir
        lasout = lasdir + os.path.basename(self.file)

        try:
            subprocess.call(['Y:/William/DeepLearning/Implementation/code/utils/laszip', '-i', self.file, '-o', lasout.replace('.laz','.las')])
            print('unpacked ', self.file)
        except:
            print('Unexpected error:', sys.exc_info()[0])
            raise
        #################################
        ##### Stop here #####
        #################################

        activeThreads -= 1

listoflazfiles = glob.glob('Y:/William/DeepLearning/Implementation/LiDAR/Laserdata_Skog/**/*.laz', recursive = True)
for file in listoflazfiles:
    worker = workerThread(file).start()
    while activeThreads >= maxThreads:
        pass
