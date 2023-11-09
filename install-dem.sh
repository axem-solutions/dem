#!/bin/bash

GREEN='\033[0;32m'
RED='\033[0;31m'

installPython(){
    required_version="3.10"
    if command -v python3 &>/dev/null; then
        python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')
        if python3 -c "import sys; sys.exit(not (sys.version_info >= (3, 10)))" &>/dev/null; then
            echo "Python $python_version is equal to or greater than 3.10."            
        else                    
            echo -e "${RED} Python 3.10 is not installed, at least Python version 3.10 is required"    
            exit -1
        fi
    else
        echo -e "${RED} Python 3 is not installed. Please install at least Python 3.10"
        exit -1
    fi
}

installDocker(){
    sudo apt update
    sudo apt install -y docker.io
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker $USER
    echo -e "${GREEN} Restart your system to finish installation!"

}

installDem(){
    sudo apt install -y pip
    pip install axem-dem --break-system-packages    
}



#main run
installPython
installDem
installDocker

