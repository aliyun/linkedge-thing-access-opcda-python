#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import os
import sys
import logging
import re
import json

from opcdaException import *

_logger = logging.getLogger()

def checkOpcdaDataType(dataType, key, value):
    if (dataType["type"] == "int"):
        if (not isinstance(value, (int))):
            _logger.warning("%s type is int but value(%s) is not int" % (key, value))
            return False
        else:
            if (("specs" in dataType) and dataType["specs"]):
                if (("min" in dataType["specs"]) and (value < int(dataType["specs"]["min"]))):
                    _logger.warning("%s type is int but value(%s) is not in range %s" % (key, value, dataType["specs"]))
                    return False

                if (("max" in dataType["specs"]) and (value > int(dataType["specs"]["max"]))):
                    _logger.warning("%s type is int but value(%s) is not in range %s" % (key, value, dataType["specs"]))
                    return False

    elif (dataType["type"] == "float" or dataType["type"] == "double"):
        if (not isinstance(value, (float, int))):
            _logger.warning("%s type is float but value(%s) is not float" % (key, value))
            return False
        else:
            if (("specs" in dataType) and dataType["specs"]):
                if (("min" in dataType["specs"]) and (value < float(dataType["specs"]["min"]))):
                    _logger.warning("%s type is float but value(%s) is not in range %s" % (key, value, dataType["specs"]))
                    return False

                if (("max" in dataType["specs"]) and (value > float(dataType["specs"]["max"]))):
                    _logger.warning("%s type is float but value(%s) is not in range %s" % (key, value, dataType["specs"]))
                    return False

    elif (dataType["type"] == "bool"):
        if (str(value) not in dataType["specs"]):
            _logger.warning("%s type is bool but value(%s) is not bool" % (key, value))
            return False

    elif (dataType["type"] == "enum"):
        if (str(value) not in dataType["specs"]):
            _logger.warning("%s type is enum but value(%s) is not in range %s" % (key, value, dataType["specs"]))
            return False

    elif ((dataType["type"] == "text")):
        if (not isinstance(value, (str))):
            _logger.warning("%s type is text but value(%s) is not text" % (key, value))
            return False
        elif (int(dataType["specs"]["length"]) < len(value)):
            _logger.warning("%s type is text but value(%s) is not in range %s" % (key, value, dataType["specs"]))
            return False

    elif ((dataType["type"] == "array") and (not isinstance(value, (list, tuple)))):
        _logger.warning("%s type is array but value(%s) is not array" % (key, value))
        return False

    elif (dataType["type"] == "date"):
        if (not isinstance(value, (str))):
            _logger.warning("%s type is date but value(%s) is not string format" % (key, value))
            return False
        elif (len(value) != 10 and len(value) != 13):
            _logger.warning("%s type is date but value(%s) length %d is not 10 or 13" % (key, value, len(value)))
            return False
    else:
        pass

    return True

def checkOpcdaDeviceConfig(opcdaDevCfg):
    """
    {
        "deviceName":"led1",
        "productKey":"a17wHuIbJxG",
        "custom":{
            "serverId":1,
            "devicePath":"alibaba.aliyun.iot.led.led1"
        }
    }
    """
    if "productKey" in opcdaDevCfg:
        if not isinstance(opcdaDevCfg["productKey"], str):
            raise OpcdaCfgError(OPCDA_ERROR_CFG_INVALID_PK, "ProductKey is not string")
    else:
        raise OpcdaCfgError(OPCDA_ERROR_CFG_INVALID_PK, "ProductKey ino exist")

    if "deviceName" in opcdaDevCfg:
        if not isinstance(opcdaDevCfg["deviceName"], str):
            raise OpcdaCfgError(OPCDA_ERROR_CFG_INVALID_DN, "DeviceName is not string")
    else:
        raise OpcdaCfgError(OPCDA_ERROR_CFG_INVALID_DN, "DeviceName no exist")

    if "custom" in opcdaDevCfg:
        opcdaDevCfg["custom"] = json.loads(opcdaDevCfg["custom"])
        if "devicePath" in opcdaDevCfg["custom"]:
            if not isinstance(opcdaDevCfg["custom"]["devicePath"], str):
                raise OpcdaCfgError(OPCDA_ERROR_CFG_INVALID_DEVICEPATH, "devicePath is not a string")
        else:
            raise OpcdaCfgError(OPCDA_ERROR_CFG_INVALID_CUSTOMCONFIG, "devicePath no exist")

        if "reportType" in opcdaDevCfg["custom"]:
            if not isinstance(opcdaDevCfg["custom"]["reportType"], int):
                raise OpcdaCfgError(OPCDA_ERROR_CFG_INVALID_REPORTTYPE, "reportType is not a int")
            else:
                if opcdaDevCfg["custom"]["reportType"] != 0 and opcdaDevCfg["custom"]["reportType"] != 1:
                    raise OpcdaCfgError(OPCDA_ERROR_CFG_INVALID_REPORTTYPE, "reportType is not in range(0, 1)")

        if "serverId" in opcdaDevCfg["custom"]:
            if not isinstance(opcdaDevCfg["custom"]["serverId"], int):
                raise OpcdaCfgError(OPCDA_ERROR_CFG_INVALID_SERVERID, "serverId is not a int")
        else:
            raise OpcdaCfgError(OPCDA_ERROR_CFG_INVALID_CUSTOMCONFIG, "serverId no exist")
    else:
        raise OpcdaCfgError(OPCDA_ERROR_CFG_INVALID_CUSTOMCONFIG, "custom no exist")

def checkOpcdaServerConfig(opcdaSvrCfg):
    """
    {
        "serverId":1,
        "opcProxyIp":"192.168.1.100",
        "opcProxyPort":7766,
        "opcServer":"Matrikon.OPC.Simulation"
    }
    """

    if "serverId" in opcdaSvrCfg:
        if not isinstance(opcdaSvrCfg["serverId"], int):
            raise OpcdaCfgError(OPCDA_ERROR_CFG_INVALID_SERVERID, "serverId is not a string")
    else:
        raise OpcdaCfgError(OPCDA_ERROR_CFG_INVALID_SERVERID, "serverId no exist")

    if "opcServer" in opcdaSvrCfg:
        if not isinstance(opcdaSvrCfg["opcServer"], str):
            raise OpcdaCfgError(OPCDA_ERROR_CFG_INVALID_OPCSERVER, "opcServer is not a string")
    else:
        raise OpcdaCfgError(OPCDA_ERROR_CFG_INVALID_OPCSERVER, "opcServer no exist")

    if "opcProxyIp" in opcdaSvrCfg:
        if not isinstance(opcdaSvrCfg["opcProxyIp"], str):
            raise OpcdaCfgError(OPCDA_ERROR_CFG_INVALID_PROXYIP, "opcProxyIp is not a string")
        else:
            ip_reg = re.compile('^(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|[1-9])\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)$')
            if not ip_reg.match(opcdaSvrCfg["opcProxyIp"]):
                raise OpcdaCfgError(OPCDA_ERROR_CFG_INVALID_PROXYIP, "opcProxyIp %s is a invalid" % (opcdaSvrCfg["opcProxyIp"]))
    else:
        raise OpcdaCfgError(OPCDA_ERROR_CFG_INVALID_PROXYIP, "opcProxyIp no exist")

    if "opcProxyPort" in opcdaSvrCfg:
        if not isinstance(opcdaSvrCfg["opcProxyPort"], int):
            raise OpcdaCfgError(OPCDA_ERROR_CFG_INVALID_PROXYPORT, "opcProxyPort is not a int")
        else:
            if opcdaSvrCfg["opcProxyPort"] <= 0 and opcdaSvrCfg["opcProxyPort"] >= 65535:
                raise OpcdaCfgError(OPCDA_ERROR_CFG_INVALID_PROXYPORT, "opcProxyPort %d is not in range(0, 65535)" % (opcdaSvrCfg["opcProxyPort"]))
    else:
        raise OpcdaCfgError(OPCDA_ERROR_CFG_INVALID_PROXYPORT, "opcProxyPort no exist")

    if "collectInterval" in opcdaSvrCfg:
        if not isinstance(opcdaSvrCfg["collectInterval"], int):
            raise OpcdaCfgError(OPCDA_ERROR_CFG_INVALID_COLLECTINTERVAL, "collectInterval is not a int")

def checkOpcdaConfig(serverConfig, deviceConfig):
    if len(serverConfig) == 0 or len(deviceConfig) == 0:
        return False

    serverList = serverConfig
    for cfg in serverList[:]:
        try:
            checkOpcdaServerConfig(cfg)
        except Exception as e:
            _logger.exception("check server config happen exception: %s" % e)
            serverList.remove(cfg)

    deviceList = deviceConfig
    for cfg in deviceList[:]:
        try:
            checkOpcdaDeviceConfig(cfg)
        except Exception as e:
            _logger.exception("check device config happen exception: %s" % e)
            deviceList.remove(cfg)

    return True
