import logging
import getpass
from datetime import datetime
from config import conf
import os

user=getpass.getuser()
logger=logging.getLogger(user)

# SET LEVEL #
if conf.loggerLevel is 'debug':
    logger.setLevel(logging.DEBUG)
elif conf.loggerLevel is 'info':
    logger.setLevel(logging.INFO)
elif conf.loggerLevel is 'warning':
    logger.setLevel(logging.WARNING)
elif conf.loggerLevel is 'error':
    logger.setLevel(logging.ERROR)
elif conf.loggerLevel is 'critical':
    logger.setLevel(logging.CRITICAL)

format='%(asctime)s - %(levelname)s -%(name)s : %(message)s'
formatter=logging.Formatter(format)
streamhandler=logging.StreamHandler()
streamhandler.setFormatter(formatter)
logger.addHandler(streamhandler)
path = './logs/logs_tutorial/'
if not os.path.isdir(path):
    os.mkdir(path)
logfile='./logs/logs_tutorial/' + "{:%Y-%m-%d}".format(datetime.now()) + '_' + user + '.log'
if os.name == 'nt':
    filehandler=logging.FileHandler(logfile, encoding='utf-8')
else:
    filehandler=logging.FileHandler(logfile)
#filehandler=logging.FileHandler(logfile)
filehandler.setFormatter(formatter)
logger.addHandler(filehandler)
logger.info("[LOGGER START RECORD.][PID : "+ str(os.getpid())+ "\t[LOGGIN LEVEL : " + str(logger.level) + "]")

def debug(msg):
    logger.debug(msg)
def info(msg):
    logger.info(msg)
def warning(msg):
    logger.warning(msg)
def error(msg):
    logger.error(msg)
def critical(msg):
    logger.critical(msg)
def log(level, msg):
    logger.log(level, msg)
def setLevel(level):
    logger.setLevel(level)
def disable():
    logging.disable(50)