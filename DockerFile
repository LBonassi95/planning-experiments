FROM ubuntu:latest

COPY install-apptainer-ubuntu.sh .

RUN mkdir /app

RUN bash install-apptainer-ubuntu.sh 1.0.3 1.18.3 \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
    bash-completion \
    ca-certificates \
    git \
    libseccomp-dev \
    python3 \
    python3-pip \
    python3-venv \
    tzdata \
    unzip \
    vim \
    wget \
    build-essential \
    gcc-x86-64-linux-gnu \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*  
    
RUN pip3 install --upgrade pip
RUN pip3 install setuptools
RUN pip3 install tqdm \
    click\
    pandas\
    tabulate
#creazione utenti
RUN apt-get update && apt-get install -y python3 && apt-get install tar 
RUN apt-get update && \
    apt-get install -y sudo

# Crea un utente temporaneo e aggiungilo al gruppo sudo
RUN useradd -m -G sudo myuser

# Configura sudo per l'utente
RUN echo 'myuser ALL=(ALL:ALL) NOPASSWD:ALL' > /etc/sudoers.d/myuser

# Cambia l'utente predefinito a myuser
USER myuser

# Cambia il working directory
WORKDIR /home/myuser

USER root
#set permessi
RUN apt-get update && \
    apt-get install -y sudo && \
    rm -rf /var/lib/apt/lists/* && \
    usermod -aG sudo myuser && \
    echo 'myuser ALL=(ALL:ALL) NOPASSWD:ALL' > /etc/sudoers.d/myuser && \
    usermod -u 1000 myuser && \
    groupmod -g 1000 myuser

# Cambia utente predefinito
USER myuser

RUN cd /home/myuser && \
    git clone https://github.com/MattiaTanchis/planning-experiments.git && \
    cd planning-experiments && \
    pip3 install . && \ 
    sudo chmod -R  734 ../planning-experiments

CMD ["tail", "-f", "/dev/null"]





# Esegui il comando per mantenere il container in esecuzione (ad esempio, tail -f /dev/null)


# NOTE: una volta lanciato il container anche con installato python è necessario installare apptainer e per far ciò: 
# 1) installare Go
#necessario scaricare e installare versione Go > 1.19 :
#scaricare la verisione wget https://dl.google.com/go/go1.21.linux-amd64.tar.gz (da errore da container) 
#quindi ho scaricato su locale e ho copiato. una volta fatto ciò eseguire mv go /usr/local dopo aver unzippato la cartella
#infine eseguire i seguenti comandi : export GOROOT=/usr/local/go, export GOPATH=$HOME/go, export PATH=$GOPATH/bin:$GOROOT/bin:$PATH
#   
# 2) Installare apptainer
#   eseguire git clone : git clone https://github.com/apptainer/apptainer.git
#   cd apptainer, successivamente è necessario eseguire questi comandi ./mconfig, cd $(/bin/pwd)/builddir, make, sudo make install
# link installazione go : https://levelup.gitconnected.com/installing-go-on-ubuntu-b443a8f0eb55
# link installazione apptainer: https://github.com/apptainer/apptainer/blob/main/INSTALL.md
# 3) Avvio container
#   è necessario lanciare il container docker con il comando "docker run --privileged nome container "
#
#
