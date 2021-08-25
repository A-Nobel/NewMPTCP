#!/bin/bash
echo "begin"
#sudo sh run.sh
chmod u+x run1.sh
#sh run.sh

for((i=0;i<=99;i+=1));  
do   
sudo gnome-terminal --title="${i}"  -x bash -c "sh run1.sh ${i}" ;sleep 240;
done  


echo "over"
exit 0
