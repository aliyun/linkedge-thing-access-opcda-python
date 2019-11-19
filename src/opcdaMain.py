#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import logging

import lethingaccesssdk
import opcdaUtil
from opcdaSession import *
from opcdaMonitor import *

_logger = logging.getLogger()

serverConfig = None
deviceConfig = []

def getDeviceConfigInServer(server):
    deviceList = []
    global deviceConfig
    for config in deviceConfig:
        if config["custom"]["serverId"] == server["serverId"]:
            deviceList.append(config)
        else:
            continue

    return deviceList

def run():
    global serverConfig
    global deviceConfig

    serverConfig = lethingaccesssdk.Config().getDriverInfo()
    deviceConfig = lethingaccesssdk.Config().getThingInfos()

    if "json" in serverConfig:
        if "opcServerList" in serverConfig["json"]:
            serverConfig = serverConfig["json"]["opcServerList"]
        else:
            return
    else:
        return

    if not opcdaUtil.checkOpcdaConfig(serverConfig, deviceConfig):
        _logger.warning("due to config %s is invalid, opcda driver will exit" % (lethingaccesssdk.getConfig()))
        return
    else:
        _logger.info("opcda driver starting...")
        opcda_monitor = OpcdaMonitor()
        for server in serverConfig:
            opcda_session = OpcdaSession(server, getDeviceConfigInServer(server))
            opcda_monitor.addSession(opcda_session)

    while True:
        opcda_monitor.Monitor()

    opcda_monitor.destroySessions()
    _logger.warning("opcda driver exiting...")

    return