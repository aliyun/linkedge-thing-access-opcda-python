#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import sys

sys.path.append("./site-packages/")

import opcdaMain

opcdaMain.run()

def handler(event, context):
    # opcda startup entry in FC Base
    return "Startup opcda drvier"
