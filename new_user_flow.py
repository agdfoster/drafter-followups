''' checks for new users in db, runs a special process for them if it's the first time.
NOTE: new is based on any previous sign up. returning users will not re-run setup. ideally improve this'''

import datetime
import logging
logging.getLogger('googleapiclient').setLevel(logging. CRITICAL + 10)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

# database
from utils.db_vars import *
import get_aliases
import get_gmail_service_obj
import followups

ONBOARDING_SPECIAL_SEARCH_DAYS = 60 # days (number of days to back search for followups during onboarding)

def check_for_new_users():
    # get user list from db
    users_list = db.user_creds.distinct('user_email')
    # get list of users that have completed onboarding from db
    user_onboards = db.user_onboards.distinct('user_email')
    # do a dif
    new_users = [user for user in users_list if user not in user_onboards]
    logging.info('new_users_list = {}'.format(new_users))
    return new_users

def onboarding_flow(new_user):
    ''' run once for each new user, 
    builds it's own service object '''
    user_email = new_user
    # build service object
    service, fname, sname, email = get_gmail_service_obj.main(user_email)
    # get aliases and store in DB for future use (inside the fucntion)
    get_aliases.run(user_email, service, fname, sname)
    # run a special, backdated followups process. (make)
    # NOTE built for multiple users but works for one as long as you wrap it in a list.
    # NOTE followups.main is a bit of a mess, and has to rebuild the service object, this is quick though... so fuck it.
    after = followups.define_search_period(ONBOARDING_SPECIAL_SEARCH_DAYS)
    print(after)
    followups.main([user_email], after) # after = date after which to backsearch
    # if successfully completed - add user to completed onboarding list.
    db.user_onboards.insert({'user_email': user_email, 'date': datetime.now()})
    pass

def main():
    logging.info('--------------------------------------------------------------------------')
    logging.info('------------------------RUNNING ONBOARDING PROCESS------------------------')
    logging.info('--------------------------------------------------------------------------')
    new_users = check_for_new_users()
    logging.info('new_users_list = {}'.format(new_users))
    for new_user_email in new_users:
        print (new_user_email)
        logging.info('running onboarding backlog followups process for {}'.format(new_user_email))
        onboarding_flow(new_user_email)
    logging.info('--------------------------------------------------------------------------')
    logging.info('------------------------FINISHED ONBOARDING PROCESS-----------------------')
    logging.info('--------------------------------------------------------------------------')

def run():
    main()

if __name__ == '__main__':
    run()