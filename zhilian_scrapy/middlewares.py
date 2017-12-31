# -*- coding: utf-8 -*-
from .usa_phone import USA_phone
# 引用 UserAgentMiddleware
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from twisted.internet import defer
from twisted.internet.error import TimeoutError, ConnectionRefusedError, \
    ConnectError, ConnectionLost, TCPTimedOutError, ConnectionDone
import logging
import redis
import random

logger = logging.getLogger(__name__)

class UserAgentmiddleware(UserAgentMiddleware):
    def process_request(self, request, spider):
        agent = random.choice(USA_phone)
        request.headers["User-Agent"] = agent

class HttpProxymiddleware(object):
    #一些异常情况汇总
    EXCEPTIONS_TO_CHANGE = (
    defer.TimeoutError, TimeoutError, ConnectionRefusedError, ConnectError, ConnectionLost, TCPTimedOutError,
    ConnectionDone)

    def __init__(self):
        #链接redis数据库
        self.rds = redis.from_url('redis://:你的密码@localhost:6379/0',decode_responses=True)  ##decode_responses设置取出的编码为str

    def process_request(self, request, spider):
        #拿出全部key，随机选取一个键值对
        keys = self.rds.hkeys("xila_hash")
        key = random.choice(keys)
        #用eval函数转换为dict
        proxy = eval(self.rds.hget("xila_hash",key))
        logger.warning("-----------------"+str(proxy)+"试用中------------------------")
        #将代理ip 和 key存入mate
        request.meta["proxy"] = proxy["ip"]
        request.meta["accountText"] = key

    def process_response(self, request, response, spider):
        http_status = response.status
        #根据response的状态判断 ，200的话ip的times +1重新写入数据库，返回response到下一环节
        if http_status == 200:
            key = request.meta["accountText"]
            proxy = eval(self.rds.hget("xila_hash",key))
            proxy["times"] = proxy["times"] + 1
            self.rds.hset("xila_hash",key,proxy)
            return response
        #403有可能是因为user-agent不可用引起，和代理ip无关，返回请求即可
        elif http_status == 403:
            logging.warning("#########################403重新请求中############################")
            return request.replace(dont_filter=True)
        #其他情况姑且被判定ip不可用，times小于10的，删掉，大于等于10的暂时保留
        else:
            ip = request.meta["proxy"]
            key = request.meta["accountText"]
            proxy = eval(self.rds.hget("xila_hash", key))
            if proxy["times"] < 10:
                self.rds.hdel("xila_hash",key)
            logging.warning("#################" + ip + "不可用，已经删除########################")
            return request.replace(dont_filter=True)

    def process_exception(self, request, exception, spider):
        #其他一些timeout之类异常判断后的处理，ip不可用删除即可
        if isinstance(exception, self.EXCEPTIONS_TO_CHANGE) \
                and request.meta.get('proxy', False):
            key = request.meta["accountText"]
            print("+++++++++++++++++++++++++{}不可用+++将被删除++++++++++++++++++++++++".format(key))
            proxy = eval(self.rds.hget("xila_hash", key))
            if proxy["times"] < 10:
                self.rds.hdel("xila_hash", key)
            logger.debug("Proxy {}链接出错{}.".format(request.meta['proxy'], exception))
            return request.replace(dont_filter=True)
