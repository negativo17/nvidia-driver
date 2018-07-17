#!/bin/sh
set -e

VERSION=${VERSION:-390.77}
DL_SITE=${DL_SITE:-http://us.download.nvidia.com/XFree86}
TEMP_UNPACK=${TEMP_UNPACK:-temp}

get_run_file() {
    printf "Downloading installer for ${VERSION} ${ARCH}... "
    [[ -f $RUN_FILE ]] || wget -c -q ${DL_SITE}/${PLATFORM}/${VERSION}/$RUN_FILE
    printf "OK\n"
}

extract_run_file() {
    sh ${RUN_FILE} --extract-only --target ${TEMP_UNPACK}
}

create_tarball() {
    printf "Creating tarballs for ${VERSION} ${ARCH}... "

    KMOD=nvidia-kmod-${VERSION}-${ARCH}
    DRIVER=nvidia-driver-${VERSION}-${ARCH}
    mkdir ${KMOD} ${DRIVER}

    cd ${TEMP_UNPACK}

    # Compiled from source
    rm -f \
        nvidia-xconfig* \
        nvidia-persistenced* \
        nvidia-modprobe* \
        libnvidia-gtk* nvidia-settings* \
        libGLESv1_CM.so.* libGLESv2.so.* libGL.la libGLdispatch.so.* libOpenGL.so.* libGLX.so.* libGL.so.1* libEGL.so.1* \
        libnvidia-egl-wayland.so.* \
        libOpenCL.so.1*

    # Non GLVND libraries
    rm -f libGL.so.${VERSION} libEGL.so.${VERSION}

    # Useless with packages
    rm -f nvidia-installer* .manifest make* mk* tls_test*

    # useless on modern distributions
    rm -f libnvidia-wfb*

    # Use correct tls implementation
    mv -f tls/libnvidia-tls.so* .
    rm -fr tls

    mv kernel ../${KMOD}/
    mv * ../${DRIVER}/

    cd ..
    rm -fr ${TEMP_UNPACK}

    tar --remove-files -cJf ${KMOD}.tar.xz ${KMOD}
    tar --remove-files -cJf ${DRIVER}.tar.xz ${DRIVER}

    printf "OK\n"
}

ARCH=i386
PLATFORM=Linux-x86
RUN_FILE=NVIDIA-${PLATFORM}-${VERSION}.run
get_run_file
extract_run_file
create_tarball

ARCH=x86_64
PLATFORM=Linux-${ARCH}
RUN_FILE=NVIDIA-${PLATFORM}-${VERSION}-no-compat32.run
get_run_file
extract_run_file
create_tarball
