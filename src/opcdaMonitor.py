#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import logging
import time

import opcdaConfig
import opcdaSession

_logger = logging.getLogger()

class OpcdaMonitor(object):
    def __init__(self):
        self.sessionList = []

    def addSession(self, session):
        self.sessionList.append(session)
        return
    
    def delSession(self, session):
        self.sessionList.remove(session)
        return

    def destroySessions(self):
        for session in self.sessionList:
            self.sessionList.remove(session)

        return

    def Monitor(self):
        while True:
            for session in self.sessionList:
                if not session.getState():
                    if session.connect():
                        _logger.info("It's success with opcda server %s by opc proxy(%s:%d)" % (session.opcServerName, session.opcProxyIp, session.opcProxyPort))
                        session.onlineDevices()
                    else:
                        _logger.warning("It's failed with opcda server %s by opc proxy(%s:%d)" % (session.opcServerName, session.opcProxyIp, session.opcProxyPort))
                else:
                    for i in range(opcdaConfig.OPEN_OPC_RETRY_NUMBER):
                        try:
                            if session.isAlive():
                                session.reOnlineDevices()
                            else:
                                time.sleep(1)
                        except Exception as e:
                            _logger.exception("exception %s happen when keepalive with opc server(%s)" % (e, session.opcServerName))
                            time.sleep(1)
                        else:
                            break
                    else:
                        _logger.warning("It' timeout keepalive with opcda server %s" % (session.opcServerName))
                        session.disconnect()
                
                _logger.debug("current session %s online device number: %d, offline device number: %d" % (session.opcServerName, len(session.onlineDeviceList), len(session.offlineDeviceList)))
            else:
                pass
            time.sleep(opcdaConfig.OPEN_OPC_KEEPALIVE_TIME)
        return