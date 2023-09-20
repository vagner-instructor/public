# <snippet-begin 0_apt-upgrade.sh>
aptUpgrade () {
  debug "Upgrading system"
  checkAptLock

  # If we run in non-interactive mode, make sure we do not stop all of a sudden
  if [[ "${PACKER}" == "1" || "${UNATTENDED}" == "1" ]]; then
    export DEBIAN_FRONTEND=noninteractive
    export DEBIAN_PRIORITY=critical
    sudo -E apt-get -qy -o "Dpkg::Options::=--force-confdef" -o "Dpkg::Options::=--force-confold" upgrade
    sudo -E apt-get -qy autoclean
  else
    sudo apt-get upgrade -qy
  fi
}
# <snippet-end 0_apt-upgrade.sh>