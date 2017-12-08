# -*- mode: ruby -*-
# vi: set ft=ruby :
Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/xenial64"
  config.vm.box_check_update = false
  config.vm.network "public_network"
  config.vm.synced_folder ".", "/var/www/rank"
  config.vm.provision "shell", inline: <<-SHELL
    set -ex
    sudo su

    ln -f -s /var/www/rank/misc/ubuntu.list /etc/apt/sources.list
    mkdir -p /root/.pip
    ln -f -s /var/www/rank/misc/pip.conf /root/.pip/pip.conf

    apt-get update
    apt-get -y install python3-pip
    pip3 install Fabric3

    cd /var/www/rank
    fab provision
  SHELL
end
