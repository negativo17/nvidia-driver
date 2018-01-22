#!/bin/sh -x
set -e

VERSION=384.90
#DL_SITE=ftp://download.nvidia.com/XFree86
DL_SITE=http://us.download.nvidia.com/XFree86

create_tarball() {
    KMOD=nvidia-kmod-${VERSION}-${ARCH}
    DRIVER=nvidia-driver-${VERSION}-${ARCH}

    sh $RUN_FILE --extract-only --target temp
    mkdir ${KMOD} ${KMOD_MULTI} ${DRIVER}

    cd temp

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
    rm -fr temp

    tar --remove-files -cJf ${KMOD}.tar.xz ${KMOD}
    tar --remove-files -cJf ${DRIVER}.tar.xz ${DRIVER}

    rm -f $RUN_FILE
}

ARCH=i386
RUN_FILE=nvidia-${VERSION}-${ARCH}.run
DIST_FILE=NVIDIA-Linux-x86-${VERSION}.run
if [ -f $DIST_FILE ]; then
    ln -s $DIST_FILE $RUN_FILE
else
    wget -c ${DL_SITE}/Linux-x86/${VERSION}/$DIST_FILE -O $RUN_FILE
fi
create_tarball

ARCH=x86_64
RUN_FILE=nvidia-${VERSION}-${ARCH}.run
DIST_FILE=NVIDIA-Linux-${ARCH}-${VERSION}-no-compat32.run
if [ -f $DIST_FILE ]; then
    ln -s $DIST_FILE $RUN_FILE
else
    wget -c ${DL_SITE}/Linux-${ARCH}/${VERSION}/$DIST_FILE -O $RUN_FILE
fi
create_tarball

