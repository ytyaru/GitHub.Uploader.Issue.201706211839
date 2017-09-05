#!python3
#encoding:utf-8
import logging

def Singleton(cls):
    instances = {}
    def getinstance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return getinstance

@Singleton
class Log(object):
    def __init__(self):
        self.__logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        self.__logger.setLevel(logging.DEBUG)
        self.__logger.addHandler(handler)
        
    @property
    def Logger(self):
        return self.__logger


if __name__ == '__main__':
    l = Log()
    l.Logger.setLevel(logging.DEBUG)
    l.Logger.debug('testですよ。')
    Log().Logger.debug('debug()')
    Log().Logger.info('info()')
    Log().Logger.warning('warning()')
    Log().Logger.error('error()')
    Log().Logger.critical('critical()')

    print('Level|Name')
    print('-----|----')
    levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]
    for level in levels:
        print("{0}|{1}".format(level, logging.getLevelName(level)))

    l.Logger.setLevel(logging.INFO)
    Log().Logger.debug('setLevelがINFOのときdebug()は表示されない。')
    level = 0
    Log().Logger.log(level, 'log() level={0} {1}'.format(level, logging.getLevelName(level)))
    level = logging.WARNING
    Log().Logger.log(level, 'log() level={0} {1}'.format(level, logging.getLevelName(level)))
