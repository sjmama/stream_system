import firebase_admin
from firebase_admin import credentials, db
import datetime

cred = credentials.Certificate("your credit path")
firebase_admin.initialize_app(cred,
                              {'databaseURL' : 'your firebase url'})

class Sdata:
    def __init__(self, cam_no):
        self.cam_no=cam_no
        self.event_type=0
        self.link_storage=''
        self.date=''
        self.time=''
