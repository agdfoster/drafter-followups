''' if you import this file, it will run the below and config the logger for
the whole of that file, no need to call anything. '''
import logging

logging.warning('Watch out!')  # will print a message to the console
logging.info('I told you so')  # will not print anything
logging.getLogger('googleapiclient').setLevel(logging. CRITICAL + 10)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

# def logg_config(log_level):
#     ''' sets configuration for logging, 'import and play' - import and that's it.
#     note: you can't change the settings in file as well of everything will log twice :( '''
#     logger = logging.getLogger()
#     logger.setLevel(log_level)
#     filemode = 'w'

#     formatter = logging.Formatter('%(message)s')

#     fileh = logging.FileHandler('_logs.txt')
#     fileh.setLevel(logging.DEBUG)
#     fileh.setFormatter(formatter)
#     logger.addHandler(fileh)

#     chch = logging.StreamHandler()
#     chch.setLevel(logging.DEBUG)
#     chch.setFormatter(formatter)
#     logger.addHandler(chch)
#     return logger

# def logg_init():
#     logg_config(logging.DEBUG)
#     # options are: debug info warning error critical
    
#     logging.info("Logger working")
#     # stops Google's API lib underlying logs from logging
#     logging.getLogger('googleapiclient').setLevel(logging. CRITICAL + 10)
#     pass

# if __name__ == '__main__':
#     logging.debug("Hello world ")