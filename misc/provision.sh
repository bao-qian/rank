set -ex

ln -f -s /var/www/rank/misc/ubuntu.list /etc/apt/sources.list
mkdir -p /root/.pip
ln -f -s /var/www/rank/misc/pip.conf /root/.pip/pip.conf

sudo apt-get update
sudo add-apt-repository -y ppa:jonathonf/python-3.6
sudo apt-get update
sudo apt-get install -y python3.6 python3-pip nginx
sudo -H python3.6 -m pip install sqlalchemy pyquery

sudo ln -f -s /var/www/rank/misc/rank.service /etc/systemd/system/rank.service
sudo ln -f -s /var/www/rank/misc/rank.timer /etc/systemd/system/rank.timer
sudo systemctl daemon-reload
sudo systemctl restart rank.service
sudo systemctl restart rank.timer

rm -f /etc/nginx/sites-enabled/*
sudo ln -f -s /var/www/rank/misc/nginx.conf /etc/nginx/sites-enabled/rank.conf
sudo systemctl restart nginx

echo 'full url:'
hostname -I | sed -e 's/ /\n/g' | sed -e 's/^/http:\/\//g'