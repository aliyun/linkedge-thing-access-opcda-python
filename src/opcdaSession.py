#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import logging
import threading
import open_opc.OpenOPC as OpenOPC
from open_opc.OpenOPC import *

from common.thread import createThread
import lethingaccesssdk
import opcdaConfig
from opcdaDevice import *

_logger = logging.getLogger()

class OpcdaSession(object):
    def __init__(self, serverConfig=None, deviceConfig=None):
        self.serverConfig       = serverConfig
        self.deviceConfig       = deviceConfig

        self.opcProxyIp         = serverConfig["opcProxyIp"]
        self.opcProxyPort       = serverConfig["opcProxyPort"]
        self.opcServerName      = serverConfig["opcServer"]
        self.opcServerIp        = 'localhost'

        self.collectInterval    = opcdaConfig.OPC_COLLECT_INTERVAL
        if "collectInterval" in serverConfig:
            self.collectInterval= serverConfig["collectInterval"]

        self.opcdaClient        = None
        self.state              = False
        self.stateLock          = threading.Lock()

        self.onlineDeviceList   = []
        self.onlineDeviceLock   = threading.Lock()

        self.offlineDeviceList  = []
        self.offlineDeviceLock  = threading.Lock()

        self.debugMode          = False

        createThread(self.loopPollData)

    def setState(self, state):
        self.stateLock.acquire()
        self.state = state
        self.stateLock.release()

    def getState(self):
        self.stateLock.acquire()
        state = self.state
        self.stateLock.release()

        return state

    def isAlive(self):
        if self.opcdaClient:
            if self.opcdaClient.ping():
                return True
            else:
                return False

        return False

    def connect(self):
        if self.getState():
            return True

        try:
            self.opcdaClient = open_client(self.opcProxyIp, self.opcProxyPort)
        except Exception as e:
            _logger.exception("exception %s happen when connect opc proxy(%s:%d)" % (e, self.opcProxyIp, self.opcProxyPort))
            return False
        else:
            _logger.info("connect opc proxy(%s:%d) success" % (self.opcProxyIp, self.opcProxyPort))

        try:
            self.opcdaClient.connect(self.opcServerName, self.opcServerIp)
        except Exception as e:
            _logger.exception("exception %s happen when connect opc server(%s)" % (e, self.opcServerName))
            return False
        else:
            _logger.info("connect opc server(%s) success" % (self.opcServerName))

        try:
            proxyInfo = self.opcdaClient.info()
        except Exception as e:
            _logger.exception("exception %s happen when get opc proxy info" % e)
        else:
            _logger.info("opc proxy info(%s)" % (proxyInfo))
        
        try:
            serverInfo = self.opcdaClient.servers(self.opcServerIp)
        except Exception as e:
            _logger.exception("exception %s happen when get opc server info" % e)
        else:
            _logger.info("opc server info(%s)" % (serverInfo))

        self.setState(True)

        return True

    def disconnect(self):
        if self.getState():
            self.offlineDevices()
            try:
                self.opcdaClient.close()
            except Exception as e:
                _logger.exception("exception %s happen when disconnect with opc server(%s)" % (e, self.opcServerName))
            self.setState(False)

        return

    def onlineDevices(self):
        for config in self.deviceConfig:
            device = OpcdaDevice(self, config)
            if device.registerDevice():
                _logger.info("online device(%s)" % (config["custom"]["devicePath"]))
                self.onlineDeviceLock.acquire()
                self.onlineDeviceList.append(device)
                self.onlineDeviceLock.release()
            else:
                _logger.warning("online device(%s) failed" % (config["custom"]["devicePath"]))
                self.offlineDeviceLock.acquire()
                self.offlineDeviceList.append(device)
                self.offlineDeviceLock.release()

        return

    def reOnlineDevices(self):
        self.offlineDeviceLock.acquire()
        for device in self.offlineDeviceList:
            if device.registerDevice():
                _logger.info("reonline device(%s)" % (device.deviceName))
                self.offlineDeviceList.remove(device)

                self.onlineDeviceLock.acquire()
                self.onlineDeviceList.append(device)
                self.onlineDeviceLock.release()
            else:
                _logger.warning("reonline device(%s) failed" % (device.deviceName))
        self.offlineDeviceLock.release()

        return

    def offlineDevices(self):
        self.onlineDeviceLock.acquire()
        for device in self.onlineDeviceList:
            _logger.info("offline device(%s)" % (device.deviceName))
            device.offlineDevice()
            self.onlineDeviceList.remove(device)
        self.onlineDeviceLock.release()

        self.offlineDeviceLock.acquire()
        self.offlineDeviceList = []
        self.offlineDeviceLock.release()

        return

    def getItemList(self, path='*', recursive=False, flat=False):
        return self.opcdaClient.list(path, recursive, flat)

    def read(self, tags, func):
        result = []
        result = self.opcdaClient.read(tags, sync=func, include_error=self.debugMode)
        if self.debugMode:
            _logger.debug("the result is %s when request read opcda device" % (result,))
        return result

    def write(self, tag_value_pairs):
        status = None
        status = self.opcdaClient.write(tag_value_pairs, include_error=self.debugMode)
        if self.debugMode:
            _logger.debug("the status is %s when request write opcda device" % (status,))
        return status

    def loopPollData(self):
        while True:
            collectBeginTimestamp = 0
            collectEndTimestamp   = 0
            collectCostTime       = 0

            self.onlineDeviceLock.acquire()
            collectBeginTimestamp = time.time()
            for device in self.onlineDeviceList:
                if not device.deviceItemList:
                    continue

                resultList = []
                for i in range(opcdaConfig.OPEN_OPC_RETRY_NUMBER):
                    try:
                        resultList = self.opcdaClient.read(device.deviceItemList, 
                                                            group=device.deviceName,
                                                            source=opcdaConfig.OPC_DATA_SOURCE_HYBRID,
                                                            update=opcdaConfig.OPC_GROUPS_UPDATE_RATE,
                                                            timeout=opcdaConfig.OPEN_OPC_READ_TIME_OUT,
                                                            sync=opcdaConfig.OPEN_OPC_ASYNC_READ,
                                                            include_error=self.debugMode)
                    except Exception as e:
                        _logger.exception("exception %s happen when read device(%s) items(%s)" % (e, device.deviceName, device.deviceItemList))
                        continue

                    if resultList:
                        if self.debugMode:
                            _logger.debug("the result is %s when request read opcda device" % (resultList,))
                        device.reportProperties(resultList)
                        break
                    else:
                        continue
                else:
                    try:
                        self.opcdaClient.remove(device.deviceName)
                    except Exception as e:
                        _logger.exception("exception %s happen when remove device group (%s) items(%s)" % (e, device.deviceName, device.deviceItemList))

                    device.offlineDevice()
                    self.onlineDeviceList.remove(device)
                    
                    self.offlineDeviceLock.acquire()
                    self.offlineDeviceList.append(device)
                    self.offlineDeviceLock.release()
            collectEndTimestamp = time.time()
            self.onlineDeviceLock.release()

            collectCostTime = (collectEndTimestamp - collectBeginTimestamp)
            if self.collectInterval > collectCostTime:
                time.sleep(self.collectInterval - collectCostTime)
            else:
                _logger.warning("the collectInterval(%d) is not enough, should be or be more than %d" % (self.collectInterval, collectCostTime))
        return