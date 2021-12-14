#!/bin/bash

# NOTE: heavy downloads can be provided in the *CACHE* directory set here:
# (e.g. OMERO.server.zip, Ice, ...)
CACHE="/tmp/omero-install-cache"

### OMERO apt dependencies ###

add-apt-repository --yes ppa:openjdk-r/ppa
apt-get update -q

apt-get -y install \
    unzip \
    wget \
    bc \
    multitail \
    software-properties-common \
    openjdk-11-jre \
    unzip \
    wget \
    python3 \
    python3-venv \
    build-essential \
    db5.3-util \
    libbz2-dev \
    libdb++-dev \
    libdb-dev \
    libexpat-dev \
    libmcpp-dev \
    libssl-dev \
    mcpp \
    zlib1g-dev \
    postgresql

### OMERO apt dependencies ###

ICE_ZIP_URI="https://github.com/ome/zeroc-ice-ubuntu2004/releases/download/0.2.0/ice-3.6.5-0.2.0-ubuntu2004-amd64.tar.gz"
ICE_ZIP=$CACHE/ice-3.6.5-0.2.0-ubuntu2004-amd64.tar.gz
if ! [ -f "$ICE_ZIP" ]; then
    wget -q $ICE_ZIP_URI -O $ICE_ZIP
fi
tar xf $ICE_ZIP
mv ice-3.6.5-0.2.0 ice-3.6.5
mv ice-3.6.5 /opt
echo /opt/ice-3.6.5/lib64 >/etc/ld.so.conf.d/ice-x86_64.conf
ldconfig

cat - >/etc/profile.d/omero-server.sh <<"EOF"
# OMERO related settings
export ICE_HOME=/opt/ice-3.6.5
export SLICEPATH="$ICE_HOME/slice"
VENV_SERVER=/opt/omero/server/venv3
export PATH="$VENV_SERVER/bin:$ICE_HOME/bin:$PATH"
EOF

systemctl start postgresql.service

useradd --system --create-home --shell /bin/bash omero-server
# NOTE: the omero user doesn't have a password yet
chmod a+X ~omero-server

# create the settings.env file to be sourced:
SETTINGS_ENV=~omero-server/.settings.env
cat - >$SETTINGS_ENV <<"EOF"
OMERO_DB_USER=db_user
OMERO_DB_PASS=db_password
OMERO_DB_NAME=omero_database
OMERO_ROOT_PASS=omero_root_password
OMERO_DATA_DIR=/OMERO

export OMERO_DB_USER OMERO_DB_PASS OMERO_DB_NAME OMERO_ROOT_PASS OMERO_DATA_DIR

export PGPASSWORD="$OMERO_DB_PASS"

# Location of the OMERO.server
export OMERODIR=/opt/omero/server/OMERO.server

# Location of the virtual environment for omero-py
VENV_SERVER=/opt/omero/server/venv3

export PATH=$VENV_SERVER/bin:$PATH
EOF

source $SETTINGS_ENV

mkdir -p "$OMERO_DATA_DIR"
chown omero-server "$OMERO_DATA_DIR"

### postgres setup ###
#
echo "CREATE USER $OMERO_DB_USER PASSWORD '$OMERO_DB_PASS'" | su - postgres -c psql
su - postgres -c "createdb -E UTF8 -O '$OMERO_DB_USER' '$OMERO_DB_NAME'"

psql -P pager=off -h localhost -U "$OMERO_DB_USER" -l
#
### postgres setup ###

### Python virtual environment setup ###
#
python3 -mvenv $VENV_SERVER
$VENV_SERVER/bin/pip install --upgrade pip wheel
#
### Python virtual environment setup ###

### Python dependencies installation ###
#
ICE_WHEEL_URI="https://github.com/ome/zeroc-ice-ubuntu2004/releases/download/0.2.0/zeroc_ice-3.6.5-cp38-cp38-linux_x86_64.whl"
ICE_WHEEL="$CACHE/zeroc_ice-3.6.5-cp38-cp38-linux_x86_64.whl"
if ! [ -f "$ICE_WHEEL" ]; then
    wget -q $ICE_WHEEL_URI -O $ICE_WHEEL
fi
$VENV_SERVER/bin/pip install $ICE_WHEEL

# Install server dependencies
$VENV_SERVER/bin/pip install omero-server[default]
#
### Python dependencies installation ###

### OMERO server package installation ###
#
SERVER=https://downloads.openmicroscopy.org/omero/5.6/server-ice36.zip
SERVER_ZIP="$CACHE/OMERO.server-ice36.zip"
if ! [ -f "$SERVER_ZIP" ]; then
    wget -q $SERVER -O $SERVER_ZIP
fi
cd /opt/omero/server
unzip -q $SERVER_ZIP

# change ownership of the folder
chown -R omero-server OMERO.server-*
ln -s OMERO.server-*/ OMERO.server
#
### OMERO server package installation ###

### OMERO system account setup ###
#
cat - >>~omero-server/.profile <<"EOF"

# read OMERO specific environment variables:
. "$HOME/.settings.env"
EOF
#
### OMERO system account setup ###

su - omero-server --command='
omero config set omero.data.dir "$OMERO_DATA_DIR"
omero config set omero.db.name "$OMERO_DB_NAME"
omero config set omero.db.user "$OMERO_DB_USER"
omero config set omero.db.pass "$OMERO_DB_PASS"
omero db script -f $OMERODIR/db.sql --password "$OMERO_ROOT_PASS"
psql -h localhost -U "$OMERO_DB_USER" "$OMERO_DB_NAME" < $OMERODIR/db.sql

omero certificates
'

# su - omero-server --command='omero admin start'

cat - >/etc/systemd/system/omero.service <<"EOF"
[Unit]
Description=OMERO.server
# After: ensures this service starts after the dependency, but only if the
# dependency is also started (PostgreSQL may be on a different server)
After=postgresql-9.4.service
After=postgresql-9.5.service
After=postgresql-9.6.service
After=postgresql-10.service
After=postgresql-11.service
After=network.service

[Service]
User=omero-server
WorkingDirectory=/opt/omero
Type=forking
Restart=no
RestartSec=10
# Allow up to 5 min for start/stop
TimeoutSec=300
Environment="PATH=/opt/ice-3.6.5/bin:/opt/omero/server/venv3/bin:/usr/local/bin:/bin:/usr/bin:/usr/local/sbin:/usr/sbin"
Environment="OMERODIR=/opt/omero/server/OMERO.server"
ExecStart=/opt/omero/server/venv3/bin/omero admin start
ExecStop=/opt/omero/server/venv3/bin/omero admin stop
# If you want to enable in-place imports uncomment this:
#UMask=0002

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload

echo "Installation complete, starting OMERO service..."
systemctl start omero.service

echo "Done."
