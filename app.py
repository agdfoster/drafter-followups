''' this is the master file which the procfile points to on the server.'''

import followups
import gmail_new_user_server
from threading import Timer

if __name__ == '__main__':
    
    
    
    def execute_task():
        followups.run()
        t = Timer(1,execute_task)
        t.start()
        return
    execute_task()

    # Heroku will run this as a background web thread
    gmail_new_user_server.run()