#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import os
import zipfile

zipFileName = 'OPCDA.zip'
zipFilePath = 'src/'

if os.path.isfile(zipFileName):
    os.remove(zipFileName)

OPCDA = zipfile.ZipFile(zipFileName, 'w')

os.chdir(zipFilePath)
curDirPath = './'
if os.path.isdir(curDirPath):
    for root, dirs, files in os.walk(curDirPath):
        for fileName in files:
            OPCDA.write(os.path.join(root, fileName), compress_type=zipfile.ZIP_DEFLATED)
    print("compress OPCDA.zip success...")
else:
    print("compress OPCDA.zip failed, due to %s directory is not exsit", zipFilePath)

OPCDA.close()