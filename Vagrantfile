# -*- mode: ruby -*-
# vi: set ft=ruby :
Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/xenial64"
  config.vm.network "public_network"
  config.vm.synced_folder ".", "/var/www/rank"
  config.vm.provision "shell", inline: <<-SHELL
    sudo add-apt-repository -y ppa:jonathonf/python-3.6
    sudo apt-get update
    sudo apt-get install -y python3.6 python3-pip nginx
    sudo pip3 install sqlalchemy
  SHELL
end
