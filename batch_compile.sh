#!/bin/bash
mkdir -p /ko_output
BUILD_VERSION=$(cat LKM/src/init.c | grep MODULE_VERSION | awk -F '"' '{print $2}')
KO_NAME=$(grep "MODULE_NAME" ./LKM/Makefile | grep -m 1 ":=" | awk '{print $3}')
UBUNTU_OR_DEBIAN_FLAG=$(cat /etc/*release | grep -iE "ubuntu|debian")
FLAG_SIZE=${#UBUNTU_OR_DEBIAN_FLAG}

if [ $FLAG_SIZE -ne 0 ]; then
    echo "this is ubuntu or debian"
    FILES=/lib/modules/*
else
    echo "this is centos"
    FILES=/usr/src/kernels/*
fi

for f in $FILES
do
    set -e
    set -o xtrace
    KV="$(basename -- $f)"
    echo "Processing $KV file..."
    KVERSION=$KV  make -C ./LKM clean || true
    BATCH=true KVERSION=$KV   make  -C ./LKM -j all || true
    sha256sum  ./LKM/${KO_NAME}.ko | awk '{print $1}' > /ko_output/${KO_NAME}_${BUILD_VERSION}_${KV}_amd64.sign  || true
    mv ./LKM/${KO_NAME}.ko /ko_output/${KO_NAME}_${BUILD_VERSION}_${KV}_amd64.ko || true
    KVERSION=$KV  make -C ./LKM clean || true
done
