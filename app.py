''' this is the master file which the procfile points to on the server.'''

import followups
import gmail_new_user_server
from threading import Timer

import logging
logging.getLogger('googleapiclient').setLevel(logging. CRITICAL + 10)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

if __name__ == '__main__':
    
    logging.info('''#
    #
    #
    (RE)STARTING PROCESS
    #
    #
    #
    ''')
    
    def execute_task():
        followups.run()
        t = Timer(45,execute_task)
        t.start()
        return
    execute_task()

    # Heroku will run this as a background web thread
    gmail_new_user_server.run()