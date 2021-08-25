#!/usr/bin/python
import shutil
import matplotlib.pyplot as plt
import time
import os
import sys
import re,signal
import xml.etree.ElementTree
from mininet.net import Mininet
from mininet.link import TCLink
from subprocess import Popen, PIPE
import argparse

#sudo python jian2.py 
#python jianf1.py --b1 1000 --b2 1000 --m 0

#echo 1 > /sys/kernel/debug/tracing/events/tcp/tcp_probe/enable
be = time.time()
def loadData(filePath):
    fr = open(filePath)
    lines = fr.readlines()
    #print len(lines),lines
    

    s1='';t1=1;C1=[];T1=[];R1=[];
    s2='';t2=1;C2=[];T2=[];R2=[];
    s3='';t3=1;C3=[];T3=[];R3=[];
    tt=0
    
    for line in lines:
     #print line
     tt+=1
     #print tt
     if('[' in line) and ('snd_cwnd=' in line):
        src=get_str_btw(line, 'src=', 'dest')
        time_temp=get_str_btw(line, '] ', ' tcp')
        
        time_str=get_str_btw(time_temp, ' ', ':')
        #print time_str
        timestamp=float(time_str)
        #print timestamp
        if(len(src)>5 and src[5]=='2'):
          s1=src
          cwnd=get_str_btw(line, 'snd_cwnd=', ' ')
          #rwnd=get_str_btw(line, 'snd_cwnd=', ' ')
          T1.append(timestamp)
          C1.append(int(cwnd))
          t1+=1
        elif (len(src)>5 and src[7]=='1'):
          s2=src
          cwnd=get_str_btw(line, 'snd_cwnd=', ' ')
          T2.append(timestamp)
          C2.append(int(cwnd))
          t2+=1
        elif (len(src)>5 and src[7]=='2'):
          s3=src
          #print s2
          cwnd=get_str_btw(line, 'snd_cwnd=', ' ')
          T3.append(timestamp)
          C3.append(int(cwnd))
          t3+=1
        else:
          continue
     else:
        continue
#     if(len(T2)>0) and (len(T3)>0):
#       if (T2[0]>T3[0]):
#         T2 = [i-T3[0] for i in T2]
#         T3 = [i-T3[0] for i in T3]
#       else:
#         T2 = [i-T2[0] for i in T2]
#         T3 = [i-T2[0] for i in T3]

    return s1,C1,T1,s2,C2,T2,s3,C3,T3

def get_str_btw(s, f, b):
    
    par = s.partition(f)
    return (par[2].partition(b))[0][:]
    
def under_testing():
	#time.sleep(test_duration/(2*flip))
	for tim in range ((int)(flip-1)):
		print "\n",tim,'cutting link...',test_duration/(2*flip),
		print h1.intf('h1-eth0').ifconfig('down'),
		print 'link down\n'
		time.sleep(test_duration/(2*flip))

		print 'activating link...',test_duration/(2*flip),
		print h1.intf('h1-eth0').ifconfig('up'),
		print 'link up',
		time.sleep(test_duration/(2*flip))

	time.sleep(test_duration/3.0)
	time.sleep(5)

parser = argparse.ArgumentParser(description='manual to this script')
parser.add_argument("--d1", type=int, default=1)
parser.add_argument("--d2", type=int, default=1)
parser.add_argument("--b1", type=int, default=50)
parser.add_argument("--b2", type=int, default=50)
parser.add_argument("--l1", type=int, default=0)
parser.add_argument("--l2", type=int, default=0)
parser.add_argument("--m", type=int, default=1)
parser.add_argument("--s", type=int, default=0)
args = parser.parse_args()

se=args.s
subfolder_name='loss'
test_bandwith = True
cut_a_link = False
add_a_link = False
max_queue_size = 5000
test_duration = 10 # seconds
DELAY1=args.d1
DELAY2=args.d2
MPTCP_ON=args.m
BW1=args.b1
BW2=args.b2
LOSS1=args.l1
LOSS2=args.l2
flip=1

net = Mininet( cleanup=True )
key = "net.mptcp.mptcp_enabled"
value = MPTCP_ON
p = Popen("sysctl -w %s=%s" % (key, value), shell=True, stdout=PIPE, stderr=PIPE)
stdout, stderr = p.communicate()
print "stdout=",stdout,"stderr=", stderr

key = "net.ipv4.tcp_congestion_control"
if MPTCP_ON:
  value = "olia"
else:
  value = 'reno'
p = Popen("sysctl -w %s=%s" % (key, value), shell=True, stdout=PIPE, stderr=PIPE)
stdout, stderr = p.communicate()
print "stdout=",stdout,"stderr=", stderr
if (MPTCP_ON ==1):
  name="DELAY1=_"+str(DELAY1)+"_DELAY2=_"+str(DELAY2)+"_BW1=_"+str(BW1)+"_BW2=_"+str(BW2)+"_LOSS1=_"+str(LOSS1)+"_LOSS2=_"+str(LOSS2)+'_'+value+str(se)+"_MPTCP.txt"
else:
  name="DELAY1=_"+str(DELAY1)+"_DELAY2=_"+str(DELAY2)+"_BW1=_"+str(BW1)+"_BW2=_"+str(BW2)+"_LOSS1=_"+str(LOSS1)+"_LOSS2=_"+str(LOSS2)+'_'+value+str(se)+".txt"


os.system("echo 1 > /sys/kernel/debug/tracing/events/tcp/tcp_probe/enable")




h1 = net.addHost( 'h1', ip='10.0.1.1')
h2 = net.addHost( 'h2', ip='10.0.2.1')
s3 = net.addSwitch( 's3' )
c0 = net.addController( 'c0' )
#jitter

net.addLink( h1, s3, cls=TCLink , bw=BW1, delay=str(DELAY1)+'ms',loss=LOSS1)
net.addLink( h1, s3, cls=TCLink , bw=BW2, delay=str(DELAY2)+'ms',loss=LOSS2 )#max_queue_size=max_queue_size
#net.addLink( h1, s3,cls=TCLink,bw=1000,delay='5ms')
#net.addLink( h1, s3,cls=TCLink,bw=1000,delay='5ms')
net.addLink( h2, s3,cls=TCLink)
net.addLink( h2, s3,cls=TCLink)
h1.setIP('10.0.1.1', intf='h1-eth0')
h1.setIP('10.0.1.2', intf='h1-eth1')
h2.setIP('10.0.2.1', intf='h2-eth0')
h2.setIP('10.0.2.2', intf='h2-eth1')
time.sleep(1)
net.start()

time.sleep(1) # wait for net to startup (unless this, it might won't work...)
net.pingAll()
time.sleep(1)

#os.system("cat /sys/kernel/debug/tracing/trace_pipe > /home/lf/Desktop/dataset/"+name+' &')
if (True):
	print 'x'*40,'\n',' '*10,'START'
	print 'starting iperf server at',h2.IP()
	h2.cmd('iperf -s  -i 2   -m   > iperf_bandwith_server_log.txt & ') # server#-w 6553500 -l 6553500
	os.system("cat /sys/kernel/debug/tracing/trace_pipe > /home/lf/Desktop/dataset/"+name+' &')
	print 'starting iperf client at',h1.IP(),', connect to ',h2.IP()
	h1.cmd('iperf   -t '+str(test_duration)+' -i 2 -c '+h2.IP()+' > iperf_bandwith_client_log.txt &') # cliens
	#os.system("cat /sys/kernel/debug/tracing/trace_pipe > /home/lf/Desktop/dataset/"+name+' &')

	time.sleep(test_duration)
	time.sleep(5)
	
	fname = 'iperf_bandwith_server_log.txt'
	with open(fname, 'r') as f:  
    		lines = f.readlines() 
    		last_line = name[0:-4]+' '+lines[-2] 
    	with open(subfolder_name+'.txt','a') as f:
    		f.write(last_line)
	print "\niperf client response:"
	print h1.cmd('cat iperf_bandwith_client_log.txt')
	
	print "\niperf server response:"
	print h2.cmd('cat iperf_bandwith_server_log.txt')


net.stop()

time.sleep(1)

shutil.copy('/home/lf/Desktop/dataset/'+name, '/home/lf/Desktop/all/'+subfolder_name)
s1,C1,T1,s2,C2,T2,s3,C3,T3 = loadData('/home/lf/Desktop/all/'+subfolder_name+'/'+name)
title_str=name[0:31]+'\n'+name[31:-4]
plt.title(title_str,fontsize=16)
plt.xlabel('Time/s',fontsize=16)
plt.ylabel('Congestion window',fontsize=16)

T2.sort()
T3.sort()

print len(T2),len(T3),len(C2),len(C3)

plt.plot(T3,C3,linewidth=1) 
plt.plot(T2,C2,'--',linewidth=1) 
plt.legend(( s2, s3), loc='upper right')
plt.savefig('/home/lf/Desktop/all/'+subfolder_name+'/'+name[0:-4]+'.png',dpi=200)

print time.time()-be





#print p.pid
#os.system("echo 1 > /sys/kernel/debug/tracing/trace")
#p1=Popen("cat /sys/kernel/debug/tracing/trace_pipe > /home/lf/Desktop/dataset/"+name+' &',shell=True,stdout=PIPE, stderr=PIPE)# shell=True
#	if cut_a_link:
#		print "\n",'cutting link...',
#		print h1.intf('h1-eth0').ifconfig('down'),
#		print 'link down\n'
#	time.sleep(test_duration/3.0)
#	if add_a_link:
#		print h1.intf('h1-eth0').ifconfig('up'),
#		print 'adding a new link...',
#		net.addLink( h1, s3, cls=TCLink , bw=50, delay='5ms', max_queue_size=max_queue_size )
#		s3.attach('s3-eth5')
#		h1.setIP('10.0.1.3', intf='h1-eth2')
#		print 'link added\n'
#		
#	time.sleep(test_duration/3.0)
	
	
#	time.sleep(5) # wait (a bit) to finish


#print T2,C2


#plt.plot(T1,C1) 
        #h1.cmd('iperf  -u -b 1000m -n 1000M -i 2 -c '+h2.IP()+' > iperf_bandwith_client_log.txt &') # cliens
	
	#under_testing()
		#h1.cmd('tcpdump -XX -n -i h1-eth0 -w 1.pcap &') # client
	#h1.cmd('tcpdump -XX -n -i h1-eth1 -w 2.pcap &') # c2

#print "\n"," "*5,"#"*40,"\n"," "*10,"STARTING\n"
#test_started_timestamp = time.time()

#if MPTCP_ON:
#  net.addLink( h1, s3, cls=TCLink , bw=BW2, delay=str(DELAY2)+'ms',loss=LOSS2 )
#  h1.setIP('10.0.1.2', intf='h1-eth1')
