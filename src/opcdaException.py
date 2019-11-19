#!/usr/bin/env python3
#-*- coding: utf-8 -*-

"""
LE error code definition
"""
LE_SUCCESS                              = 0       # 执行成功
LE_ERROR_FAILED                         = 100000  # 执行失败
LE_ERROR_INVAILD_PARAM                  = 100001  # 无效参数
LE_ERROR_NO_MEM                         = 100002  # 没有内存
LE_ERROR_TIMEOUT                        = 100006  # 超时
LE_ERROR_NOT_SUPPORT                    = 100008  # 不支持
LE_ERROR_PROPERTY_NOT_EXIST             = 109002  # 属性不存在
LE_ERROR_PROPERTY_READ_ONLY             = 109003  # 属性不允许写
LE_ERROR_PROPERTY_WRITE_ONLY            = 109004  # 属性不允许读
LE_ERROR_SERVICE_NOT_EXIST              = 109005  # 服务不存在
LE_ERROR_SERVICE_INPUT_PARAM            = 109006  # 服务参数未验证

"""
OPCDA error code definition
"""
OPCDA_ERROR                             = 100
OPCDA_ERROR_CFG                         = 101
OPCDA_ERROR_CFG_INVALID_SERVERID        = 102
OPCDA_ERROR_CFG_INVALID_OPCSERVER       = 103
OPCDA_ERROR_CFG_INVALID_PROXYIP         = 104
OPCDA_ERROR_CFG_INVALID_PROXYPORT       = 105
OPCDA_ERROR_CFG_INVALID_COLLECTINTERVAL = 106
OPCDA_ERROR_CFG_INVALID_PK              = 107
OPCDA_ERROR_CFG_INVALID_DN              = 108
OPCDA_ERROR_CFG_INVALID_CUSTOMCONFIG    = 109
OPCDA_ERROR_CFG_INVALID_DEVICEPATH      = 110
OPCDA_ERROR_CFG_INVALID_REPORTTYPE      = 111

"""
OPCDA exception class definition
"""
class OpcdaError(Exception):
    def __init__(self, value=OPCDA_ERROR, msg="opcda common error"):
        self.value = value
        self.msg = msg

    def __str__(self):
        return "Error code:%d, Error message: %s" % (self.value, str(self.msg))

    __repr__ = __str__

class OpcdaCfgError(OpcdaError):
    def __init__(self, value=OPCDA_ERROR_CFG, msg = "opcda configuration common error"):
        message = "[OpcdaCfgError] %s" % (str(msg))
        OpcdaError.__init__(self, value, message)
