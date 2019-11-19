#!/usr/bin/env python3
#-*- coding: utf-8 -*-

"""
opcda server state definition
"""
OPC_STATUS_RUNNING          = 'Running'
OPC_STATUS_FAILED           = 'Failed'
OPC_STATUS_NOCONFIG         = 'NoConfig'
OPC_STATUS_SUSPENDED        = 'Suspended'
OPC_STATUS_TEST             = 'Test'

"""
opcda browser type definition
"""
OPC_BROWSER_TYPE_FLAT       = 'Flat'
OPC_BROWSER_TYPE_HIERARCHIC = 'Hierarchical'

"""
opcda data access rights definition
"""
OPC_ACCESS_MODE_R           = 'r'
OPC_ACCESS_MODE_W           = 'w'
OPC_ACCESS_MODE_RW          = 'rw'

"""
opcda data quality definition
"""
OPC_QUALITY_BAD             = 'Bad'
OPC_QUALITY_UNCERTAIN       = 'Uncertain'
OPC_QUALITY_UNKNOWN         = 'Unknown'
OPC_QUALITY_GOOD            = 'Good'

"""
opcda data source definition
"""
OPC_DATA_SOURCE_DEVICE      = 'device'
OPC_DATA_SOURCE_CACHE       = 'cache'
OPC_DATA_SOURCE_HYBRID      = 'hybrid'

"""
opcda groups default config definition
"""
OPC_GROUPS_UPDATE_RATE      = 1000      #update interval(milliseconds)
OPC_GROUPS_TIME_BIAS        = 0
OPC_GROUPS_DEAD_BAND        = 0

"""
opcda report type definition
"""
OPC_REPORT_TYPE_TIMER       = 0
OPC_REPORT_TYPE_CHANGE      = 1

"""
opcda collect interval definition
"""
OPC_COLLECT_INTERVAL        = 5         #collect interval(seconds)

"""
OpenOPC library default config definition
"""
OPEN_OPC_READ_TIME_OUT     = 5000

OPEN_OPC_SYNC_READ         = True
OPEN_OPC_ASYNC_READ        = False

OPEN_OPC_LIST_FLAT         = True
OPEN_OPC_LIST_HIERARCHICAL = False

OPEN_OPC_LIST_RECURSIVE     = True
OPEN_OPC_LIST_UNRECURSIVE   = False

OPEN_OPC_RETRY_NUMBER       = 3

OPEN_OPC_KEEPALIVE_TIME     = 3
