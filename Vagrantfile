# -*- mode: ruby -*-
# vi: set ft=ruby :
Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/xenial64"
  config.vm.network "public_network"
  config.vm.synced_folder ".", "/var/www/rank"
  config.vm.provision "shell", inline: <<-SHELL
    bash -ex /var/www/rank/misc/provision.sh
  SHELL
end
