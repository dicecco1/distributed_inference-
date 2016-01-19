cpu_list=$(heat output-show caffe server_cpu_ips)
cpu_list="$(echo $cpu_list | sed -e 's/\"//g' -e 's/\[//g' -e 's/\]//g' -e 's/\,//g')"

fpga_list=$(heat output-show caffe server_fpga_ips)
fpga_list="$(echo $fpga_list | sed -e 's/\"//g' -e 's/\[//g' -e 's/\]//g' -e 's/\,//g')"

echo List of CPU VM IPs
echo $cpu_list
echo List of FPGA VM IPs
echo $fpga_list

echo CPU_LIST > ip_list.txt
echo $cpu_list >> ip_list.txt
echo FPGA_LIST >> ip_list.txt
echo $fpga_list >> ip_list.txt

scp -i dicecco1key.pem ip_list.txt ubuntu@$1:~/.

for ip in $cpu_list
do
    echo SSH IP: $ip
    ssh -i dicecco1key.pem centos@$ip "killall -u centos python; cd ~/fpga_caffe; screen -d -m bash -c 'source ~/.bashrc; nohup python server.py 0 $1'; exit;"
done

for ip in $fpga_list
do
    echo SSH IP: $ip
    ssh -i dicecco1key.pem centos@$ip "killall -u centos python; cd ~/fpga_caffe; screen -d -m bash -c 'source ~/.bashrc; nohup python server.py 1 $1'; exit;"
done
