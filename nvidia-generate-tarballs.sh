#!/bin/bash

set -e

VERSION=${VERSION:-390.48}
DL_SITE=${DL_SITE:-http://us.download.nvidia.com/XFree86}
TEMP_UNPACK=${TEMP_UNPACK:-temp}
X64_ONLY=${X64_ONLY:-0}

get_run_file() {
    printf "Downloading installer for ${VERSION} ${ARCH}... " >&2
    wget -N -c -q ${DL_SITE}/${PLATFORM}/${VERSION}/$RUN_FILE || return $?
    printf "OK\n" >&2
}

extract_run_file() {
    local dest_dir="$1" src_file="$PWD/$RUN_FILE"
    local fname="${src_file##*/}"
    local dest_subdir="${fname%.run}"
    dest_dir="$dest_dir/$dest_subdir"

    if [ -e "$dest_dir" ]; then
        rm -rf "$dest_dir"
    fi

    sh "$src_file" --extract-only --target "$dest_dir" >&2 || return $?
    echo "$dest_dir"
}

create_kmod_tarball() {
    local src_dir="$1"
    local kmod_name="nvidia-kmod-${VERSION}-${ARCH}"
    printf "Creating kernel module tarball for ${VERSION} ${ARCH}... " >&2

    tar -cJv -f "${kmod_name}.tar.xz.tmp" \
        --transform "s!^!${kmod_name}/!S" \
        --show-transformed-names \
        -C "$src_dir" kernel || return $?
    mv "${kmod_name}.tar.xz"{.tmp,}
}

create_driver_tarball() {
    local src_dir="$1" prefix="$2"
    local driver_name="nvidia-driver-${VERSION}-${ARCH}"

    printf "Creating driver tarball for ${VERSION} ${ARCH}... " >&2

    set -f
    local -a exclude=(
        # Compiled from source
        nvidia-xconfig* \
        nvidia-persistenced* \
        nvidia-modprobe* \
        libnvidia-gtk* nvidia-settings* \
        libGLESv1_CM.so.* libGLESv2.so.* libGL.la libGLdispatch.so.* libOpenGL.so.* libGLX.so.* libGL.so.1* libEGL.so.1* \
        libnvidia-egl-wayland.so.* \
        libOpenCL.so.1*
        # Non GLVND libraries
        libGL.so.${VERSION} libEGL.so.${VERSION}
        # Useless with packages
        nvidia-installer* .manifest make* mk* tls_test*
        # useless on modern distributions
        libnvidia-wfb*
        # kmod has its own tarball
        kernel
        # 32-bit on 64-bit package is handled separately
        32
    )
    set +f

    tar -cJv -f "${driver_name}.tar.xz.tmp" \
        --anchored $(printf -- '--exclude=./%s ' "${exclude[@]}") \
        --transform 's!^\./tls/!./!S' \
        --transform "s!^\\./!${driver_name}/!S" \
        --show-transformed-names \
        -C "$src_dir/$prefix/" . || return $?
    mv "${driver_name}.tar.xz"{.tmp,}
}

if [ "$X64_ONLY" -ne 1 ]; then
    ARCH=i386
    PLATFORM=Linux-x86
    RUN_FILE=NVIDIA-${PLATFORM}-${VERSION}.run
    if get_run_file; then
        src_dir=$(extract_run_file "$TEMP_UNPACK")
        create_kmod_tarball "$src_dir"
        create_driver_tarball "$src_dir"
    else
        echo "WARN: Failed to download 32-bit driver package" >&2
        X64_ONLY=1
    fi
fi

ARCH=x86_64
PLATFORM=Linux-${ARCH}
if [ "$X64_ONLY" -eq 1 ]; then
    RUN_FILE=NVIDIA-${PLATFORM}-${VERSION}.run
else
    RUN_FILE=NVIDIA-${PLATFORM}-${VERSION}-no-compat32.run
fi

get_run_file
src_dir=$(extract_run_file "$TEMP_UNPACK")
create_kmod_tarball "$src_dir"
create_driver_tarball "$src_dir"

# Generate the 32-bit libs tarballs from the 64-bit package
if [ "$X64_ONLY" -eq 1 ]; then
    ARCH=i386 PLATFORM=Linux-${ARCH} create_driver_tarball "$src_dir" 32
fi
