#!/bin/sh -x
if id | grep -qv uid=0; then
    echo "Must run setup as root"
    exit 1
fi

create_socket_dir() {
    local dirname="$1"
    local ownergroup="$2"
    local perms="$3"

    mkdir -p $dirname
    chown $ownergroup $dirname
    chmod $perms $dirname
}

set_perms() {
    local ownergroup="$1"
    local perms="$2"
    local pn="$3"

    chown $ownergroup $pn
    chmod $perms $pn
}

rm -rf /jail
mkdir -p /jail
cp -p index.html /jail

./chroot-copy.sh zookd /jail
./chroot-copy.sh zookfs /jail

#./chroot-copy.sh /bin/bash /jail

./chroot-copy.sh /usr/bin/env /jail
./chroot-copy.sh /usr/bin/python /jail

# to bring in the crypto libraries
./chroot-copy.sh /usr/bin/openssl /jail

mkdir -p /jail/usr/lib /jail/usr/lib/i386-linux-gnu /jail/lib /jail/lib/i386-linux-gnu
cp -r /usr/lib/python2.7 /jail/usr/lib
cp /usr/lib/i386-linux-gnu/libsqlite3.so.0 /jail/usr/lib/i386-linux-gnu
cp /lib/i386-linux-gnu/libnss_dns.so.2 /jail/lib/i386-linux-gnu
cp /lib/i386-linux-gnu/libresolv.so.2 /jail/lib/i386-linux-gnu
cp -r /lib/resolvconf /jail/lib

mkdir -p /jail/usr/local/lib
cp -r /usr/local/lib/python2.7 /jail/usr/local/lib

mkdir -p /jail/etc
cp /etc/localtime /jail/etc/
cp /etc/timezone /jail/etc/
cp /etc/resolv.conf /jail/etc/

mkdir -p /jail/usr/share/zoneinfo
cp -r /usr/share/zoneinfo/America /jail/usr/share/zoneinfo/

create_socket_dir /jail/echosvc 61010:61010 755
create_socket_dir /jail/authsvc 61015:61015 755

mkdir -p /jail/tmp
chmod a+rwxt /jail/tmp

mkdir -p /jail/dev
mknod /jail/dev/urandom c 1 9

cp -r zoobar /jail/
rm -rf /jail/zoobar/db

#chown -hR 61013:61013 /jail/zoobar/ #sets permissions for zoofs to the folder and subfolders
#chown 61015:61015 /jail/zoobar/auth-server.py

python /jail/zoobar/zoodb.py init-person
python /jail/zoobar/zoodb.py init-transfer
python /jail/zoobar/zoodb.py init-cred

#chown -hR 61012:61012 /jail/zoobar/db/transfer/transfer.db
#chown -hR 61012:61012 /jail/zoobar/db/person/person.db # sets rights to the databases
#chmod 770 /jail/zoobar/db
#chown 61012:61012 /jail/zoobar/db/person
#chmod 770 /jail/zoobar/db/person
#chmod 770 /jail/zoobar/db/person/person.db
#chown 61012:61012 /jail/zoobar/db/transfer
#chmod 660 /jail/zoobar/db/transfer
#chown -hR 61015:61015 /jail/zoobar/db/cred/cred.db
#chown 61015:61015 /jail/zoobar/db/cred
#chmod 700 /jail/zoobar/db/cred
#chmod 600 /jail/zoobar/db/cred/cred.db

chown 61012:61012 /jail/zoobar/db/person/
chmod 330 /jail/zoobar/db/person
chown 61015:61015 /jail/zoobar/db/cred/
chmod 300 /jail/zoobar/db/cred/
chown 61012:61012 /jail/zoobar/db/transfer/
chmod 330 /jail/zoobar/db/transfer

chown 61012:61012 /jail/zoobar/db/person/person.db
chmod 660 /jail/zoobar/db/person/person.db
chown 61015:61015 /jail/zoobar/db/cred/cred.db
chmod 600 /jail/zoobar/db/cred/cred.db
chown 61012:61012 /jail/zoobar/db/transfer/transfer.db
chmod 660 /jail/zoobar/db/transfer/transfer.db

# TODO: User rights, works with chmod -R 777 but not without the rights
# they should
#chmod -R 777 /jail/zoobar/db/ 
#chmod -R 777 /jail/zoobar/db/person
#set_perms 61012 770 /jail/zoobar/db/person/person.db 

chown 61014:61014 /jail/zoobar/index.cgi



