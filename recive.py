import cv2 as cv
import numpy as np
import threading
import os
import time
import datetime
from upload import s3
import firebase_admin
from firebase_admin import credentials, db
import multiprocessing as mp
from multiprocessing import shared_memory
import sys

cred = credentials.Certificate("your firebase credit path")
firebase_admin.initialize_app(cred,
                              {'databaseURL' : 'your firebase url'})

datapath='video'
ref=db.reference(datapath)
fps= 30
dst='./test.mp4'    #저장 위치


event_flag=np.array([0])

save_second=3   #몇초 저장할건지

queue_size = save_second*30
queue = []
class Sdata:
    def __init__(self, cam_no):
        self.cam_no=cam_no
        self.event_type=0
        self.link_storage=''
        self.date=''
        self.time=''
        
# def flagcontrol():
    # sevent_flag=np.array([0])
    # print(sevent_flag.nbytes)
    # flagshm=shared_memory.SharedMemory(create=True, size=sevent_flag.nbytes)
    # print('flag= '+flagshm.name)
    # event_flag = np.ndarray(sevent_flag.shape, dtype=sevent_flag.dtype, buffer=flagshm.buf)
    # event_flag[:]=sevent_flag[:]
    # while True:
    #     event_flag=0
    #     time.sleep(10)
    #     event_flag=1
    #     time.sleep(10)
    #     event_flag=2
    #     time.sleep(5)
        
def Vsave(sdata, filename):
    global event_flag
    ref=db.reference('flag')
    ref.set(str(event_flag[0]))
    s3.upload_file(filename,"sjmama1",filename)
    print('s3 upload!')
    sdata.link_storage='https://your_s3_storage_url/'+sdata.date+'%'+sdata.date[2:4]+sdata.time+'.mp4'
    sdata_dict=sdata.__dict__
    print(sdata_dict)
    ref=db.reference('video')#저장한 파일은 삭제
    ref.push(sdata_dict)
    print('firebase push!')
    os.remove(filename)

def showNsave(cam_no):
    global cap
    global event_flag
    ret, frame = cap.read()
    ref=db.reference('flag')
    ref.set(str('0'))
    print(str(frame.shape).replace(' ', ''))
    os.system('echo '+str(frame.shape).replace(' ', '').replace('(', '').replace(')','')+' > info.txt')
    sevent_flag=np.array([0])
    print(sevent_flag.nbytes)
    flagshm=shared_memory.SharedMemory(create=True, size=sevent_flag.nbytes)
    print('flag= '+flagshm.name)
    os.system('echo '+flagshm.name+' >> info.txt')
    event_flag = np.ndarray(sevent_flag.shape, dtype=sevent_flag.dtype, buffer=flagshm.buf)
    event_flag[:]=sevent_flag[:]
    sdata=Sdata(cam_no)
    innerflag=0
    print(frame.shape, frame.dtype)
    fourcc = cv.VideoWriter_fourcc(*'mp4v')
    frameshm=shared_memory.SharedMemory(create=True, size=frame.nbytes)
    os.system('echo '+frameshm.name+' >> info.txt')
    print('frame= '+frameshm.name)
    out = cv.VideoWriter(dst, fourcc, fps, (frame.shape[1], frame.shape[0]))
    while cap.isOpened():
        ret, frame = cap.read()
        sharedframe=np.ndarray(frame.shape, dtype=frame.dtype, buffer=frameshm.buf)
        sharedframe[:]=frame[:]
        # if frame is read correctly ret is True
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        #cv.imshow('frame', frame)
        queue.append(frame)
        if len(queue) > queue_size:
            queue.pop(0)
        if innerflag==0 and event_flag[0]!=0:#여기는 위험 신호 감지해서 저장하게 해야하고
            print(event_flag[0])
            ref=db.reference('flag')
            if event_flag[0]==12:
                ref.set(str(2))
            else:
                ref.set(str(event_flag[0]))
            sdata.event_type=str(event_flag[0])
            innerflag=event_flag[0]
            now = datetime.datetime.now()
            sdata.date=now.strftime("%Y-%m-%d")
            sdata.time=now.strftime("%Hh%Mm%Ss")
            new_filename = f"{sdata.date}#{sdata.time}.mp4"
            for f in queue:
                out.write(f)
        elif innerflag!=0 and event_flag[0]!=0:
            out.write(frame)
            if (innerflag != event_flag[0]) :
                innerflag=event_flag[0]
                ref=db.reference('flag')
                if event_flag[0]==12:
                    ref.set(str(2))
                else:
                    ref.set(str(event_flag[0]))
        elif innerflag!=0 and event_flag[0]==0:
            print(event_flag[0])
            out.release()
            os.rename("test.mp4", new_filename)
            Vsaveth=threading.Thread(target=Vsave, args=(sdata, new_filename))
            Vsaveth.start()
            innerflag=event_flag[0]
            # ref=db.reference('flag')
            # ref.set(event_flag)
            # innerflag=event_flag
            # out.release()
            # os.rename("test.mp4", new_filename)
            # s3.upload_file(new_filename,"sjmama1",new_filename)
            # print('s3 upload!')
            # sdata.link_storage='https://your s3 storage url/'+new_filename
            # sdata_dict=sdata.__dict__
            # print(sdata_dict)
            # ref=db.reference('video')#저장한 파일은 삭제
            # ref.push(sdata_dict)
            # print('firebase push!')
            out = cv.VideoWriter(dst, fourcc, fps, (frame.shape[1], frame.shape[0]))
        
    out.release()
    cap.release()


# fctl=threading.Thread(target=flagcontrol, args=())
# fctl.daemon=True
def main():
    global cap
    cam_no='0000'
    cap = cv.VideoCapture('rtmp://stramserverip/stream app name/'+cam_no)
    S_S=threading.Thread(target=showNsave, args=(cam_no,))#show and save
    # fctl.start()
    if os.path.exists(dst):
        os.remove(dst)
    S_S.start()
    S_S.join()
    cv.destroyAllWindows()

if __name__ == "__main__":
    main()