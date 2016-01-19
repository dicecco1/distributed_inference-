import socket
import time
from threading import Thread
from SocketServer import ThreadingMixIn
import subprocess
import Queue
import sys
import cv2
import os
import video_record
TCP_PORT = 60001

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(('8.8.8.8', 0))
local_ip_address = s.getsockname()[0]
s.close()

class ClientThread(Thread):

    def __init__(self,ip,port,sock):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.sock = sock
#        print " New thread started for "+ip+":"+str(port)

    def run(self):
        #clock_start = time.clock()
        #time_start = time.time()
        self.sock.sendall('getfilename')
        filename = self.sock.recv(1024)
#        print 'file opened'
        while True:
            self.sock.sendall('getfile')
            size = self.sock.recv(18)
            size = size.split('-')[0]
#            print size
            size = int(size)
            print('Total size: ' + str(size))
            recvd = ''
            while size > len(recvd):
                data = self.sock.recv(1024)
                if not data:
                    break
                recvd += data
            break
            self.sock.sendall('status')
            status = self.sock.recv(32)
            self.sock.sendall('end')
        index = recvd.find('\n')
        filename = filename.split('txt')[0]+'jpg'
        print "Received File"
        base = int(filename.split('.jpg')[0])

        for i in range(20):
            img = cv2.imread("temp/" + str(base + i) + '.jpg')
            if img != None:
                font = cv2.FONT_HERSHEY_SIMPLEX 

                text = recvd[index+1:].split('\n')
                offset = 0
                for line in text:
                    cv2.putText(img, line, (30, 30 + offset), font, 1, (0,0,0), 2, 8)      
                    offset = offset + 30
                cv2.imwrite("output/" + str(base + i) + '.jpg', img)

        temp = os.listdir('temp/')
        output = os.listdir('output/')
#        if len(output) == len(temp):
#            done_recv = 1
            #clock_end = time.clock()
            #time_end = time.time()

            #duration_clock = clock_end - clock_start
            #print 'clock:  start = ',clock_start, ' end = ',clock_end
            #print 'clock:  duration_clock = ', duration_clock

            #duration_time = time_end - time_start
            #print 'time:  start = ',time_start, ' end = ',time_end
            #print 'time:  duration_time = ', duration_time

tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpsock.bind((local_ip_address, TCP_PORT))
#tcpsock.setblocking(0)
tcpsock.settimeout(1)
threads = []

is_set = 0

print "Waiting for incoming connections..."
while True:
    tcpsock.listen(5)
    #print "Waiting for incoming connections..."
    try:
        (conn, (ip,port)) = tcpsock.accept()
        print 'Got connection from ', (ip,port)
        if is_set == 0:
            print "Starting Timer"
            clock_start = time.clock()
            time_start = time.time()        
        is_set = 1
        newthread = ClientThread(ip,port,conn)
        newthread.daemon = True
        newthread.start()
        threads.append(newthread)
    except socket.error, e:
        pass
    temp = os.listdir('temp/')
    output = os.listdir('output/')

    if len(output) == len(temp) and is_set:
        clock_end = time.clock()
        time_end = time.time()

        duration_clock = clock_end - clock_start
        print 'clock:  start = ',clock_start, ' end = ',clock_end
        print 'clock:  duration_clock = ', duration_clock

        duration_time = time_end - time_start
        print 'time:  start = ',time_start, ' end = ',time_end
        print 'time:  duration_time = ', duration_time
        clock_start = time.clock()
        time_start = time.time()

        video_record.write_video('output.wmv')
        clock_end = time.clock()
        time_end = time.time()

        duration_clock = clock_end - clock_start
        print 'video_record clock:  start = ',clock_start, ' end = ',clock_end
        print 'video_record clock:  duration_clock = ', duration_clock

        duration_time = time_end - time_start
        print 'video_record time:  start = ',time_start, ' end = ',time_end
        print 'video_record time:  duration_time = ', duration_time

        is_set = 0

for t in threads:
    t.join()

