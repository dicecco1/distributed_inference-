# server3.py on EC2 instance
import socket
import time
from threading import Thread
from SocketServer import ThreadingMixIn
#from subprocess import call 
import subprocess
import Queue
import sys

#TCP_IP = '10.2.5.16'
TCP_PORT = 8888
TCP_PORT_CL = 60001 
TCP_IP_CL = sys.argv[2]
#TCP_IP_CL = '10.2.5.14'
BUFFER_SIZE = 1024

BUF_SIZE = 1000

q = Queue.Queue(BUF_SIZE)

#print 'TCP_IP=',TCP_IP
#print 'TCP_PORT=',TCP_PORT

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(('8.8.8.8', 0))
local_ip_address = s.getsockname()[0]
s.close()

class SendThread(Thread):
    def __init__(self, filename=None, group=None, target=None, name=None,
                args=(), kwargs=None, verbose=None):
        super(SendThread, self).__init__()
        self.target = target
        self.name = name
        self.filename = filename
        print "Thread name ", name
        return
    def run(self):
        print "Connecting to Client Server"
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP_CL, TCP_PORT_CL))

        print "Successfully connected"

        #filename = item.split('jpg')[0] + "txt"
        filename = self.filename
        f = open(filename, 'rb')

        while True:
            cmd = s.recv(32)
            if cmd == 'getfilename':
                print('"getfilename" command received.')
                s.sendall(filename)

            if cmd == 'getfile':
                clock_start = time.clock()
                time_start = time.time()
                print('"getfile" command received. Going to send file.')
                data = f.read()
                s.sendall('%16d' % len(data))
                s.sendall(data)
                print('File transmission done.')
                clock_end = time.clock()
                time_end = time.time()

            if cmd == 'status':
                s.sendall('done')

            if cmd == 'end':
                print('"end" command received. Terminate.')
                break
        duration_clock = clock_end - clock_start
        print 'clock:  start = ',clock_start, ' end = ',clock_end
        print 'clock:  duration_clock = ', duration_clock

        duration_time = time_end - time_start
        print 'time:  start = ',time_start, ' end = ',time_end
        print 'time:  duration_time = ', duration_time
        subprocess.Popen(["rm", filename])

class ConsumerThread(Thread):
    def __init__(self, group=None, target=None, name=None,
                args=(), kwargs=None, verbose=None):
        super(ConsumerThread, self).__init__()
        self.target = target
        self.name = name
        print "Thread name ", name 
        return
    def run(self):
        while True:
            if not q.empty():
                print "Got new file"
                item = q.get()
                print "Item is ", item
                if sys.argv[1] == '1':
                    output = subprocess.Popen(["./build/examples/cpp_classification/classification.bin",
                                            "models/bvlc_alexnet/deploy.prototxt",
                                            "models/bvlc_alexnet/bvlc_alexnet.caffemodel",
                                            "data/ilsvrc12/imagenet_mean.binaryproto",
                                            "data/ilsvrc12/synset_words.txt",
                                            item, "OCL_enable"], stdout=subprocess.PIPE).communicate()[0]
                else:
                    output = subprocess.Popen(["./build/examples/cpp_classification/classification.bin",
                                            "models/bvlc_alexnet/deploy.prototxt",
                                            "models/bvlc_alexnet/bvlc_alexnet.caffemodel",
                                            "data/ilsvrc12/imagenet_mean.binaryproto",
                                            "data/ilsvrc12/synset_words.txt",
                                            item, "OCL_disable"], stdout=subprocess.PIPE).communicate()[0]                    
                print "Output is \n", output
                f = open(item.split('jpg')[0] + "txt", 'wb')
                f.write(output)
                f.close()
                print('Successfully got the file')
                
                subprocess.Popen(["rm", item])
                newthread = SendThread(filename=item.split('jpg')[0] + "txt", name='sender')
                newthread.daemon = True
                newthread.start()
                threads.append(newthread)

class ClientThread(Thread):

    def __init__(self,ip,port,sock):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.sock = sock
        print " New thread started for "+ip+":"+str(port)

    def run(self):
        clock_start = time.clock()
        time_start = time.time()
        self.sock.sendall('getfilename')
        filename = self.sock.recv(1024)
        with open(filename, 'wb') as f:
            print 'file opened'
            while True:
                self.sock.sendall('getfile')
                size = int(self.sock.recv(16))
                print('Total size: ' + str(size))
                recvd = ''
                while size > len(recvd):
                    data = self.sock.recv(1024)
                    if not data:
                        break
                    recvd += data
                    f.write(data)
                break
            self.sock.sendall('status')
            status = self.sock.recv(32)
            print status
            self.sock.sendall('end')
            f.close()
            print('File received.')
            if not q.full():
                print "Queue isn't full"
                q.put(filename)
            else:
                while q.full():
                    print "Waiting"
                q.put(filename)
#        output = subprocess.Popen(["./fpga_caffe/build/examples/cpp_classification/classification.bin",
#                "fpga_caffe/models/bvlc_alexnet/deploy.prototxt",
#                "fpga_caffe/models/bvlc_alexnet/bvlc_alexnet.caffemodel",
#                "fpga_caffe/data/ilsvrc12/imagenet_mean.binaryproto",
#                "fpga_caffe/data/ilsvrc12/synset_words.txt",
#                filename, "1"], stdout=subprocess.PIPE).communicate()[0]
#        print "Output is \n", output
#        f = open(filename.split('jpg')[0] + "txt", 'wb')
#        f.write(output)
#        f.close()
#        print('Successfully got the file')
#        self.sock.close()
#        print('Connection closed')
        
        clock_end = time.clock()
        time_end = time.time()

        duration_clock = clock_end - clock_start
        print 'clock:  start = ',clock_start, ' end = ',clock_end
        print 'clock:  duration_clock = ', duration_clock

        duration_time = time_end - time_start
        print 'time:  start = ',time_start, ' end = ',time_end
        print 'time:  duration_time = ', duration_time

tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpsock.bind((local_ip_address, TCP_PORT))
threads = []

newthread = ConsumerThread(name='consumer')
newthread.daemon = True
newthread.start()
threads.append(newthread)

while True:
    tcpsock.listen(5)
    print "Waiting for incoming connections..."
    (conn, (ip,port)) = tcpsock.accept()
    print 'Got connection from ', (ip,port)
    newthread = ClientThread(ip,port,conn)
    newthread.daemon = True
    newthread.start()
    threads.append(newthread)

for t in threads:
    t.join()
