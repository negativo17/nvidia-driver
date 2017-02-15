%global debug_package %{nil}
%global __strip /bin/true

%if 0%{?rhel} == 6
# RHEL 6 does not have _udevrulesdir defined
%global _udevrulesdir   %{_prefix}/lib/udev/rules.d/
%global _dracutopts     nouveau.modeset=0 rdblacklist=nouveau
%global _dracutopts_rm  nomodeset vga=normal
%global _modprobe_d     %{_sysconfdir}/modprobe.d/
%global _grubby         /sbin/grubby --grub --update-kernel=ALL

# Prevent nvidia-driver-libs being pulled in place of mesa
%{?filter_setup:
%filter_provides_in %{_libdir}/nvidia
%filter_requires_in %{_libdir}/nvidia
%filter_setup
}
%endif

%if 0%{?fedora} || 0%{?rhel} >= 7
%global _dracutopts     nouveau.modeset=0 rd.driver.blacklist=nouveau
%global _dracutopts_rm  nomodeset gfxpayload=vga=normal
%global _modprobe_d     %{_prefix}/lib/modprobe.d/
%global _grubby         %{_sbindir}/grubby --update-kernel=ALL

# Prevent nvidia-libs being pulled in place of mesa. This is for all
# libraries in the "nvidia" subdirectory.
%global __provides_exclude_from %{_libdir}/nvidia
%global __requires_exclude_from %{_libdir}/nvidia
%endif

Name:           nvidia-driver
Version:        378.13
Release:        1%{?dist}
Summary:        NVIDIA's proprietary display driver for NVIDIA graphic cards
Epoch:          2
License:        NVIDIA License
URL:            http://www.nvidia.com/object/unix.html
ExclusiveArch:  %{ix86} x86_64

Source0:        %{name}-%{version}-i386.tar.xz
Source1:        %{name}-%{version}-x86_64.tar.xz
# For servers up to 1.19.0-3
Source10:       99-nvidia-modules.conf
# For servers from 1.16 to 1.19.0-3
Source11:       10-nvidia-driver.conf
# For unreleased Fedora versions
Source12:       99-nvidia-ignoreabi.conf
# For servers 1.19.0-3+
Source13:       10-nvidia.conf
# For servers up to 1.15, also used as sample
Source14:       xorg.conf.nvidia

Source20:       nvidia.conf
Source21:       alternate-install-present
Source22:       60-nvidia-uvm.rules
Source23:       nvidia-uvm.conf

Source40:       com.nvidia.driver.metainfo.xml
Source41:       parse-readme.py

Source99:       nvidia-generate-tarballs.sh

BuildRequires:  python

%if 0%{?fedora} || 0%{?rhel} >= 7
# UDev rule location (_udevrulesdir)
BuildRequires:  systemd
%endif

%if 0%{?fedora} >= 25
# AppStream metadata generation
BuildRequires:  libappstream-glib%{?_isa} >= 0.6.3
%endif

Requires:       grubby
Requires:       nvidia-driver-libs%{?_isa} = %{?epoch}:%{version}
Requires:       nvidia-kmod = %{?epoch}:%{version}
Provides:       nvidia-kmod-common = %{?epoch}:%{version}
Requires:       libva-vdpau-driver%{?_isa}

%if 0%{?fedora}
Requires:       vulkan-filesystem
%endif

%if 0%{?rhel} == 6
Requires:       xorg-x11-server-Xorg%{?_isa}
%endif

%if 0%{?fedora} == 24 || 0%{?rhel} == 7
# X.org "OutputClass"
Requires:       xorg-x11-server-Xorg%{?_isa} >= 1.16
%endif

%if 0%{?fedora} >= 25
# Extended "OutputClass" with device options
Requires:       xorg-x11-server-Xorg%{?_isa} >= 1.19.0-3
%endif

Conflicts:      fglrx-x11-drv
Conflicts:      catalyst-x11-drv
Conflicts:      catalyst-x11-drv-legacy

Obsoletes:      xorg-x11-drv-nvidia < %{?epoch}:%{version}-%{release}
Provides:       xorg-x11-drv-nvidia = %{?epoch}:%{version}-%{release}
Obsoletes:      nvidia-x11-drv < %{?epoch}:%{version}-%{release}
Provides:       nvidia-x11-drv = %{?epoch}:%{version}-%{release}

# Introduced in CUDA 8.0
Obsoletes:      cuda-drivers < %{?epoch}:%{version}-%{release}
Provides:       cuda-drivers = %{?epoch}:%{version}-%{release}

%description
This package provides the most recent NVIDIA display driver which allows for
hardware accelerated rendering with recent NVIDIA chipsets.

For the full product support list, please consult the release notes for driver
version %{version}.

%package libs
Summary:        Libraries for %{name}
Requires(post): ldconfig
Requires:       %{name} = %{?epoch}:%{version}-%{release}
Requires:       libvdpau%{?_isa} >= 0.5
Requires:       libglvnd%{?_isa} >= 0.2
Requires:       libglvnd-egl%{?_isa} >= 0.2
Requires:       libglvnd-gles%{?_isa} >= 0.2
Requires:       libglvnd-glx%{?_isa} >= 0.2
Requires:       libglvnd-opengl%{?_isa} >= 0.2

%if 0%{?fedora} >= 25 || 0%{?rhel} >= 8
Requires:       egl-wayland
%endif

Obsoletes:      nvidia-x11-drv-libs < %{?epoch}:%{version}
Provides:       nvidia-x11-drv-libs = %{?epoch}:%{version}
Obsoletes:      xorg-x11-drv-nvidia-libs < %{?epoch}:%{version}
Provides:       xorg-x11-drv-nvidia-libs = %{?epoch}:%{version}
%ifarch %{ix86}
Obsoletes:      nvidia-x11-drv-32bit < %{?epoch}:%{version}
Provides:       nvidia-x11-drv-32bit = %{?epoch}:%{version}
%endif

%description libs
This package provides the shared libraries for %{name}.

%package cuda
Summary:        CUDA integration for %{name}
Obsoletes:      xorg-x11-drv-nvidia-cuda < %{?epoch}:%{version}-%{release}
Provides:       xorg-x11-drv-nvidia-cuda = %{?epoch}:%{version}-%{release}
Requires:       %{name}-cuda-libs%{?_isa} = %{?epoch}:%{version}
Requires:       nvidia-persistenced = %{?epoch}:%{version}
%if 0%{?fedora} || 0%{?rhel} >= 8
Requires:       opencl-filesystem
%endif

%description cuda
This package provides the CUDA integration components for %{name}.

%package cuda-libs
Summary:        Libraries for %{name}-cuda
Requires(post): ldconfig

%description cuda-libs
This package provides the CUDA libraries for %{name}-cuda.

%package NvFBCOpenGL
Summary:        NVIDIA OpenGL-based Framebuffer Capture libraries
Requires(post): ldconfig
# Loads libnvidia-encode.so at runtime
Requires:       %{name}-cuda-libs%{?_isa} = %{?epoch}:%{version}-%{release}

%description NvFBCOpenGL
This library provides a high performance, low latency interface to capture and
optionally encode the composited framebuffer of an X screen. NvFBC and NvIFR are
private APIs that are only available to NVIDIA approved partners for use in
remote graphics scenarios.

%package NVML
Summary:        NVIDIA Management Library (NVML)
Requires(post): ldconfig
Provides:       cuda-nvml%{?_isa} = %{?epoch}:%{version}-%{release}

%description NVML
A C-based API for monitoring and managing various states of the NVIDIA GPU
devices. It provides a direct access to the queries and commands exposed via
nvidia-smi. The run-time version of NVML ships with the NVIDIA display driver,
and the SDK provides the appropriate header, stub libraries and sample
applications. Each new version of NVML is backwards compatible and is intended
to be a platform for building 3rd party applications.

%package devel
Summary:        Development files for %{name}
Obsoletes:      xorg-x11-drv-nvidia-devel < %{?epoch}:%{version}-%{release}
Provides:       xorg-x11-drv-nvidia-devel = %{?epoch}:%{version}-%{release}
Requires:       %{name}-libs%{?_isa} = %{?epoch}:%{version}-%{release}
Requires:       %{name}-cuda-libs%{?_isa} = %{?epoch}:%{version}-%{release}
Requires:       %{name}-NVML%{?_isa} = %{?epoch}:%{version}-%{release}
Requires:       %{name}-NvFBCOpenGL%{?_isa} = %{?epoch}:%{version}-%{release}

%description devel
This package provides the development files of the %{name} package,
such as OpenGL headers.
 
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

%build

%install
# Create empty tree
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/appdata/
mkdir -p %{buildroot}%{_datadir}/glvnd/egl_vendor.d/
mkdir -p %{buildroot}%{_datadir}/nvidia/
mkdir -p %{buildroot}%{_includedir}/nvidia/GL/
mkdir -p %{buildroot}%{_libdir}/nvidia/xorg/
mkdir -p %{buildroot}%{_libdir}/vdpau/
mkdir -p %{buildroot}%{_libdir}/xorg/modules/drivers/
mkdir -p %{buildroot}%{_mandir}/man1/
mkdir -p %{buildroot}%{_sysconfdir}/X11/xorg.conf.d/
mkdir -p %{buildroot}%{_sysconfdir}/ld.so.conf.d/
mkdir -p %{buildroot}%{_sysconfdir}/nvidia/
mkdir -p %{buildroot}%{_sysconfdir}/vulkan/icd.d/
mkdir -p %{buildroot}%{_udevrulesdir}
mkdir -p %{buildroot}%{_modprobe_d}/
mkdir -p %{buildroot}%{_sysconfdir}/OpenCL/vendors/

%if 0%{?fedora} == 24 || 0%{?rhel}
mkdir -p %{buildroot}%{_datadir}/X11/xorg.conf.d/
%endif

# Headers
install -p -m 0644 *.h %{buildroot}%{_includedir}/nvidia/GL/

# OpenCL config
install -p -m 0755 nvidia.icd %{buildroot}%{_sysconfdir}/OpenCL/vendors/

# Vulkan and EGL loaders
install -p -m 0644 nvidia_icd.json %{buildroot}%{_sysconfdir}/vulkan/icd.d/
install -p -m 0644 10_nvidia.json %{buildroot}%{_datadir}/glvnd/egl_vendor.d/
# Library search path
echo "%{_libdir}/nvidia" > %{buildroot}%{_sysconfdir}/ld.so.conf.d/nvidia-%{_lib}.conf

# Blacklist nouveau, enable KMS
install -p -m 0644 %{SOURCE20} %{buildroot}%{_modprobe_d}/

# Autoload nvidia-uvm module after nvidia module
install -p -m 0644 %{SOURCE23} %{buildroot}%{_modprobe_d}/

# Binaries
install -p -m 0755 nvidia-{debugdump,smi,cuda-mps-control,cuda-mps-server,bug-report.sh} %{buildroot}%{_bindir}

# Man pages
install -p -m 0644 nvidia-{smi,cuda-mps-control}*.gz %{buildroot}%{_mandir}/man1/

%if 0%{?fedora} >= 25
# install AppData and add modalias provides
install -p -m 0644 %{SOURCE40} %{buildroot}%{_datadir}/appdata/
fn=%{buildroot}%{_datadir}/appdata/com.nvidia.driver.metainfo.xml
%{SOURCE41} README.txt "NVIDIA GEFORCE GPUS" | xargs appstream-util add-provide ${fn} modalias
%{SOURCE41} README.txt "NVIDIA QUADRO GPUS" | xargs appstream-util add-provide ${fn} modalias
%{SOURCE41} README.txt "NVIDIA NVS GPUS" | xargs appstream-util add-provide ${fn} modalias
%{SOURCE41} README.txt "NVIDIA TESLA GPUS" | xargs appstream-util add-provide ${fn} modalias
%endif

# X configuration
%if 0%{?rhel} == 6
install -p -m 0644 %{SOURCE14} %{buildroot}%{_sysconfdir}/X11/xorg.conf.nvidia
%endif

%if 0%{?fedora} == 24 || 0%{?rhel}
install -p -m 0644 %{SOURCE10} %{buildroot}%{_sysconfdir}/X11/xorg.conf.d/99-nvidia-modules.conf
sed -i -e 's|@LIBDIR@|%{_libdir}|g' %{buildroot}%{_sysconfdir}/X11/xorg.conf.d/99-nvidia-modules.conf
%endif

%if 0%{?fedora} == 24 || 0%{?rhel} >= 7
# Use xorg.conf as sample
cp %{SOURCE14} xorg.conf.sample
install -p -m 0644 %{SOURCE11} %{buildroot}%{_datadir}/X11/xorg.conf.d/10-nvidia-driver.conf
%endif

%if 0%{?fedora} >= 25
# Use xorg.conf as sample
cp %{SOURCE14} xorg.conf.sample
install -p -m 0644 %{SOURCE13} %{buildroot}%{_sysconfdir}/X11/xorg.conf.d/10-nvidia.conf
sed -i -e 's|@LIBDIR@|%{_libdir}|g' %{buildroot}%{_sysconfdir}/X11/xorg.conf.d/10-nvidia.conf
%endif

%if 0%{?fedora} >= 26
install -p -m 0644 %{SOURCE12} %{buildroot}%{_sysconfdir}/X11/xorg.conf.d/99-nvidia-ignoreabi.conf
%endif

# X stuff
install -p -m 0755 nvidia_drv.so %{buildroot}%{_libdir}/xorg/modules/drivers/
install -p -m 0755 libglx.so.%{version} %{buildroot}%{_libdir}/nvidia/xorg/libglx.so

# NVIDIA specific configuration files
install -p -m 0644 nvidia-application-profiles-%{version}-key-documentation \
    %{buildroot}%{_datadir}/nvidia/
install -p -m 0644 nvidia-application-profiles-%{version}-rc \
    %{buildroot}%{_datadir}/nvidia/

# Text files for alternate installation
install -p -m 644 %{SOURCE21} %{buildroot}%{_libdir}/nvidia/alternate-install-present

# UDev rules for nvidia-uvm
install -p -m 644 %{SOURCE22} %{buildroot}%{_udevrulesdir}

# System conflicting libraries
cp -a libOpenCL.so* %{buildroot}%{_libdir}/nvidia/

# Unique libraries
cp -a lib*GL*_nvidia.so* libcuda.so* libnvidia-*.so* libnvcuvid.so* %{buildroot}%{_libdir}/
cp -a libvdpau_nvidia.so* %{buildroot}%{_libdir}/vdpau/

ln -sf libcuda.so.%{version} %{buildroot}%{_libdir}/libcuda.so
ln -sf libGLX_nvidia.so.%{version} %{buildroot}%{_libdir}/libGLX_indirect.so.0

%post
if [ "$1" -eq "1" ]; then
  %{_grubby} --args='%{_dracutopts}' &>/dev/null
%if 0%{?fedora} || 0%{?rhel} >= 7
  sed -i -e 's/GRUB_CMDLINE_LINUX="/GRUB_CMDLINE_LINUX="%{_dracutopts} /g' /etc/default/grub
%endif
fi || :
if [ "$1" -eq "2" ]; then
  # Remove no longer needed options
  %{_grubby} --remove-args='%{_dracutopts_rm}' &>/dev/null
  sed -i -e 's/ %{_dracutopts_rm}//g' /etc/default/grub
fi || :

%post libs -p /sbin/ldconfig

%post cuda-libs -p /sbin/ldconfig

%post NvFBCOpenGL -p /sbin/ldconfig

%post NVML -p /sbin/ldconfig

%if 0%{?rhel} == 6
%posttrans
[ -f %{_sysconfdir}/X11/xorg.conf ] || cp -p %{_sysconfdir}/X11/xorg.conf.nvidia %{_sysconfdir}/X11/xorg.conf || :
%endif

%preun
if [ "$1" -eq "0" ]; then
  %{_grubby} --remove-args='%{_dracutopts}' &>/dev/null
%if 0%{?fedora} || 0%{?rhel} >= 7
  sed -i -e 's/%{_dracutopts} //g' /etc/default/grub
%endif
%if 0%{?rhel} == 6
  # Backup and disable previously used xorg.conf
  [ -f %{_sysconfdir}/X11/xorg.conf ] && mv %{_sysconfdir}/X11/xorg.conf %{_sysconfdir}/X11/xorg.conf.nvidia_uninstalled &>/dev/null
%endif
fi ||:

%postun libs -p /sbin/ldconfig

%postun cuda-libs -p /sbin/ldconfig

%postun NvFBCOpenGL -p /sbin/ldconfig

%postun NVML -p /sbin/ldconfig

%files
%{!?_licensedir:%global license %%doc}
%license LICENSE
%doc NVIDIA_Changelog README.txt html
%dir %{_sysconfdir}/nvidia
%{_bindir}/nvidia-bug-report.sh
%if 0%{?fedora} >= 25
%{_datadir}/appdata/com.nvidia.driver.metainfo.xml
%endif
%{_datadir}/nvidia
%{_libdir}/nvidia/alternate-install-present
%{_libdir}/nvidia/xorg
%{_libdir}/xorg/modules/drivers/nvidia_drv.so
%{_modprobe_d}/nvidia.conf
%{_sysconfdir}/vulkan/icd.d/*

# X.org configuration files
%if 0%{?fedora} == 24 || 0%{?rhel}
%config(noreplace) %{_sysconfdir}/X11/xorg.conf.d/99-nvidia-modules.conf
%endif

%if 0%{?rhel} == 6
%config(noreplace) %{_sysconfdir}/X11/xorg.conf.nvidia
%endif

%if 0%{?fedora} == 24 || 0%{?rhel} >= 7
%config(noreplace) %{_datadir}/X11/xorg.conf.d/10-nvidia-driver.conf
%endif

%if 0%{?fedora} >= 25
%config(noreplace) %{_sysconfdir}/X11/xorg.conf.d/10-nvidia.conf
%endif

%if 0%{?fedora} >= 26 || 0%{?rhel} >= 8
%config(noreplace) %{_sysconfdir}/X11/xorg.conf.d/99-nvidia-ignoreabi.conf
%endif

%files cuda
%{_sysconfdir}/OpenCL/vendors/*
%{_bindir}/nvidia-cuda-mps-control
%{_bindir}/nvidia-cuda-mps-server
%{_bindir}/nvidia-debugdump
%{_bindir}/nvidia-smi
%{_mandir}/man1/nvidia-cuda-mps-control.1.*
%{_mandir}/man1/nvidia-smi.*
%{_modprobe_d}/nvidia-uvm.conf
%{_udevrulesdir}/60-nvidia-uvm.rules

%files libs
%{_datadir}/glvnd/egl_vendor.d/*
%{_libdir}/libEGL_nvidia.so.0
%{_libdir}/libEGL_nvidia.so.%{version}
%{_libdir}/libGLESv1_CM_nvidia.so.1
%{_libdir}/libGLESv1_CM_nvidia.so.%{version}
%{_libdir}/libGLESv2_nvidia.so.2
%{_libdir}/libGLESv2_nvidia.so.%{version}
%{_libdir}/libGLX_indirect.so.0
%{_libdir}/libGLX_nvidia.so.0
%{_libdir}/libGLX_nvidia.so.%{version}
%{_libdir}/libnvidia-cfg.so.1
%{_libdir}/libnvidia-cfg.so.%{version}
%{_libdir}/libnvidia-eglcore.so.%{version}
%{_libdir}/libnvidia-glcore.so.%{version}
%{_libdir}/libnvidia-glsi.so.%{version}
%{_libdir}/libnvidia-tls.so.%{version}
%{_libdir}/vdpau/libvdpau_nvidia.so.1
%{_libdir}/vdpau/libvdpau_nvidia.so.%{version}

%files cuda-libs
%dir %{_libdir}/nvidia
%{_libdir}/libcuda.so
%{_libdir}/libcuda.so.1
%{_libdir}/libcuda.so.%{version}
%{_libdir}/libnvcuvid.so.1
%{_libdir}/libnvcuvid.so.%{version}
%{_libdir}/libnvidia-compiler.so.%{version}
%{_libdir}/libnvidia-encode.so.1
%{_libdir}/libnvidia-encode.so.%{version}
%{_libdir}/libnvidia-fatbinaryloader.so.%{version}
%{_libdir}/libnvidia-opencl.so.1
%{_libdir}/libnvidia-opencl.so.%{version}
%{_libdir}/libnvidia-ptxjitcompiler.so.%{version}
%{_libdir}/nvidia/libOpenCL.so.1
%{_libdir}/nvidia/libOpenCL.so.1.0.0
%{_sysconfdir}/ld.so.conf.d/nvidia-%{_lib}.conf

%files NvFBCOpenGL
%{_libdir}/libnvidia-fbc.so.1
%{_libdir}/libnvidia-fbc.so.%{version}
%{_libdir}/libnvidia-ifr.so.1
%{_libdir}/libnvidia-ifr.so.%{version}

%files NVML
%{_libdir}/libnvidia-ml.so.1
%{_libdir}/libnvidia-ml.so.%{version}

%files devel
%{_includedir}/nvidia/
%{_libdir}/libnvcuvid.so
%{_libdir}/libnvidia-encode.so

%changelog
* Wed Feb 15 2017 Simone Caronni <negativo17@gmail.com> - 2:378.13-1
- Update to 378.13.

* Mon Feb 06 2017 Simone Caronni <negativo17@gmail.com> - 2:378.09-2
- EGL external plaform configuration folders are now in libglvnd-egl.

* Thu Jan 19 2017 Simone Caronni <negativo17@gmail.com> - 2:378.09-1
- Update to 378.09.
- Remove libnvidia-egl-wayland as it is now built from source.
- Temporarily add EGL External Platform Interface configuration directories to
  the libs subpackage.

* Tue Jan 10 2017 Simone Caronni <negativo17@gmail.com> - 2:375.26-4
- Enable SLI and BaseMosaic (SLI multimonitor) by default.

* Wed Dec 21 2016 Simone Caronni <negativo17@gmail.com> - 2:375.26-3
- Do not enable nvidia-drm modeset by default yet.
- Adjust removal of obsolete kernel command line options for RHEL 6.
- Update OutputClass configuration for Intel/Optimus systems.

* Tue Dec 20 2016 Simone Caronni <negativo17@gmail.com> - 2:375.26-2
- Add configuration options for new OutputClass Device integration on Fedora 25
  with X server 1.19.0-3 (new 10-nvidia.conf configuration file).
- Trim changelog.
- Remove support for Fedora 23.
- Remove no longer needed kernel command line options.
- Enable modeset by default for the nvidia-drm module.

* Thu Dec 15 2016 Simone Caronni <negativo17@gmail.com> - 2:375.26-1
- Update to 375.26.

* Fri Dec 02 2016 Simone Caronni <negativo17@gmail.com> - 2:375.20-2
- Remove library location override from the libs subpackage.

* Sat Nov 19 2016 Simone Caronni <negativo17@gmail.com> - 2:375.20-1
- Update to 375.20.
- Add IgnoreABI only on Fedora 26+.
- Remove releases from AppStream metadata file (can't track between various
  beta, short lived, long lived releases).

* Thu Nov 03 2016 Simone Caronni <negativo17@gmail.com> - 2:375.10-4
- Nvidia driver version 375.10 is not yet compatible with X server version 1.19.

* Tue Oct 25 2016 Simone Caronni <negativo17@gmail.com> - 2:375.10-3
- Enable libglvnd 0.2.x based EGL.

* Mon Oct 24 2016 Simone Caronni <negativo17@gmail.com> - 2:375.10-2
- Add missing libglvnd library dependency.

* Sat Oct 22 2016 Simone Caronni <negativo17@gmail.com> - 2:375.10-1
- Update to 375.10.

* Fri Oct 21 2016 Simone Caronni <negativo17@gmail.com> - 2:370.28-6
- Update requirements on improved libglvnd package.

* Fri Oct 14 2016 Simone Caronni <negativo17@gmail.com> - 2:370.28-5
- Obsoletes/Provides cuda-drivers, as introduced in CUDA 8.0 packages.

* Sun Oct 09 2016 Simone Caronni <negativo17@gmail.com> - 2:370.28-4
- Require vulkan-filesystem on Fedora.

* Wed Sep 14 2016 Simone Caronni <negativo17@gmail.com> - 2:370.28-3
- Enable filtering by pci id in the AppStream metadata.

* Sun Sep 11 2016 Simone Caronni <negativo17@gmail.com> - 2:370.28-2
- Update AppStream metadata.

* Fri Sep 09 2016 Simone Caronni <negativo17@gmail.com> - 2:370.28-1
- Update to 370.28.

* Mon Sep 05 2016 Simone Caronni <negativo17@gmail.com> - 2:370.23-5
- Make the whole AppStream generation available only on Fedora 25+.

* Mon Sep 05 2016 Simone Caronni <negativo17@gmail.com> - 2:370.23-4
- Do not require nvidia-settings, make it possible to install without the GUI.

* Mon Sep 05 2016 Richard Hughes <richard@hughsie.com> - 2:370.23-3
- Add modaliases to the MetaInfo file to only match supported NVIDIA hardware

* Mon Sep 05 2016 Richard Hughes <richard@hughsie.com> - 2:370.23-2
- Install an MetaInfo so the driver appears in the software center

* Wed Aug 17 2016 Simone Caronni <negativo17@gmail.com> - 2:370.23-1
- Update to 370.23.

* Sat Aug 13 2016 Simone Caronni <negativo17@gmail.com> - 2:367.35-2
- Move IgnoreABI directive to Fedora 26+.

* Fri Jul 22 2016 Simone Caronni <negativo17@gmail.com> - 2:367.35-1
- Update to 367.35.

* Thu Jul 14 2016 Simone Caronni <negativo17@gmail.com> - 2:367.27-3
- Add unversioned CUVID library to devel subpackage for building FFMPeg 3.1
  CUVID support.

* Tue Jun 21 2016 Simone Caronni <negativo17@gmail.com> - 2:367.27-2
- Add missing dependency on CUDA libs for CUDA driver components. The automatic
  one went missing with libraries reorganization.

* Mon Jun 13 2016 Simone Caronni <negativo17@gmail.com> - 2:367.27-1
- Update to 367.27.
- Add libnvidia-egl-wayland.so to the library subpackage only on Fedora systems.

* Thu Jun 09 2016 Simone Caronni <negativo17@gmail.com> - 2:367.18-2
- Add unversioned libnvidia-encode shared object to devel subpackage; required
  to build the Gstreamer NVENC plugin.

* Thu May 26 2016 Simone Caronni <negativo17@gmail.com> - 2:367.18-1
- Update to 367.18.
- Load nvidia-uvm.ko through a soft dependency on nvidia.ko. This avoids
  inserting the nvidia-uvm configuration file in the initrd. Since the module
  is not (and should not be) in the initrd, this prevents the (harmless) module
  loading error in Plymouth.

* Mon May 02 2016 Simone Caronni <negativo17@gmail.com> - 2:364.19-1
- Update to 364.19.
- Disable modeset by default. There is no fb driver and the only consumer is a
  custom build of Wayland with rejected patches.

* Fri Apr 08 2016 Simone Caronni <negativo17@gmail.com> - 2:364.15-1
- Update to 364.15.
- Requires libglvnd >= 0.1.0.

* Tue Mar 22 2016 Simone Caronni <negativo17@gmail.com> - 2:364.12-1
- Update to 364.12.
- Add Vulkan and DRM KMS support.
- Do not require vulkan-filesystem (yet):
  https://copr.fedorainfracloud.org/coprs/ajax/vulkan/
- Update description.

* Sun Feb 28 2016 Simone Caronni <negativo17@gmail.com> - 2:361.28-3
- Re-enable libglvnd libGL.so library.

* Tue Feb 16 2016 Simone Caronni <negativo17@gmail.com> - 2:361.28-2
- Use non-libglvnd libGL as per default Nvidia installation, some Steam games
  check for non-abi stuff in libGL.

* Tue Feb 09 2016 Simone Caronni <negativo17@gmail.com> - 2:361.28-1
- Update to 361.28.
- Add new symlink libGLX_indirect.so.0.

* Thu Jan 14 2016 Simone Caronni <negativo17@gmail.com> - 2:361.18-1
- Update to 361.18.

* Tue Jan 05 2016 Simone Caronni <negativo17@gmail.com> - 2:361.16-1
- Update to 361.16, use libglvnd libraries for everything except EGL.
- Remove ARM (Carma, Kayla) support.
- Use new X.org OutputClass loader for RHEL 7 (X.org 1.16+, RHEL 7.2+).

* Fri Nov 20 2015 Simone Caronni <negativo17@gmail.com> - 2:358.16-1
- Update to 358.16.

* Wed Nov 18 2015 Simone Caronni <negativo17@gmail.com> - 2:358.09-2
- Add kernel command line also to Grub default files for grub2-mkconfig
  consumption.
- Create new macro for grubby command in post.
- Remove support for Grub 0.97 in Fedora or CentOS/RHEL 7.

* Tue Oct 13 2015 Simone Caronni <negativo17@gmail.com> - 2:358.09-1
- Update to 358.09.

* Wed Sep 30 2015 Simone Caronni <negativo17@gmail.com> - 2:355.11-3
- Update modprobe configuration file position in CentOS/RHEL 6.

* Tue Sep 08 2015 Simone Caronni <negativo17@gmail.com> - 2:355.11-2
- Update isa requirements.

* Tue Sep 01 2015 Simone Caronni <negativo17@gmail.com> - 2:355.11-1
- Update to 355.11.

* Sat Aug 22 2015 Simone Caronni <negativo17@gmail.com> - 2:355.06-2
- Re-add nvidia-driver-libs requirement mistakenly removed in latest
  reorganization.

* Tue Aug 04 2015 Simone Caronni <negativo17@gmail.com> - 2:355.06-1
- Update to 355.06.
- Add new libglvnd support (OpenGL only, no GLX or GL for now). EGL is included
  here but not in libglvnd (?), so it's still here.
- Remove Fedora 20 checks now that is EOL.
- Fix NvFBCOpenGL requirements.
- Split out NVML in its own subpackage, so trying to build against it does not
  install the whole CUDA stack with modules.
- Move all libraries that do not replace system libraries in the default
  directories. There is no reason to keep them separate and this helps for
  building programs that link to these libraries (like nvidia-settings on NVML)
  and for writing out filters in the SPEC file.
- Build requires execstack in place of prelink on Fedora 23+.
- Rework completely symlink creation using ldconfig, remove useless symlink and
  trim devel subpackage.

* Wed Jul 29 2015 Simone Caronni <negativo17@gmail.com> - 2:352.30-1
- Update to 352.30.

* Wed Jun 17 2015 Simone Caronni <negativo17@gmail.com> - 2:352.21-1
- Update to 352.21.

* Mon Jun 08 2015 Simone Caronni <negativo17@gmail.com> - 2:352.09-2
- Ignore ABI configuration file moved to Fedora 23+.

* Tue May 19 2015 Simone Caronni <negativo17@gmail.com> - 2:352.09-1
- Update to 352.09.

* Wed May 13 2015 Simone Caronni <negativo17@gmail.com> - 2:346.72-1
- Update to 346.72.

* Mon Apr 27 2015 Simone Caronni <negativo17@gmail.com> - 2:346.59-2
- Load nvidia-uvm when installing nvidia-driver-cuda.

* Tue Apr 07 2015 Simone Caronni <negativo17@gmail.com> - 2:346.59-1
- Update to 346.59.

* Wed Feb 25 2015 Simone Caronni <negativo17@gmail.com> - 2:346.47-1
- Update to 346.47.
- Add license macro.

* Thu Jan 29 2015 Simone Caronni <negativo17@gmail.com> - 2:346.35-3
- Fix grubby command line.

* Wed Jan 28 2015 Simone Caronni <negativo17@gmail.com> - 2:346.35-2
- Update kernel parameters on all installed kernels, not just current. This
  solves issues when updating kernel, not rebooting, and installing the driver
  afterwards.

* Sat Jan 17 2015 Simone Caronni <negativo17@gmail.com> - 2:346.35-1
- Update to 346.35.

* Mon Jan 12 2015 Simone Caronni <negativo17@gmail.com> - 2:346.22-2
- RHEL/CentOS 7 does not have OpenCL packages (thanks stj).
