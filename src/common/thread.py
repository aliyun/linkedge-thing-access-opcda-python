#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import queue
import threading
import logging

_logger = logging.getLogger()

class Thread(threading.Thread):
	'''
	定义一个能够处理任务的线程类，属于自定义线程类，自定义线程类就需要定义run()函数
	'''

	def __init__(self, taskQueue):
		threading.Thread.__init__(self)
		self.taskQueue = taskQueue
		self.stopFlag = False
		self.setDaemon(True)
		self.start()

	def enableStopFlag(self):
		self.stopFlag = True

	def run(self):
		'''
		重构run 方法
		'''
		while(True):
			if(True == self.stopFlag):
				break

			try:
				func, kwargs = self.taskQueue.get(block = True, timeout = 10)
			except queue.Empty:
				continue
			else:
				func(**kwargs)


class ThreadPool(object):
	'''
	自定义线程池
	'''
	def __init__(self, threadNum, taskNum):
		self.threadList = []
		self.taskQueue = queue.Queue(maxsize = taskNum)
		self._init_threadPool(threadNum)

	def _init_threadPool(self, threadNum):
		for i in range(threadNum):
			thread = Thread(self.taskQueue)
			self.threadList.append(thread)

	def addTask(self, func, **kwargs):
		try:
			self.taskQueue.put((func, kwargs))
		except queue.Full:
			_logger.warning("threaPool Queue is overflowed")
			pass

	def releasThread(self):
		"""
		关闭线程池中所有的线程
		"""
		for item in self.threadList:
			if(item.isAlive()):
				item.enableStopFlag()
				item.join()



# 函数名称： createThread
# 功能描述： 创建独立线程
# 输入参数：
# 	task： 任务
# 	args: 任务的参数
# 返 回 值： 无
def createThread(task, *args):

	t = threading.Thread(target=task, args = args)
	t.setDaemon(True)
	t.start()

