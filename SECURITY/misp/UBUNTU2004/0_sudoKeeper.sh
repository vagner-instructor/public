# <snippet-begin 0_sudoKeeper.sh>
# check if sudo is installed
checkSudoKeeper () {
  echo "Checking for sudo and installing etckeeper"
  if [[ ! -f $(which sudo) ]]; then
    echo "Please enter your root password below to install etckeeper"
    su -c "apt install etckeeper -y"
    echo "Please enter your root password below to install sudo"
    su -c "apt install sudo -y"
    echo "Please enter your root password below to install sudo"
    su -c "apt install curl -y"
    echo "Please enter your root password below to add ${MISP_USER} to sudo group"
    su -c "/usr/sbin/adduser ${MISP_USER} sudo"
    echo "We added ${MISP_USER} to group sudo and now we need to log out and in again."
    exit
  else
    sudo apt update
    sudo apt install etckeeper -y
  fi
}
# <snippet-end 0_sudoKeeper.sh>