import socket
import time
import cv2
import subprocess

#TCP_IP = 'localhost'
TCP_IP = '10.2.5.16'
TCP_PORT = 8888

BUFFER_SIZE = 1024

def client(pref, filename, last_file, ip):
    print "Connecting"
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    s.connect((ip, TCP_PORT))
    print "Done connecting"
    print('Connected. Waiting for command.')

    #filename = 'bookstore.jpg'
    f = open(pref + filename, 'rb')
    print 'file opened'

    while True:
        cmd = s.recv(32)

        if cmd == 'getfilename':
            print('"getfilename" command received.')
            s.sendall(filename)
    
        if cmd == 'getfile':
#            clock_start = time.clock()
#            time_start = time.time()
            print('"getfile" command received. Going to send file.')
            data = f.read()
            s.sendall('%16d' % len(data))
            s.sendall(data)
            print('File transmission done.')
#            clock_end = time.clock()
#            time_end = time.time()

        if cmd == 'status':
            if last_file:
                s.sendall('done')
            else:
                s.sendall('notdone')

        if cmd == 'end':
            print('"end" command received. Terminate.')
            break

#    duration_clock = clock_end - clock_start
#    print 'clock:  start = ',clock_start, ' end = ',clock_end
#    print 'clock:  duration_clock = ', duration_clock

#    duration_time = time_end - time_start
#    print 'time:  start = ',time_start, ' end = ',time_end
#    print 'time:  duration_time = ', duration_time


def process_frames(video):
    clock_start = time.clock()
    time_start = time.time()

    f = open('ip_list.txt')
    lines = f.readlines()

    ips = []
    ips.extend(lines[1].split("\n")[0].split(" "))
    ips.extend(lines[3].split("\n")[0].split(" "))

    to_del = []
    for i in range(len(ips)):
        if ips[i] == '':
            to_del.append(i)

    for i in to_del:
        ips.pop(i)
    print ips

    f.close()

    cap = cv2.VideoCapture(video)

    count = 0 

    if cap.isOpened():
        rval, frame = cap.read()
    else:
        rval = False
    send_count = 0
    while rval:
        rval, frame = cap.read()
        if rval:
            filename = str(count) + '.jpg'
            cv2.imwrite("temp/" + filename, frame)
        if count % 20 == 0 and rval:
            while True:
                try:
                    client("temp/", filename, 1, ips[send_count % len(ips)])
                    send_count = send_count + 1
                    break
                except:
                    send_count = send_count + 1
        count = count + 1
#        cv2.waitKey(1)
    cap.release()

    clock_end = time.clock()
    time_end = time.time()


    duration_clock = clock_end - clock_start
    print 'clock:  start = ',clock_start, ' end = ',clock_end
    print 'clock:  duration_clock = ', duration_clock

    duration_time = time_end - time_start
    print 'time:  start = ',time_start, ' end = ',time_end
    print 'time:  duration_time = ', duration_time
    

process_frames('Wildlife.wmv')
