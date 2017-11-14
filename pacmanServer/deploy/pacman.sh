#!/usr/bin/env bash

function service_config() {
echo "# Pacman Service"
echo
echo "[Unit]"
echo "Description=Multiplayer cyber-physical pacman game"
echo "Documentation=http://apollo.ele.tue.nl/fputter/pacman"
echo "Requires=network.target"
echo "After=network.target"
echo
echo "[Service]"
echo "Type=forking"
echo "User=${1}"
echo "WorkingDirectory=~"
echo "ExecStart=${2}/deploy/pacman.sh start"
echo "ExecStop=${2}/deploy/pacman.sh stop"
echo "Restart=always"
echo
echo "[Install]"
echo "WantedBy=multi-user.target"
}

INSTALL_DIR="$( cd "$(dirname "$0")/.." ; pwd -P )"
USER=`ls -ld $0 | awk '{print $3}'`

case "$1" in
  start)
    echo "Starting pacman service..."
    sudo xvfb-run sudo PYTHONPATH=${INSTALL_DIR} python ${INSTALL_DIR}/pacman.py &
    ;;
  stop)
    pid=`ps -eo uname:20,pid,unit,cmd | grep pacman.service | grep ${USER} | grep python | grep ${INSTALL_DIR}/pacman.py | awk '{ print $2 }'`
    case ${pid} in
      ''|*[!0-9]*)
        echo "Nothing to do. No pacman service is running."
        ;;
      *)
        echo "Sending SIGINT to ${pid} ..."
        sudo kill -SIGINT ${pid}
        ;;
    esac
    ;;
  install)
    echo "Gracefull replacement of existing pacman service..."
    sudo systemctl stop pacman.service 2>&1 | sed 's/^/  /'
    sudo systemctl disable pacman.service 2>&1 | sed 's/^/  /'
    sudo rm /etc/systemd/system/pacman.service 2>&1 | sed 's/^/  /'
    sudo systemctl daemon-reload 2>&1 | sed 's/^/  /'
    echo
    echo "Creating pacman systemd service..."
    service_config ${USER} ${INSTALL_DIR} | sudo tee /etc/systemd/system/pacman.service > /dev/null
    sudo systemctl enable pacman.service 2>&1 | sed 's/^/  /'
    sudo systemctl start pacman.service 2>&1 | sed 's/^/  /'
    sudo systemctl status pacman.service 2>&1 | sed 's/^/  /'
    ;;
  remove)
    echo "Uninstalling pacman service..."
    sudo systemctl stop pacman.service 2>&1 | sed 's/^/  /'
    sudo systemctl disable pacman.service 2>&1 | sed 's/^/  /'
    sudo rm /etc/systemd/system/pacman.service 2>&1 | sed 's/^/  /'
    sudo systemctl daemon-reload 2>&1 | sed 's/^/  /'
    ;;
  *)
    echo "Usage: pacman.sh {install|remove|start|stop}"
    exit 1
    ;;
esac

exit 0
