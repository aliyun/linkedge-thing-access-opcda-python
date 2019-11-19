#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import sys
import time
import logging
import json
import datetime

import lethingaccesssdk
import opcdaConfig
import opcdaException
import opcdaUtil

_logger = logging.getLogger()

class OpcdaDevice(lethingaccesssdk.ThingCallback):
    def __init__(self, opcdaClient, config):
        self.opcdaClient    = opcdaClient
        self.cloudClient    = lethingaccesssdk.ThingAccessClient(config)

        self.reportType     = opcdaConfig.OPC_REPORT_TYPE_TIMER
        if "reportType" in config["custom"]:
            if config["custom"]["reportType"] == 1:
                self.reportType = opcdaConfig.OPC_REPORT_TYPE_CHANGE

        self.deviceConfig   = config
        self.deviceName     = config["custom"]["devicePath"]

        '''
        {
            "alibaba.aliyun.iot.led.led1.temperature": 
            {
                "identifier": "temperature",
                "itemMode" : "rw",
                "itemType" : "dataType": {
                                "specs": {
                                    "min": "-100",
                                    "max": "1000",
                                    "step": "1"
                                },
                                "type": "int"
                            }
            },
            "alibaba.aliyun.iot.led.led1.power": 
            {
                "identifier": "power",
                "itemMode" : "rw",
                "itemType" : "dataType": {
                                "specs": {
                                    "min": "0",
                                    "max": "1",
                                    "step": "1"
                                },
                                "type": "int"
                            }
            }
        }
        '''
        self.deviceModel = {}

        '''
        {
            "temperature":"alibaba.aliyun.iot.led.led1.temperature"
        }
        '''
        self.identifier2ItemId = {}

        '''
        {
            "alibaba.aliyun.iot.led.led1.temperature":"temperature"
        }
        '''
        self.itemId2Identifier = {}

        self.deviceItemList = []

        '''
        {
            "alibaba.aliyun.iot.led.led1.temperature":
            {
                "itemName" : "temperature",
                "itemValue": 50,
                "itemQuality": "Good",
                "itemTimestamp": 1569554708,
            }
        }
        '''
        self.deviceItemData = {}

    def initDevice(self):
        if not self.deviceModel:
            tsl = self.cloudClient.getTsl()
            extTsl = self.cloudClient.getTslExtInfo()

            if tsl == None or extTsl == None:
                _logger.warning("%s has no tsl or ext tsl" % (self.deviceConfig["productKey"]))
                return False

            tsl = json.loads(tsl)
            extTsl = json.loads(extTsl)
            for tslItem in tsl["properties"]:
                itemIdentifier = tslItem["identifier"]
                for extTslItem in extTsl["properties"]:
                    if itemIdentifier == extTslItem["identifier"]:
                        itemName = extTslItem["customize"]["itemName"]
                        break
                else:
                    _logger.warning("%s is not exist in ext tsl %s" % (itemIdentifier, extTsl["properties"]))
                    continue

                itemMode = tslItem["accessMode"]
                itemType = tslItem["dataType"]

                itemPath = self.deviceName + '.' + itemName
                self.deviceModel[itemPath] = {
                    "identifier": itemIdentifier,
                    "itemMode": itemMode,
                    "itemType": itemType
                }
            else:
                if not self.deviceModel:
                    _logger.warning("tsl is no matched with ext tsl")
                    return False
                else:
                    for key, value in self.deviceModel.items():
                        self.itemId2Identifier[key] = value["identifier"]
                        self.identifier2ItemId[value["identifier"]] = key
        itemList = []
        try:
            path = self.deviceName + '.*'
            itemList = self.opcdaClient.getItemList(path, flat=True)
        except Exception as e:
            _logger.exception("exception %s happen when get device(%s) items" % (e, self.deviceName))
        finally:
            if not itemList:
                _logger.warning("get itemid failed from device %s in opc server" % (self.deviceName))
                return False

        isMatch = False
        for item in self.deviceModel.keys():
            if item in itemList:
                if not isMatch:
                    isMatch = True
                self.deviceItemList.append(item)
                continue
            else:
                _logger.warning("itemId %s is not exist in opc server" % item)
        else:
            if not isMatch:
                _logger.warning("device %s is not exist in opc server" % (self.deviceName))
                return False

        return True

    def registerDevice(self):
        if self.initDevice():
            result = None
            try:
                result = self.cloudClient.registerAndOnline(self)
            except Exception as e:
                _logger.exception("exception %s happen when online device(%s)" % (e, self.deviceName))
            finally:
                return result
        return None

    def onlineDevice(self):
        if self.cloudClient:
            try:
                self.cloudClient.online()
            except Exception as e:
                _logger.exception("exception %s happen when online device(%s)" % (e, self.deviceName))
        return
    
    def offlineDevice(self):
        if self.cloudClient:
            try:
                self.cloudClient.offline()
            except Exception as e:
                _logger.exception("exception %s happen when offline device(%s)" % (e, self.deviceName))
        return

    def checkItemData(self, itemData):
        if not isinstance(itemData, list):
            return False

        if itemData[0] not in self.deviceModel:
            return False

        if itemData[2] != opcdaConfig.OPC_QUALITY_GOOD:
            return False

        if not opcdaUtil.checkOpcdaDataType(self.deviceModel[itemData[0]]["itemType"], self.deviceModel[itemData[0]]["identifier"], itemData[1]):
            return False

        '''
        timestamp = time.mktime(time.strptime(itemData[3], "%Y-%m-%d %H:%M:%S+00:00"))
        '''

        return True

    def itemDataHaveChange(self, newData, oldData):
        isChange = False
        if isinstance(newData, (bool, int, float, str)):
            if newData != oldData:
                isChange = True
        elif isinstance(newData, (list, tuple)):
            if len(newData) == len(oldData):
                for i in range(len(newData)):
                    isChange = self.itemDataHaveChange(newData[i], oldData[i])
                    if isChange:
                        break
            else:
                isChange = True

        return isChange

    def itemData2cloudData(self, itemDataList=[]):
        '''
        origin data format:
        [
            ('alibaba.aliyun.iot.led.led1.temperature', 90, 'Good', '09/27/19 11:45:48')
        ]
        
        protocol data format:
        {
            "temperature" : 90
        }
        '''

        result = {}
        if len(itemDataList) == 0:
            return result

        for itemData in itemDataList:
            if isinstance(itemData, tuple) and len(itemData) >= 4:
                itemData = list(itemData)
                if isinstance(itemData[1], bool):
                    if itemData[1]:
                        itemData[1] = 1
                    else:
                        itemData[1] = 0
                else:
                    pass

                if self.checkItemData(itemData):
                    result[self.itemId2Identifier[itemData[0]]] = itemData[1]
                    self.deviceItemData[itemData[0]] = {
                        "itemName" : self.itemId2Identifier[itemData[0]],
                        "itemValue": itemData[1],
                        "itemQuality": itemData[2],
                        "itemTimestamp": time.mktime(time.strptime(itemData[3], "%Y-%m-%d %H:%M:%S+00:00"))
                    }
                else:
                    _logger.warning("item data (%s) is invalid" % (itemData,))
            else:
                _logger.warning("item data (%s) is invalid" % (itemData,))

        return result

    def checkCloudData(self, itemDataList):
        if len(itemDataList) == 0:
            return False

        if isinstance(itemDataList, list):
            for itemData in itemDataList:
                if itemData in self.identifier2ItemId:
                    if self.deviceModel[self.identifier2ItemId[itemData]]["itemMode"] == opcdaConfig.OPC_ACCESS_MODE_R or self.deviceModel[self.identifier2ItemId[itemData]]["itemMode"] == opcdaConfig.OPC_ACCESS_MODE_RW:
                        continue
                    else:
                        return False
                else:
                    return False
            else:
                return True
        elif isinstance(itemDataList, dict):
            for key, value in itemDataList.items():
                if key in self.identifier2ItemId:
                    if self.deviceModel[self.identifier2ItemId[key]]["itemMode"] == opcdaConfig.OPC_ACCESS_MODE_W or self.deviceModel[self.identifier2ItemId[key]]["itemMode"] == opcdaConfig.OPC_ACCESS_MODE_RW:
                        if opcdaUtil.checkOpcdaDataType(self.deviceModel[self.identifier2ItemId[key]]["itemType"], key, value):
                            continue
                        else:
                            return False
                    else:
                        return False
                else:
                    return False
            else:
                return True

        return False

    def reportProperties(self, itemDataList=[]):
        if not self.cloudClient:
            _logger.warning("device %s is no online" % self.deviceName)
            return
        elif not len(itemDataList):
            _logger.warning("report data is None")
            return

        for itemData in itemDataList:
            if isinstance(itemData, tuple) and len(itemData) == 4:
                if self.reportType == opcdaConfig.OPC_REPORT_TYPE_CHANGE:
                    if self.deviceItemData and itemData[0] in self.deviceItemData:
                        if isinstance(itemData[1], bool):
                            if itemData[1]:
                                data = 1
                            else:
                                data = 0
                        else:
                            data = itemData[1]

                        if not self.itemDataHaveChange(data, self.deviceItemData[itemData[0]]["itemValue"]):
                            itemDataList.remove(itemData)
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
            else:
                itemDataList.remove(itemData)

        result = {}
        result = self.itemData2cloudData(itemDataList)
        if len(result) == 0:
            return

        self.cloudClient.reportProperties(result)
        return

    def reportEvent(self, eventName, eventData):
        _logger.info("report event %s with data %s" % (eventName, eventData))
        return

    def getProperties(self, properNameList):
        _logger.info("cloud request call get with parameters %s" % (properNameList))
        if not self.checkCloudData(properNameList):
            return opcdaException.LE_ERROR_INVAILD_PARAM, {}

        itemIdList = []
        for propertyName in properNameList:
            if propertyName in self.identifier2ItemId:
                itemIdList.append(self.identifier2ItemId[propertyName])
            else:
                return opcdaException.LE_ERROR_INVAILD_PARAM, {}
        else:
            if len(itemIdList) == 0:
                return opcdaException.LE_ERROR_INVAILD_PARAM, {}

        for i in range(opcdaConfig.OPEN_OPC_RETRY_NUMBER):
            try:
                itemDataList = self.opcdaClient.read(itemIdList, True)
            except Exception as e:
                _logger.exception("exception %s happen when read device(%s) items(%s)" % (e, self.deviceName, itemIdList))
                continue
            else:
                break
        else:
            return opcdaException.LE_ERROR_FAILED, {}

        result = {}
        result = self.itemData2cloudData(itemDataList)
        if len(result) == 0:
            return opcdaException.LE_ERROR_FAILED, result

        return opcdaException.LE_SUCCESS, result

    def setProperties(self, properPairList):
        _logger.info("cloud request call set with parameters %s" % (properPairList))
        if not self.checkCloudData(properPairList):
            return opcdaException.LE_ERROR_INVAILD_PARAM, {}

        itemIdList = []
        for key, value in properPairList.items():
            if key in self.identifier2ItemId:
                itemIdList.append((self.identifier2ItemId[key], value))
            else:
                return opcdaException.LE_ERROR_INVAILD_PARAM, {}
        else:
            if len(itemIdList) == 0:
                return opcdaException.LE_ERROR_INVAILD_PARAM, {}

        status = None
        for i in range(opcdaConfig.OPEN_OPC_RETRY_NUMBER):
            try:
                status = self.opcdaClient.write(itemIdList)
            except Exception as e:
                _logger.exception("exception %s happen when write device(%s) items(%s)" % (e, self.deviceName, itemIdList))
                continue
            else:
                break
        else:
            _logger.warning("it's failed when try write device(%s) items(%s) in 3 times" % (e, self.deviceName, itemIdList))
            return opcdaException.LE_ERROR_FAILED, {}

        if isinstance(status, list):
            for s in status:
                if isinstance(s, tuple):
                    if not s.count('Success'):
                        return opcdaException.LE_ERROR_FAILED, {}
                else:
                    return opcdaException.LE_ERROR_FAILED, {}
        elif isinstance(status, tuple):
            if not status.count('Success'):
                return opcdaException.LE_ERROR_FAILED, {}
        else:
            return opcdaException.LE_ERROR_FAILED, {}

        return opcdaException.LE_SUCCESS, {}

    def callService(self, name, parameters):
        _logger.info("cloud request call %s with parameters %s" % (name, parameters))
        return opcdaException.LE_SUCCESS, {}
