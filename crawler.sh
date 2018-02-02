#/bin/bash
cd /home/mango/.virtualenvs/crawler3/bin/
source ./activate
cd /home/mango/workspace/python/crawler_csdn_huaban/
python3.6 __main__.py
git add ./
DATE=$(date +%Y-%m-%d_%H:%M)
git commit -m $DATE
git push origin master