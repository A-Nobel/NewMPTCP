#!/bin/bash
echo "subbegin"

#chmod u+x run.sh
#sh run.sh
for((ss=0;ss<=9;ss+=1));  
do   
python jianf1.py --s ${ss} --l1 $1 --m 0;wait;
done  

find /home/lf/Desktop/dataset -name '*.txt' -type f -print -exec rm -rf {} \;
find /home/lf/Desktop/all/loss -name '*.txt' -type f -print -exec rm -rf {} \;
echo "subover"
exit 0
