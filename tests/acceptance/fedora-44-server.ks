text --non-interactive
lang en_US.UTF-8
keyboard us
timezone UTC --utc
network --device=enp0s2 --bootproto=dhcp --activate --hostname=ride-server-pilot
url --url=https://download.fedoraproject.org/pub/fedora/linux/releases/44/Everything/x86_64/os/
rootpw --lock
user --name=ride-test --groups=wheel --lock
firewall --enabled --service=ssh
selinux --enforcing
ignoredisk --only-use=vda
zerombr
clearpart --all --initlabel --disklabel=gpt --drives=vda
autopart --type=plain
bootloader --append="console=ttyS0"
firstboot --disable
reboot --eject

%packages
@^server-product-environment
cloud-init
openssh-server
sudo
jq
%end

%post
systemctl enable sshd
%end
