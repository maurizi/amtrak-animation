# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "precise64"

  config.vm.network :forwarded_port, guest: 80, host: 6060

  config.vm.synced_folder ".", "/usr/local/amtrak/"

  config.vm.provision "shell", inline: "sudo apt-get install -qy python-apt"
  config.vm.provision "ansible" do |ansible|
      ansible.playbook = "playbook.yml"
      ansible.sudo = true
      ansible.verbose = true
  end

  config.vm.provider :virtualbox do |vb, override|
    override.vm.box_url = "http://files.vagrantup.com/precise64.box"
  end
  config.vm.provider :lxc do |lxc, override|
    override.vm.box_url = "http://bit.ly/vagrant-lxc-precise64-2013-07-12"
  end
end
