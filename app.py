''' this is the master file which the procfile points to on the server.
It has:
1. a loop and timer over followups.py,
2. a loop and timer over new_user_flow.py
2. runs the webserver for signups
'''

from threading import Timer

import logging
logging.getLogger('googleapiclient').setLevel(logging. CRITICAL + 10)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

import gmail_new_user_server
import followups
import new_user_flow




def execute_task():
        logging.info('''#
        #
        #
        (RE)STARTING PROCESS
        #
        #
        #
        ''')
        
        # functions to run each cycle
        new_user_flow.run()
        followups.run()
        
        # Timer
        t = Timer(45,execute_task)
        t.start()
        return

if __name__ == '__main__':
    
    # Heroku will run this as a background web thread
    # NOTE toggle this off for local testing of it will just run the webserver forever.
    # gmail_new_user_server.run()

    # initialize the infinite cycle
    execute_task()