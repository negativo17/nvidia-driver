%global debug_package %{nil}
%global __strip /bin/true

%if 0%{?rhel} == 6
%global _glvnd_libdir   %{_libdir}/libglvnd
%endif

Name:           nvidia-driver
Version:        450.80.02
Release:        1%{?dist}
Summary:        NVIDIA's proprietary display driver for NVIDIA graphic cards
Epoch:          3
License:        NVIDIA License
URL:            http://www.nvidia.com/object/unix.html
ExclusiveArch:  %{ix86} x86_64

Source0:        %{name}-%{version}-i386.tar.xz
Source1:        %{name}-%{version}-x86_64.tar.xz
# For servers without OutputClass device options (el6)
Source11:       10-nvidia.conf
# For servers with OutputClass device options (el7+)
Source12:       10-nvidia.conf.outputclass-device

Source40:       com.nvidia.driver.metainfo.xml
Source41:       parse-readme.py

Source99:       nvidia-generate-tarballs.sh

%ifarch x86_64

%if 0%{?rhel} >= 7
BuildRequires:  systemd
%endif

%if 0%{?fedora}
BuildRequires:  systemd-rpm-macros
%endif

%if 0%{?fedora} || 0%{?rhel} >= 8
BuildRequires:  libappstream-glib
BuildRequires:  python3
%else
BuildRequires:  python2
%endif

%endif

Requires:       nvidia-driver-libs%{?_isa} = %{?epoch:%{epoch}:}%{version}
Requires:       nvidia-kmod-common = %{?epoch:%{epoch}:}%{version}
Requires:       libva-vdpau-driver%{?_isa}
Requires:       xorg-x11-server-Xorg%{?_isa}

Conflicts:      catalyst-x11-drv
Conflicts:      catalyst-x11-drv-legacy
Conflicts:      fglrx-x11-drv
Conflicts:      nvidia-x11-drv
Conflicts:      nvidia-x11-drv-173xx
Conflicts:      nvidia-x11-drv-304xx
Conflicts:      nvidia-x11-drv-340xx
Conflicts:      nvidia-x11-drv-390xx
Conflicts:      xorg-x11-drv-nvidia
Conflicts:      xorg-x11-drv-nvidia-173xx
Conflicts:      xorg-x11-drv-nvidia-304xx
Conflicts:      xorg-x11-drv-nvidia-340xx
Conflicts:      xorg-x11-drv-nvidia-390xx

%description
This package provides the most recent NVIDIA display driver which allows for
hardware accelerated rendering with recent NVIDIA chipsets.

For the full product support list, please consult the release notes for driver
version %{version}.

%package libs
Summary:        Libraries for %{name}
Requires:       libvdpau%{?_isa} >= 0.5
Requires:       libglvnd%{?_isa} >= 1.0
Requires:       libglvnd-egl%{?_isa} >= 1.0
Requires:       libglvnd-gles%{?_isa} >= 1.0
Requires:       libglvnd-glx%{?_isa} >= 1.0
Requires:       libglvnd-opengl%{?_isa} >= 1.0

%if 0%{?fedora} || 0%{?rhel} >= 8
Requires:       egl-wayland%{?_isa}
Requires:       vulkan-loader
%endif

%if 0%{?rhel} == 7
Requires:       vulkan-filesystem
%ifarch x86_64
Requires:       egl-wayland%{?_isa}
%endif
%endif

Conflicts:      nvidia-x11-drv-libs
Conflicts:      nvidia-x11-drv-libs-96xx
Conflicts:      nvidia-x11-drv-libs-173xx
Conflicts:      nvidia-x11-drv-libs-304xx
Conflicts:      nvidia-x11-drv-libs-340xx
Conflicts:      nvidia-x11-drv-libs-390xx
Conflicts:      xorg-x11-drv-nvidia-gl
Conflicts:      xorg-x11-drv-nvidia-libs
Conflicts:      xorg-x11-drv-nvidia-libs-173xx
Conflicts:      xorg-x11-drv-nvidia-libs-304xx
Conflicts:      xorg-x11-drv-nvidia-libs-340xx
Conflicts:      xorg-x11-drv-nvidia-libs-390xx
%ifarch %{ix86}
Conflicts:      nvidia-x11-drv-32bit
Conflicts:      nvidia-x11-drv-32bit-96xx
Conflicts:      nvidia-x11-drv-32bit-173xx
Conflicts:      nvidia-x11-drv-32bit-304xx
Conflicts:      nvidia-x11-drv-32bit-340xx
Conflicts:      nvidia-x11-drv-32bit-390xx
%endif

%description libs
This package provides the shared libraries for %{name}.

%package cuda-libs
Summary:        Libraries for %{name}-cuda

%description cuda-libs
This package provides the CUDA libraries for %{name}-cuda.

%package NvFBCOpenGL
Summary:        NVIDIA OpenGL-based Framebuffer Capture libraries
# Loads libnvidia-encode.so at runtime
Requires:       %{name}-cuda-libs%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}

%description NvFBCOpenGL
This library provides a high performance, low latency interface to capture and
optionally encode the composited framebuffer of an X screen. NvFBC and NvIFR are
private APIs that are only available to NVIDIA approved partners for use in
remote graphics scenarios.

%package NVML
Summary:        NVIDIA Management Library (NVML)
Provides:       cuda-nvml%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}

%description NVML
A C-based API for monitoring and managing various states of the NVIDIA GPU
devices. It provides a direct access to the queries and commands exposed via
nvidia-smi. The run-time version of NVML ships with the NVIDIA display driver,
and the SDK provides the appropriate header, stub libraries and sample
applications. Each new version of NVML is backwards compatible and is intended
to be a platform for building 3rd party applications.

%package devel
Summary:        Development files for %{name}
Conflicts:      xorg-x11-drv-nvidia-devel
Conflicts:      xorg-x11-drv-nvidia-devel-173xx
Conflicts:      xorg-x11-drv-nvidia-devel-304xx
Conflicts:      xorg-x11-drv-nvidia-devel-340xx
Conflicts:      xorg-x11-drv-nvidia-devel-390xx
Requires:       %{name}-libs%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Requires:       %{name}-cuda-libs%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Requires:       %{name}-NvFBCOpenGL%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}

%description devel
This package provides the development files of the %{name} package.

%ifarch x86_64

%package cuda
Summary:        CUDA integration for %{name}
Conflicts:      xorg-x11-drv-nvidia-cuda
Requires:       nvidia-kmod-common = %{?epoch:%{epoch}:}%{version}
Requires:       %{name}-cuda-libs%{?_isa} = %{?epoch:%{epoch}:}%{version}
Requires:       nvidia-persistenced = %{?epoch:%{epoch}:}%{version}
Requires:       opencl-filesystem
Requires:       ocl-icd

%description cuda
This package provides the CUDA integration components for %{name}.

%endif
 
%prep
%ifarch %{ix86}
%setup -q -n %{name}-%{version}-i386
%endif

%ifarch x86_64
%setup -q -T -b 1 -n %{name}-%{version}-x86_64
%endif

# Create symlinks for shared objects
ldconfig -vn .

# Required for building gstreamer 1.0 NVENC plugins
ln -sf libnvidia-encode.so.%{version} libnvidia-encode.so
# Required for building ffmpeg 3.1 Nvidia CUVID
ln -sf libnvcuvid.so.%{version} libnvcuvid.so

# Required for building against CUDA
ln -sf libcuda.so.%{version} libcuda.so
# libglvnd indirect entry point
ln -sf libGLX_nvidia.so.%{version} libGLX_indirect.so.0

%if 0%{?rhel} == 6
rm -f libnvidia-glvkspirv.so.%{version}
%endif

%build

%install

mkdir -p %{buildroot}%{_datadir}/glvnd/egl_vendor.d/
mkdir -p %{buildroot}%{_datadir}/vulkan/icd.d/
mkdir -p %{buildroot}%{_includedir}/nvidia/GL/
mkdir -p %{buildroot}%{_libdir}/vdpau/

%ifarch x86_64

mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/nvidia/
mkdir -p %{buildroot}%{_libdir}/xorg/modules/drivers/
mkdir -p %{buildroot}%{_libdir}/xorg/modules/extensions/
mkdir -p %{buildroot}%{_mandir}/man1/
mkdir -p %{buildroot}%{_sysconfdir}/X11/xorg.conf.d/
mkdir -p %{buildroot}%{_sysconfdir}/nvidia/
mkdir -p %{buildroot}%{_sysconfdir}/OpenCL/vendors/

%if 0%{?fedora} || 0%{?rhel} >= 7
mkdir -p %{buildroot}%{_datadir}/vulkan/implicit_layer.d/
mkdir -p %{buildroot}%{_unitdir}/
%endif

%if 0%{?rhel} == 6
mkdir -p %{buildroot}%{_datadir}/X11/xorg.conf.d/
%endif

# OpenCL config
install -p -m 0755 nvidia.icd %{buildroot}%{_sysconfdir}/OpenCL/vendors/

# Binaries
install -p -m 0755 nvidia-{debugdump,smi,cuda-mps-control,cuda-mps-server,bug-report.sh} %{buildroot}%{_bindir}

# Man pages
install -p -m 0644 nvidia-{smi,cuda-mps-control}*.gz %{buildroot}%{_mandir}/man1/

%if 0%{?fedora} || 0%{?rhel} >= 8
# install AppData and add modalias provides
install -D -p -m 0644 %{SOURCE40} %{buildroot}%{_metainfodir}/com.nvidia.driver.metainfo.xml
fn=%{buildroot}%{_metainfodir}/com.nvidia.driver.metainfo.xml
%{SOURCE41} README.txt "NVIDIA GEFORCE GPUS" | xargs appstream-util add-provide ${fn} modalias
%{SOURCE41} README.txt "NVIDIA QUADRO GPUS" | xargs appstream-util add-provide ${fn} modalias
%{SOURCE41} README.txt "NVIDIA NVS GPUS" | xargs appstream-util add-provide ${fn} modalias
%{SOURCE41} README.txt "NVIDIA TESLA GPUS" | xargs appstream-util add-provide ${fn} modalias
%{SOURCE41} README.txt "NVIDIA GRID GPUS" | xargs appstream-util add-provide ${fn} modalias
%endif

%if 0%{?rhel} == 6
install -p -m 0644 %{SOURCE11} %{buildroot}%{_sysconfdir}/X11/xorg.conf.d/10-nvidia.conf
%endif

%if 0%{?fedora} || 0%{?rhel} >= 7
install -p -m 0644 %{SOURCE12} %{buildroot}%{_sysconfdir}/X11/xorg.conf.d/10-nvidia.conf
%endif

# X stuff
install -p -m 0755 nvidia_drv.so %{buildroot}%{_libdir}/xorg/modules/drivers/
install -p -m 0755 libglxserver_nvidia.so.%{version} %{buildroot}%{_libdir}/xorg/modules/extensions/libglxserver_nvidia.so

# NVIDIA specific configuration files
install -p -m 0644 nvidia-application-profiles-%{version}-key-documentation \
    %{buildroot}%{_datadir}/nvidia/
install -p -m 0644 nvidia-application-profiles-%{version}-rc \
    %{buildroot}%{_datadir}/nvidia/

%endif

%ifarch x86_64

%if 0%{?fedora} || 0%{?rhel} >= 7
# Vulkan loader
install -p -m 0644 nvidia_icd.json %{buildroot}%{_datadir}/vulkan/icd.d/
%endif

%if 0%{?fedora} || 0%{?rhel} >= 8
# Vulkan layer
install -p -m 0644 nvidia_layers.json %{buildroot}%{_datadir}/vulkan/implicit_layer.d/
%endif

%endif

# EGL loader
install -p -m 0644 10_nvidia.json %{buildroot}%{_datadir}/glvnd/egl_vendor.d/

# Unique libraries
cp -a lib*GL*_nvidia.so* libcuda.so* libnv*.so* %{buildroot}%{_libdir}/
cp -a libvdpau_nvidia.so* %{buildroot}%{_libdir}/vdpau/

# libglvnd indirect entry point and private libglvnd libraries
%if 0%{?rhel} == 6
cp -a libGLX_indirect.so* %{buildroot}%{_libdir}/
install -m 0755 -d %{buildroot}%{_sysconfdir}/ld.so.conf.d/
echo -e "%{_glvnd_libdir} \n" > %{buildroot}%{_sysconfdir}/ld.so.conf.d/nvidia-%{_target_cpu}.conf
%endif

%ifarch x86_64

%if 0%{?fedora} || 0%{?rhel} >= 7
# Systemd units and script for suspending/resuming
install -p -m 0644 nvidia-hibernate.service nvidia-resume.service nvidia-suspend.service %{buildroot}%{_unitdir}
install -p -m 0755 nvidia-sleep.sh %{buildroot}%{_bindir}
%endif

%if 0%{?fedora} || 0%{?rhel} >= 8
%check
appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/com.nvidia.driver.metainfo.xml
%endif

%endif

%ldconfig_scriptlets libs

%ldconfig_scriptlets cuda-libs

%ldconfig_scriptlets NvFBCOpenGL

%ldconfig_scriptlets NVML

%ifarch x86_64

%if 0%{?fedora} || 0%{?rhel} >= 7

%post
%systemd_post nvidia-hibernate.service
%systemd_post nvidia-resume.service
%systemd_post nvidia-suspend.service

%preun
%systemd_preun nvidia-hibernate.service
%systemd_preun nvidia-resume.service
%systemd_preun nvidia-suspend.service

%postun
%systemd_postun nvidia-hibernate.service
%systemd_postun nvidia-resume.service
%systemd_postun nvidia-suspend.service

%endif

%files
%license LICENSE
%doc NVIDIA_Changelog README.txt html supported-gpus.json
%dir %{_sysconfdir}/nvidia
%config(noreplace) %{_sysconfdir}/X11/xorg.conf.d/10-nvidia.conf
%{_bindir}/nvidia-bug-report.sh
%if 0%{?fedora} || 0%{?rhel} >= 8
%{_metainfodir}/com.nvidia.driver.metainfo.xml
%endif
%{_datadir}/nvidia
%{_libdir}/xorg/modules/extensions/libglxserver_nvidia.so
%{_libdir}/xorg/modules/drivers/nvidia_drv.so
%if 0%{?fedora} || 0%{?rhel} >= 7
%{_bindir}/nvidia-sleep.sh
%{_unitdir}/nvidia-hibernate.service
%{_unitdir}/nvidia-resume.service
%{_unitdir}/nvidia-suspend.service
%endif

%files cuda
%{_sysconfdir}/OpenCL/vendors/*
%{_bindir}/nvidia-cuda-mps-control
%{_bindir}/nvidia-cuda-mps-server
%{_bindir}/nvidia-debugdump
%{_bindir}/nvidia-smi
%{_mandir}/man1/nvidia-cuda-mps-control.1.*
%{_mandir}/man1/nvidia-smi.*

%endif

%files devel
%{_includedir}/nvidia/
%{_libdir}/libnvcuvid.so
%{_libdir}/libnvidia-encode.so

%files libs
%if 0%{?rhel} == 6
%{_sysconfdir}/ld.so.conf.d/nvidia-%{_target_cpu}.conf
%{_libdir}/libGLX_indirect.so.0
%endif
%{_datadir}/glvnd/egl_vendor.d/10_nvidia.json
%ifarch x86_64
%if 0%{?fedora} || 0%{?rhel} >= 7
%{_datadir}/vulkan/icd.d/nvidia_icd.json
%endif
%if 0%{?fedora} || 0%{?rhel} >= 8
%{_datadir}/vulkan/implicit_layer.d/nvidia_layers.json
%endif
%endif
%{_libdir}/libEGL_nvidia.so.0
%{_libdir}/libEGL_nvidia.so.%{version}
%{_libdir}/libGLESv1_CM_nvidia.so.1
%{_libdir}/libGLESv1_CM_nvidia.so.%{version}
%{_libdir}/libGLESv2_nvidia.so.2
%{_libdir}/libGLESv2_nvidia.so.%{version}
%{_libdir}/libGLX_nvidia.so.0
%{_libdir}/libGLX_nvidia.so.%{version}
%ifarch x86_64
%{_libdir}/libnvidia-cbl.so.%{version}
%{_libdir}/libnvidia-cfg.so.1
%{_libdir}/libnvidia-cfg.so.%{version}
%{_libdir}/libnvidia-ngx.so.1
%{_libdir}/libnvidia-ngx.so.%{version}
%{_libdir}/libnvidia-rtcore.so.%{version}
%{_libdir}/libnvoptix.so.1
%{_libdir}/libnvoptix.so.%{version}
%endif
%{_libdir}/libnvidia-allocator.so.1
%{_libdir}/libnvidia-allocator.so.%{version}
%{_libdir}/libnvidia-eglcore.so.%{version}
%{_libdir}/libnvidia-glcore.so.%{version}
%{_libdir}/libnvidia-glsi.so.%{version}
%if 0%{?fedora} || 0%{?rhel} >= 7
%{_libdir}/libnvidia-glvkspirv.so.%{version}
%endif
%{_libdir}/libnvidia-tls.so.%{version}
%{_libdir}/vdpau/libvdpau_nvidia.so.1
%{_libdir}/vdpau/libvdpau_nvidia.so.%{version}

%files cuda-libs
%{_libdir}/libcuda.so
%{_libdir}/libcuda.so.1
%{_libdir}/libcuda.so.%{version}
%{_libdir}/libnvcuvid.so.1
%{_libdir}/libnvcuvid.so.%{version}
%{_libdir}/libnvidia-compiler.so.%{version}
%{_libdir}/libnvidia-encode.so.1
%{_libdir}/libnvidia-encode.so.%{version}
%{_libdir}/libnvidia-opencl.so.1
%{_libdir}/libnvidia-opencl.so.%{version}
%{_libdir}/libnvidia-opticalflow.so.1
%{_libdir}/libnvidia-opticalflow.so.%{version}
%{_libdir}/libnvidia-ptxjitcompiler.so.1
%{_libdir}/libnvidia-ptxjitcompiler.so.%{version}

%files NvFBCOpenGL
%{_libdir}/libnvidia-fbc.so.1
%{_libdir}/libnvidia-fbc.so.%{version}
%{_libdir}/libnvidia-ifr.so.1
%{_libdir}/libnvidia-ifr.so.%{version}

%files NVML
%{_libdir}/libnvidia-ml.so.1
%{_libdir}/libnvidia-ml.so.%{version}

%changelog
* Thu Oct 1 2020 Christian Birk <chris.h3o66@gmail.com> - 3:450.80.02-1
- Update to 450.80.02.

* Thu Aug 20 2020 Simone Caronni <negativo17@gmail.com> - 3:450.66-1
- Update to 450.66.

* Fri Jul 10 2020 Simone Caronni <negativo17@gmail.com> - 3:450.57-1
- Update to 450.57.
- Driver now autodetects GPU Screens and RandR PRIME Display Offload Sink
  based on X.org version.

* Thu Jun 25 2020 Simone Caronni <negativo17@gmail.com> - 3:440.100-1
- Update to 440.100.

* Thu Apr 09 2020 Simone Caronni <negativo17@gmail.com> - 3:440.82-1
- Update to 440.82.

* Fri Feb 28 2020 Simone Caronni <negativo17@gmail.com> - 3:440.64-1
- Update to 440.64.

* Tue Feb 14 2020 Jens Peters <jp7677@gmail.com> - 3:440.59-2
- Ensure that only one Vulkan ICD manifest is present.

* Tue Feb 04 2020 Simone Caronni <negativo17@gmail.com> - 3:440.59-1
- Update to 440.59.

* Sat Dec 14 2019 Simone Caronni <negativo17@gmail.com> - 3:440.44-1
- Update to 440.44.

* Sat Nov 30 2019 Simone Caronni <negativo17@gmail.com> - 3:440.36-1
- Update to 440.36.

* Wed Nov 13 2019 Simone Caronni <negativo17@gmail.com> - 3:440.31-3
- RHEL/CentOS 6 does not work anymore with OutputClass configurations.

* Sun Nov 10 2019 Simone Caronni <negativo17@gmail.com> - 3:440.31-2
- Streamline configurations between the various distributions.

* Sat Nov 09 2019 Simone Caronni <negativo17@gmail.com> - 3:440.31-1
- Update to 440.31.

* Thu Oct 17 2019 Simone Caronni <negativo17@gmail.com> - 3:440.26-1
- Update to 440.26.

* Tue Oct 01 2019 Simone Caronni <negativo17@gmail.com> - 3:435.21-2
- Fix build dependency on CentOS/RHEL 8.

* Mon Sep 02 2019 Simone Caronni <negativo17@gmail.com> - 3:435.21-1
- Update to 435.21.

* Thu Aug 22 2019 Simone Caronni <negativo17@gmail.com> - 3:435.17-1
- Update to 435.17.
- Add hibernate/resume/suspend systemd hooks.
- Add Vulkan layer file and default powermanagement.

* Wed Jul 31 2019 Simone Caronni <negativo17@gmail.com> - 3:430.40-1
- Update to 430.40.
- Update AppData installation.

* Fri Jul 12 2019 Simone Caronni <negativo17@gmail.com> - 3:430.34-1
- Update to 430.34.

* Wed Jun 12 2019 Simone Caronni <negativo17@gmail.com> - 3:430.26-1
- Update to 430.26.

* Sat May 18 2019 Simone Caronni <negativo17@gmail.com> - 3:430.14-1
- Update to 430.14.

* Thu May 09 2019 Simone Caronni <negativo17@gmail.com> - 3:418.74-1
- Update to 418.74.

* Sun Mar 24 2019 Simone Caronni <negativo17@gmail.com> - 3:418.56-1
- Update to 418.56.

* Thu Feb 28 2019 Simone Caronni <negativo17@gmail.com> - 3:418.43-2
- Do not require egl-wayland on EPEL 32 bit.

* Fri Feb 22 2019 Simone Caronni <negativo17@gmail.com> - 3:418.43-1
- Update to 418.43.
- Trim changelog.

* Wed Feb 06 2019 Simone Caronni <negativo17@gmail.com> - 3:418.30-1
- Update to 418.30.

* Mon Feb 04 2019 Simone Caronni <negativo17@gmail.com> - 3:415.27-5
- Move fatbinaryloader in main libraries subpackage.

* Sun Feb 03 2019 Simone Caronni <negativo17@gmail.com> - 3:415.27-4
- Split out all kernel related interactions into the nvidia-kmod-common package.
- Require nvidia-kmod-common in both nvidia-driver and nvidia-driver-cuda as
  they can now be installed separately.

* Sun Feb 03 2019 Simone Caronni <negativo17@gmail.com> - 3:415.27-3
- Remove CUDA provides/requires, move them to separate package.

* Sat Feb 02 2019 Simone Caronni <negativo17@gmail.com> - 3:415.27-2
- Add nvidia-drivers and cuda-drivers virtual provides as requested by Red Hat.

* Thu Jan 17 2019 Simone Caronni <negativo17@gmail.com> - 3:415.27-1
- Update to 415.27.

* Sat Jan 12 2019 Simone Caronni <negativo17@gmail.com> - 3:415.25-2
- Update requirements.

* Thu Dec 20 2018 Simone Caronni <negativo17@gmail.com> - 3:415.25-1
- Update to 415.25.

* Fri Dec 14 2018 Simone Caronni <negativo17@gmail.com> - 3:415.23-1
- Update to 415.23.

* Sun Dec 09 2018 Simone Caronni <negativo17@gmail.com> - 3:415.22-1
- Update to 415.22.

* Sat Dec 01 2018 Simone Caronni <negativo17@gmail.com> - 3:415.18-3
- No more private GLVND libraries on RHEL 7.

* Thu Nov 22 2018 Simone Caronni <negativo17@gmail.com> - 3:415.18-2
- Update scripts to always perform updates/removal of boot options.

* Thu Nov 22 2018 Simone Caronni <negativo17@gmail.com> - 3:415.18-1
- Update to 415.18.

* Thu Nov 22 2018 Simone Caronni <negativo17@gmail.com> - 3:410.78-2
- Remove modesetting again on Fedora.

* Mon Nov 19 2018 Simone Caronni <negativo17@gmail.com> - 3:410.78-1
- Update to 410.78.

* Tue Oct 30 2018 Simone Caronni <negativo17@gmail.com> - 3:410.73-4
- Disable modesetting on Fedora < 29.

* Sat Oct 27 2018 Simone Caronni <negativo17@gmail.com> - 3:410.73-3
- Revert grubby invocation on RHEL/CentOS 6.

* Fri Oct 26 2018 Simone Caronni <negativo17@gmail.com> - 3:410.73-2
- Update post scriptlets to make sure new parameters are added correctly.

* Fri Oct 26 2018 Simone Caronni <negativo17@gmail.com> - 3:410.73-1
- Update to 410.73.
- Enable modesetting and remove ignoreabi setting for Fedora.
- Update conditionals for RHEL/CentOS.
- Add additional conflicting packages.
- Bump GLVND requirements.

* Wed Oct 17 2018 Simone Caronni <negativo17@gmail.com> - 3:410.66-2
- Do not enable Vulkan components on RHEL/CentOS 6.

* Wed Oct 17 2018 Simone Caronni <negativo17@gmail.com> - 3:410.66-1
- Update to 410.66.
- Enable modeset for RHEL/CentOS 7 (7.6).

* Sat Sep 22 2018 Simone Caronni <negativo17@gmail.com> - 3:410.57-1
- Update to 410.57.

* Tue Aug 28 2018 Simone Caronni <negativo17@gmail.com> - 3:396.54-2
- Re-add devel subpackage to x86.
- Remove nvml header requirements for devel subpackage (pulled in by CUDA
  devel subpackage if needed).

* Wed Aug 22 2018 Simone Caronni <negativo17@gmail.com> - 3:396.54-1
- Update to 396.54.

* Sun Aug 19 2018 Simone Caronni <negativo17@gmail.com> - 3:396.51-1
- Update to 396.51.

* Fri Jul 20 2018 Simone Caronni <negativo17@gmail.com> - 3:396.45-1
- Update to 396.45.

* Fri Jun 01 2018 Simone Caronni <negativo17@gmail.com> - 3:396.24-1
- Update to 396.24, x86_64 only.
- Fix Vulkan ownership of files.
- Update conditionals for distributions.

* Tue May 22 2018 Simone Caronni <negativo17@gmail.com> - 3:390.59-1
- Update to 390.59.

* Tue Apr 03 2018 Simone Caronni <negativo17@gmail.com> - 3:390.48-1
- Update to 390.48.

* Thu Mar 15 2018 Simone Caronni <negativo17@gmail.com> - 3:390.42-1
- Update to 390.42.

* Tue Feb 27 2018 Simone Caronni <negativo17@gmail.com> - 3:390.25-4
- Update Epoch so packages do not overlap with RPMFusion.

* Tue Feb 27 2018 Simone Caronni <negativo17@gmail.com> - 2:390.25-3
- Require libnvidia-ml.so in nvidia-driver-devel package.

* Fri Feb 02 2018 Simone Caronni <negativo17@gmail.com> - 2:390.25-2
- Fix omitting drivers from the initrd.

* Tue Jan 30 2018 Simone Caronni <negativo17@gmail.com> - 2:390.25-1
- Update to 390.25.

* Fri Jan 19 2018 Simone Caronni <negativo17@gmail.com> - 2:390.12-1
- Update to 390.12.
