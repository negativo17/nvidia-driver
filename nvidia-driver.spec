%global debug_package %{nil}
%global __brp_strip %{nil}
%global __brp_ldconfig %{nil}
%define _build_id_links none

# systemd 248+
%if 0%{?rhel} == 8
%global _systemd_util_dir %{_prefix}/lib/systemd
%endif

Name:           nvidia-driver
Version:        580.105.08
Release:        1%{?dist}
Summary:        NVIDIA's proprietary display driver for NVIDIA graphic cards
Epoch:          3
License:        NVIDIA License
URL:            http://www.nvidia.com/object/unix.html
ExclusiveArch:  %{ix86} x86_64 aarch64

Source0:        %{name}-%{version}-i386.tar.xz
Source1:        %{name}-%{version}-x86_64.tar.xz
Source2:        %{name}-%{version}-aarch64.tar.xz
Source8:        70-nvidia-driver.preset
Source9:        70-nvidia-driver-cuda.preset
Source10:       10-nvidia.conf
Source13:       alternate-install-present

Source40:       com.nvidia.driver.metainfo.xml
Source41:       parse-supported-gpus.py
Source42:       com.nvidia.driver.png

Source99:       nvidia-generate-tarballs.sh

%ifarch x86_64 aarch64
BuildRequires:  libappstream-glib
%if 0%{?rhel} == 8
# xml.etree.ElementTree has indent only from 3.9+:
BuildRequires:  python(abi) >= 3.9
%else
BuildRequires:  python3
%endif
BuildRequires:  systemd-rpm-macros
%endif

Requires:       nvidia-driver-libs%{?_isa} = %{?epoch:%{epoch}:}%{version}
Requires:       nvidia-kmod-common = %{?epoch:%{epoch}:}%{version}

Conflicts:      nvidia-x11-drv
Conflicts:      nvidia-x11-drv-470xx
Conflicts:      xorg-x11-drv-nvidia
Conflicts:      xorg-x11-drv-nvidia-470xx

%description
This package provides the most recent NVIDIA display driver which allows for
hardware accelerated rendering with recent NVIDIA chipsets.

For the full product support list, please consult the release notes for driver
version %{version}.

%package libs
Summary:        Libraries for %{name}
Requires:       egl-gbm%{?_isa} >= 2:1.1.2.1
Requires:       (egl-wayland%{?_isa} >= 1.1.20 or egl-wayland2%{?_isa} >= 1.0.0~20250806gitd4deb7c-3)
Suggests:       egl-wayland%{?_isa} >= 1.1.20
Requires:       egl-x11%{?_isa} >= 1.0.3
Requires:       libvdpau%{?_isa} >= 1.5
Requires:       libglvnd%{?_isa} >= 1.0
Requires:       libglvnd-egl%{?_isa} >= 1.0
Requires:       libglvnd-gles%{?_isa} >= 1.0
Requires:       libglvnd-glx%{?_isa} >= 1.0
Requires:       libglvnd-opengl%{?_isa} >= 1.0
Requires:       vulkan-loader
#  dlopened:
Requires:       libnvidia-gpucomp%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Requires:       libnvidia-ml%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}

Conflicts:      nvidia-x11-drv-libs
Conflicts:      nvidia-x11-drv-470xx-libs
Conflicts:      xorg-x11-drv-nvidia-libs
Conflicts:      xorg-x11-drv-nvidia-470xx-libs

%description libs
This package provides the shared libraries for %{name}.

%package cuda-libs
Summary:        Libraries for %{name}-cuda
Provides:       %{name}-devel = %{?epoch:%{epoch}:}%{version}-%{release}
Obsoletes:      %{name}-devel < %{?epoch:%{epoch}:}%{version}-%{release}

# dlopened:
%ifarch x86_64 aarch64
Requires:       libnvidia-cfg = %{?epoch:%{epoch}:}%{version}-%{release}
%endif
Requires:       libnvidia-gpucomp%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Requires:       libnvidia-ml = %{?epoch:%{epoch}:}%{version}-%{release}

Conflicts:      xorg-x11-drv-nvidia-cuda-libs
Conflicts:      xorg-x11-drv-nvidia-470xx-cuda-libs

%description cuda-libs
This package provides the CUDA libraries for %{name}-cuda.

%package -n libnvidia-fbc
Summary:        NVIDIA OpenGL-based Framebuffer Capture libraries
Provides:       nvidia-driver-NvFBCOpenGL = %{?epoch:%{epoch}:}%{version}-%{release}
Obsoletes:      nvidia-driver-NvFBCOpenGL < %{?epoch:%{epoch}:}%{version}-%{release}
# dlopened (libnvidia-encode.so):
Requires:       %{name}-cuda-libs%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}

%description -n libnvidia-fbc
This library provides a high performance, low latency interface to capture and
optionally encode the composited framebuffer of an X screen. NvFBC are private
APIs that are only available to NVIDIA approved partners for use in remote
graphics scenarios.

%package -n libnvidia-gpucomp
Summary:        NVIDIA library for shader compilation (nvgpucomp)

%description -n libnvidia-gpucomp
This package contains the private libnvidia-gpucomp runtime library which is used by
other driver components.

%package -n libnvidia-ml
Summary:        NVIDIA Management Library (NVML)
Provides:       cuda-nvml%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Provides:       nvidia-driver-NVML = %{?epoch:%{epoch}:}%{version}-%{release}
Obsoletes:      nvidia-driver-NVML < %{?epoch:%{epoch}:}%{version}-%{release}

%description -n libnvidia-ml
A C-based API for monitoring and managing various states of the NVIDIA GPU
devices. It provides a direct access to the queries and commands exposed via
nvidia-smi. The run-time version of NVML ships with the NVIDIA display driver,
and the SDK provides the appropriate header, stub libraries and sample
applications. Each new version of NVML is backwards compatible and is intended
to be a platform for building 3rd party applications.

%ifarch x86_64 aarch64

%package -n libnvidia-cfg
Summary:        NVIDIA Config public interface (nvcfg)

%description -n libnvidia-cfg
This package contains the private libnvidia-cfg runtime library which is used by
other driver components.

%package cuda
Summary:        CUDA integration for %{name}
Requires:       %{name}-cuda-libs%{?_isa} = %{?epoch:%{epoch}:}%{version}
Requires:       nvidia-kmod-common = %{?epoch:%{epoch}:}%{version}
Requires:       nvidia-persistenced = %{?epoch:%{epoch}:}%{version}
Requires:       (ocl-icd or OpenCL-ICD-Loader)
Requires:       opencl-filesystem

Conflicts:      xorg-x11-drv-nvidia-cuda
Conflicts:      xorg-x11-drv-nvidia-470xx-cuda

%description cuda
This package provides the CUDA integration components for %{name}.

%if 0%{?fedora} || 0%{?rhel} < 10
%package -n xorg-x11-nvidia
Summary:        X.org X11 NVIDIA driver and extensions
Requires:       %{name}%{?_isa} = %{?epoch:%{epoch}:}%{version}
Requires:       xorg-x11-server-Xorg%{?_isa}
Supplements:    (nvidia-driver and xorg-x11-server-Xorg)

Conflicts:      xorg-x11-drv-nvidia
Conflicts:      xorg-x11-drv-nvidia-470xx

%description -n xorg-x11-nvidia
The NVIDIA X.org X11 driver and associated components.
%endif

%endif
 
%prep
%ifarch %{ix86}
%setup -q -n %{name}-%{version}-i386
%endif

%ifarch x86_64
%setup -q -T -b 1 -n %{name}-%{version}-x86_64
%endif

%ifarch aarch64
%setup -q -T -b 2 -n %{name}-%{version}-aarch64
%endif

%ifarch x86_64
%if 0%{?rhel} == 8
rm -f libnvidia-pkcs11-openssl3.so.%{version}
%else
rm -f libnvidia-pkcs11.so.%{version}
%endif
%endif

# Create symlinks for shared objects
ldconfig -vn .

# Required for building gstreamer 1.0 NVENC plugins
ln -sf libnvidia-encode.so.%{version} libnvidia-encode.so

# Required for building ffmpeg 3.1 Nvidia CUVID
ln -sf libnvcuvid.so.%{version} libnvcuvid.so

# Required for building against CUDA
ln -sf libcuda.so.%{version} libcuda.so

%build

%install
# EGL loader
install -p -m 0644 -D 10_nvidia.json %{buildroot}%{_datadir}/glvnd/egl_vendor.d/10_nvidia.json

# Vulkan loader
install -p -m 0644 -D nvidia_icd.json %{buildroot}%{_datadir}/vulkan/icd.d/nvidia_icd.%{_target_cpu}.json
sed -i -e 's|libGLX_nvidia|%{_libdir}/libGLX_nvidia|g' %{buildroot}%{_datadir}/vulkan/icd.d/nvidia_icd.%{_target_cpu}.json

%ifarch x86_64
# Vulkan SC loader and compiler
install -p -m 0644 -D nvidia_icd_vksc.json %{buildroot}%{_datadir}/vulkansc/icd.d/nvidia_icd.%{_target_cpu}.json
sed -i -e 's|libnvidia-vksc-core|%{_libdir}/libnvidia-vksc-core|g' %{buildroot}%{_datadir}/vulkansc/icd.d/nvidia_icd.%{_target_cpu}.json
install -p -m 0755 -D nvidia-pcc %{buildroot}%{_bindir}/nvidia-pcc
%endif

# Unique libraries
mkdir -p %{buildroot}%{_libdir}/vdpau/
cp -a lib*GL*_nvidia.so* libcuda*.so* libnv*.so* %{buildroot}%{_libdir}/
cp -a libvdpau_nvidia.so* %{buildroot}%{_libdir}/vdpau/

%if 0%{?fedora} || 0%{?rhel} >= 9
# GBM loader
mkdir -p %{buildroot}%{_libdir}/gbm/
ln -sf ../libnvidia-allocator.so.%{version} %{buildroot}%{_libdir}/gbm/nvidia-drm_gbm.so
%endif

%ifarch x86_64

# NGX Proton/Wine library
mkdir -p %{buildroot}%{_libdir}/nvidia/wine/
cp -a *.dll %{buildroot}%{_libdir}/nvidia/wine/

%endif

%ifarch x86_64 aarch64

# alternate-install-present file triggers runfile warning
install -m 0755 -d %{buildroot}/usr/lib/nvidia/
install -p -m 0644 %{SOURCE13} %{buildroot}/usr/lib/nvidia/

# Empty?
mkdir -p %{buildroot}%{_sysconfdir}/nvidia/

# OpenCL config
install -p -m 0755 -D nvidia.icd %{buildroot}%{_sysconfdir}/OpenCL/vendors/nvidia.icd

# Binaries
mkdir -p %{buildroot}%{_bindir}
install -p -m 0755 nvidia-{debugdump,smi,cuda-mps-control,cuda-mps-server,ngx-updater,powerd} %{buildroot}%{_bindir}

# Man pages
mkdir -p %{buildroot}%{_mandir}/man1/
install -p -m 0644 nvidia-{smi,cuda-mps-control}*.gz %{buildroot}%{_mandir}/man1/

%if 0%{?fedora} || 0%{?rhel} < 10
# X stuff
install -p -m 0644 -D %{SOURCE10} %{buildroot}%{_sysconfdir}/X11/xorg.conf.d/10-nvidia.conf
install -p -m 0755 -D nvidia_drv.so %{buildroot}%{_libdir}/xorg/modules/drivers/nvidia_drv.so
install -p -m 0755 -D libglxserver_nvidia.so.%{version} %{buildroot}%{_libdir}/xorg/modules/extensions/libglxserver_nvidia.so
%endif

# NVIDIA specific configuration files
mkdir -p %{buildroot}%{_datadir}/nvidia/
install -p -m 0644 nvidia-application-profiles-%{version}-key-documentation \
    %{buildroot}%{_datadir}/nvidia/
install -p -m 0644 nvidia-application-profiles-%{version}-rc \
    %{buildroot}%{_datadir}/nvidia/

# OptiX
install -p -m 0644 nvoptix.bin %{buildroot}%{_datadir}/nvidia/

# Systemd units and script for suspending/resuming
mkdir -p %{buildroot}%{_systemd_util_dir}/system-preset/
install -p -m 0644 %{SOURCE8} %{SOURCE9} %{buildroot}%{_systemd_util_dir}/system-preset/
mkdir -p %{buildroot}%{_unitdir}/
install -p -m 0644 systemd/system/*.service %{buildroot}%{_unitdir}/
install -p -m 0755 systemd/nvidia-sleep.sh %{buildroot}%{_bindir}/
install -p -m 0755 -D systemd/system-sleep/nvidia %{buildroot}%{_systemd_util_dir}/system-sleep/nvidia
install -p -m 0644 -D nvidia-dbus.conf %{buildroot}%{_datadir}/dbus-1/system.d/nvidia-dbus.conf

# Ignore powerd binary exiting if hardware is not present
# We should check for information in the DMI table
sed -i -e 's/ExecStart=/ExecStart=-/g' %{buildroot}%{_unitdir}/nvidia-powerd.service

# Vulkan layer
install -p -m 0644 -D nvidia_layers.json %{buildroot}%{_datadir}/vulkan/implicit_layer.d/nvidia_layers.json

# Install AppData and add modalias provides, do not use appstream-util add-provide as it mangles the xml
install -p -m 0644 -D %{SOURCE40} %{buildroot}%{_metainfodir}/com.nvidia.driver.metainfo.xml
%{SOURCE41} supported-gpus/supported-gpus.json %{buildroot}%{_metainfodir}/com.nvidia.driver.metainfo.xml
mkdir -p %{buildroot}%{_datadir}/pixmaps/
cp %{SOURCE42} %{buildroot}%{_datadir}/pixmaps/

# nvsandboxutils configuration
install -p -m 0644 -D sandboxutils-filelist.json %{buildroot}%{_datadir}/nvidia/files.d/sandboxutils-filelist.json

# dnf needs-restarting plugin
# dnf4 only for the moment: https://github.com/rpm-software-management/dnf5/issues/1815
%if 0%{?fedora} < 42 || 0%{?rhel}
mkdir -p %{buildroot}%{_sysconfdir}/dnf/plugins/needs-restarting.d
echo %{name} > %{buildroot}%{_sysconfdir}/dnf/plugins/needs-restarting.d/%{name}.conf
echo %{name}-cuda > %{buildroot}%{_sysconfdir}/dnf/plugins/needs-restarting.d/%{name}-cuda.conf
%endif

%check
# Using appstreamcli: appstreamcli validate --strict
# Icon type local is not supported by appstreamcli for drivers
appstream-util validate --nonet %{buildroot}%{_metainfodir}/com.nvidia.driver.metainfo.xml

%endif

%ifarch x86_64 aarch64

%post
%systemd_post nvidia-hibernate.service
%systemd_post nvidia-powerd.service
%systemd_post nvidia-resume.service
%systemd_post nvidia-suspend.service
%systemd_post nvidia-suspend-then-hibernate.service

%preun
%systemd_preun nvidia-hibernate.service
%systemd_preun nvidia-powerd.service
%systemd_preun nvidia-resume.service
%systemd_preun nvidia-suspend.service
%systemd_preun nvidia-suspend-then-hibernate.service

%postun
%systemd_postun nvidia-hibernate.service
%systemd_postun nvidia-powerd.service
%systemd_postun nvidia-resume.service
%systemd_postun nvidia-suspend.service
%systemd_postun nvidia-suspend-then-hibernate.service

%endif

%ifarch x86_64 aarch64

%files
%license LICENSE
%doc NVIDIA_Changelog README.txt html supported-gpus/supported-gpus.json
%dir %{_sysconfdir}/nvidia
%{_bindir}/nvidia-ngx-updater
%ifarch x86_64
%{_bindir}/nvidia-pcc
%endif
%{_bindir}/nvidia-powerd
%{_bindir}/nvidia-sleep.sh
%{_metainfodir}/com.nvidia.driver.metainfo.xml
%{_datadir}/dbus-1/system.d/nvidia-dbus.conf
%{_datadir}/nvidia/nvidia-application-profiles*
%{_datadir}/pixmaps/com.nvidia.driver.png
%{_systemd_util_dir}/system-preset/70-nvidia-driver.preset
%{_systemd_util_dir}/system-sleep/nvidia
%{_unitdir}/nvidia-hibernate.service
%{_unitdir}/nvidia-powerd.service
%{_unitdir}/nvidia-resume.service
%{_unitdir}/nvidia-suspend.service
%{_unitdir}/nvidia-suspend-then-hibernate.service
%if 0%{?fedora} < 42 || 0%{?rhel}
%{_sysconfdir}/dnf/plugins/needs-restarting.d/%{name}.conf
%endif

%if 0%{?fedora} || 0%{?rhel} < 10
%files -n xorg-x11-nvidia
%config(noreplace) %{_sysconfdir}/X11/xorg.conf.d/10-nvidia.conf
%{_libdir}/xorg/modules/extensions/libglxserver_nvidia.so
%{_libdir}/xorg/modules/drivers/nvidia_drv.so
%endif

%files -n libnvidia-cfg
%{_libdir}/libnvidia-cfg.so.1
%{_libdir}/libnvidia-cfg.so.%{version}

%files cuda
%{_sysconfdir}/OpenCL/vendors/*
%{_bindir}/nvidia-cuda-mps-control
%{_bindir}/nvidia-cuda-mps-server
%{_bindir}/nvidia-debugdump
%{_bindir}/nvidia-smi
%{_datadir}/nvidia/files.d/sandboxutils-filelist.json
%{_mandir}/man1/nvidia-cuda-mps-control.1.*
%{_mandir}/man1/nvidia-smi.*
%{_prefix}/lib/nvidia/alternate-install-present
%{_systemd_util_dir}/system-preset/70-nvidia-driver-cuda.preset
%if 0%{?fedora} < 42 || 0%{?rhel}
%{_sysconfdir}/dnf/plugins/needs-restarting.d/%{name}-cuda.conf
%endif

%endif

%files libs
%{_datadir}/glvnd/egl_vendor.d/10_nvidia.json
%{_datadir}/vulkan/icd.d/nvidia_icd.%{_target_cpu}.json
%if 0%{?fedora} || 0%{?rhel} >= 9
%dir %{_libdir}/gbm
%{_libdir}/gbm/nvidia-drm_gbm.so
%endif
%{_libdir}/libEGL_nvidia.so.0
%{_libdir}/libEGL_nvidia.so.%{version}
%{_libdir}/libGLESv1_CM_nvidia.so.1
%{_libdir}/libGLESv1_CM_nvidia.so.%{version}
%{_libdir}/libGLESv2_nvidia.so.2
%{_libdir}/libGLESv2_nvidia.so.%{version}
%{_libdir}/libGLX_nvidia.so.0
%{_libdir}/libGLX_nvidia.so.%{version}
%{_libdir}/libnvidia-allocator.so.1
%{_libdir}/libnvidia-allocator.so.%{version}
%{_libdir}/libnvidia-eglcore.so.%{version}
%{_libdir}/libnvidia-glcore.so.%{version}
%{_libdir}/libnvidia-glsi.so.%{version}
%{_libdir}/libnvidia-glvkspirv.so.%{version}
%{_libdir}/libnvidia-tls.so.%{version}
%{_libdir}/vdpau/libvdpau_nvidia.so.1
%{_libdir}/vdpau/libvdpau_nvidia.so.%{version}
%ifarch x86_64 aarch64
%{_datadir}/nvidia/nvoptix.bin
%{_datadir}/vulkan/implicit_layer.d/nvidia_layers.json
%{_libdir}/libnvidia-api.so.1
%{_libdir}/libnvidia-ngx.so.1
%{_libdir}/libnvidia-ngx.so.%{version}
%{_libdir}/libnvidia-rtcore.so.%{version}
%{_libdir}/libnvoptix.so.1
%{_libdir}/libnvoptix.so.%{version}
%endif
%ifarch x86_64
%{_datadir}/vulkansc/icd.d/nvidia_icd.%{_target_cpu}.json
%{_libdir}/libnvidia-present.so.%{version}
%{_libdir}/libnvidia-vksc-core.so.1
%{_libdir}/libnvidia-vksc-core.so.%{version}
%dir %{_libdir}/nvidia
%dir %{_libdir}/nvidia/wine
%{_libdir}/nvidia/wine/_nvngx.dll
%{_libdir}/nvidia/wine/nvngx.dll
%{_libdir}/nvidia/wine/nvngx_dlssg.dll
%endif

%files cuda-libs
%{_libdir}/libcuda.so
%{_libdir}/libcuda.so.1
%{_libdir}/libcuda.so.%{version}
%{_libdir}/libnvcuvid.so
%{_libdir}/libnvcuvid.so.1
%{_libdir}/libnvcuvid.so.%{version}
%{_libdir}/libnvidia-encode.so
%{_libdir}/libnvidia-encode.so.1
%{_libdir}/libnvidia-encode.so.%{version}
%{_libdir}/libnvidia-nvvm.so.4
%{_libdir}/libnvidia-nvvm.so.%{version}
%{_libdir}/libnvidia-opencl.so.1
%{_libdir}/libnvidia-opencl.so.%{version}
%{_libdir}/libnvidia-opticalflow.so.1
%{_libdir}/libnvidia-opticalflow.so.%{version}
%{_libdir}/libnvidia-ptxjitcompiler.so.1
%{_libdir}/libnvidia-ptxjitcompiler.so.%{version}
%ifarch x86_64 aarch64
%{_libdir}/libcudadebugger.so.1
%{_libdir}/libcudadebugger.so.%{version}
%{_libdir}/libnvidia-nvvm70.so.4
%{_libdir}/libnvidia-sandboxutils.so.1
%{_libdir}/libnvidia-sandboxutils.so.%{version}
%endif
%ifarch x86_64
%if 0%{?rhel} == 8
%{_libdir}/libnvidia-pkcs11.so.%{version}
%else
%{_libdir}/libnvidia-pkcs11-openssl3.so.%{version}
%endif
%endif

%files -n libnvidia-fbc
%{_libdir}/libnvidia-fbc.so.1
%{_libdir}/libnvidia-fbc.so.%{version}

%files -n libnvidia-gpucomp
%{_libdir}/libnvidia-gpucomp.so.%{version}

%files -n libnvidia-ml
%{_libdir}/libnvidia-ml.so.1
%{_libdir}/libnvidia-ml.so.%{version}

%changelog
* Fri Nov 07 2025 Simone Caronni <negativo17@gmail.com> - 3:580.105.08-1
- Update to 580.105.08.

* Wed Oct 01 2025 Simone Caronni <negativo17@gmail.com> - 3:580.95.05-1
- Update to 580.95.05.
- Move nvidia-bug-report.sh to nvidia-kmod-common.
- Update tarball script.
- Fix duplicate library in nvidia-driver-libs and libnvidia-gpucomp.

* Thu Sep 11 2025 Simone Caronni <negativo17@gmail.com> - 3:580.82.09-1
- Update to 580.82.09.

* Tue Sep 02 2025 Simone Caronni <negativo17@gmail.com> - 3:580.82.07-2
- Enable missing systemd unit.

* Mon Sep 01 2025 Simone Caronni <negativo17@gmail.com> - 3:580.82.07-1
- Update to 580.82.07.

* Fri Aug 22 2025 Simone Caronni <negativo17@gmail.com> - 3:580.76.05-2
- Update EGl requirements.

* Thu Aug 14 2025 Simone Caronni <negativo17@gmail.com> - 3:580.76.05-1
- Update to 580.76.05.

* Tue Aug 05 2025 Simone Caronni <negativo17@gmail.com> - 3:580.65.06-1
- Update to 580.65.06.

* Wed Jul 23 2025 Simone Caronni <negativo17@gmail.com> - 3:575.64.05-1
- Update to 575.64.05.

* Tue Jul 01 2025 Simone Caronni <negativo17@gmail.com> - 3:575.64.03-1
- Update to 575.64.03.

* Wed Jun 18 2025 Simone Caronni <negativo17@gmail.com> - 3:575.64-1
- Update to 575.64.

* Thu May 29 2025 Simone Caronni <negativo17@gmail.com> - 3:575.57.08-1
- Update to 575.57.08.

* Tue May 20 2025 Simone Caronni <negativo17@gmail.com> - 3:575.51.02-1
- Update to 575.51.02.
- libnvidia-gpucomp is now required by both desktop and CUDA only components.

* Tue May 20 2025 Simone Caronni <negativo17@gmail.com> - 3:570.153.02-1
- Update to 570.153.02.

* Tue Apr 22 2025 Simone Caronni <negativo17@gmail.com> - 3:570.144-1
- Update to 570.144.

* Wed Mar 19 2025 Simone Caronni <negativo17@gmail.com> - 3:570.133.07-1
- Update to 570.133.07.

* Thu Mar 13 2025 Simone Caronni <negativo17@gmail.com> - 3:570.124.04-3
- Remove workaround for system sleep on systemd 256+.

* Wed Mar 12 2025 Simone Caronni <negativo17@gmail.com> - 3:570.124.04-2
- Add DNF4 needs-restarting plugin support.

* Fri Feb 28 2025 Simone Caronni <negativo17@gmail.com> - 3:570.124.04-1
- Update to 570.124.04.

* Sat Feb 08 2025 Simone Caronni <negativo17@gmail.com> - 3:570.86.16-2
- Do not build X components for el10+.

* Fri Jan 31 2025 Simone Caronni <negativo17@gmail.com> - 3:570.86.16-1
- Update to 570.86.16.

* Mon Jan 27 2025 Simone Caronni <negativo17@gmail.com> - 3:570.86.15-1
- Update to 570.86.15.

* Mon Jan 20 2025 Simone Caronni <negativo17@gmail.com> - 3:565.77-2
- Allow using OpenCL-ICD-Loader in place of ocl-icd.

* Thu Dec 05 2024 Simone Caronni <negativo17@gmail.com> - 3:565.77-1
- Update to 565.77.

* Mon Nov 25 2024 Simone Caronni <negativo17@gmail.com> - 3:565.57.01-5
- Switch back to local icon.

* Fri Nov 15 2024 Simone Caronni <negativo17@gmail.com> - 3:565.57.01-4
- Do not manipulate appstream metadata using libappstream-glib.

* Sat Nov 09 2024 Simone Caronni <negativo17@gmail.com> - 3:565.57.01-3
- Switch to remote icon for Appstream metadata. "appstremcli validate", instead
  of "appstream-util validate", prints out that local is not a valid icon type,
  even if the documentation says so.

* Sun Oct 27 2024 Simone Caronni <negativo17@gmail.com> - 3:565.57.01-2
- Add workaround for system sleep on systemd 256+.

* Wed Oct 23 2024 Simone Caronni <negativo17@gmail.com> - 3:565.57.01-1
- Update to 565.57.01.

* Thu Oct 10 2024 Simone Caronni <negativo17@gmail.com> - 3:560.35.03-4
- Enable nvidia-persistenced by default if installed through a systemd preset.

* Wed Sep 04 2024 Simone Caronni <negativo17@gmail.com> - 3:560.35.03-3
- Unbundle nvidia-egl-platform-base.

* Fri Aug 30 2024 Simone Caronni <negativo17@gmail.com> - 3:560.35.03-2
- Split out X.org components.

* Wed Aug 21 2024 Simone Caronni <negativo17@gmail.com> - 3:560.35.03-1
- Update to 560.35.03.

* Tue Aug 06 2024 Simone Caronni <negativo17@gmail.com> - 3:560.31.02-1
- Update to 560.31.02.
- Update EGL requirements.

* Mon Aug 05 2024 Simone Caronni <negativo17@gmail.com> - 3:560.28.03-1
- Update to 560.28.03.
- Add Vulkan Safety Critical library and offline Pipeline Cache Compiler.
- Temporarily add new EGL libraries.

* Mon Jul 15 2024 Simone Caronni <negativo17@gmail.com> - 3:555.58.02-3
- Provider of cuda-nvml still needs _isa.

* Sat Jul 13 2024 Simone Caronni <negativo17@gmail.com> - 3:555.58.02-2
- Remove isa Provides/Requires.

* Tue Jul 02 2024 Simone Caronni <negativo17@gmail.com> - 3:555.58.02-1
- Update to 555.58.02.
- Reorganize some libraries that get dynamically opened by other components.

* Sat Jun 29 2024 Simone Caronni <negativo17@gmail.com> - 3:555.58-4
- Adjust Appstream icon path.

* Fri Jun 28 2024 Simone Caronni <negativo17@gmail.com> - 3:555.58-3
- Switch to local icon for Appstream metadata before madness takes over.

* Fri Jun 28 2024 Simone Caronni <negativo17@gmail.com> - 3:555.58-2
- Make sure there are no redirects in the Appstream metadata URLs.

* Thu Jun 27 2024 Simone Caronni <negativo17@gmail.com> - 3:555.58-1
- Update to 555.58.

* Wed Jun 26 2024 Simone Caronni <negativo17@gmail.com> - 3:555.52.04-2
- Update AppData metadata, add new custom key entry:
  https://gitlab.gnome.org/GNOME/gnome-software/-/merge_requests/2034

* Thu Jun 06 2024 Simone Caronni <negativo17@gmail.com>
- Update to 555.52.04.

* Fri May 31 2024 Simone Caronni <negativo17@gmail.com> - 3:555.42.02-3
- Fix file format specification for Vulkan layers.

* Mon May 27 2024 Simone Caronni <negativo17@gmail.com> - 3:555.42.02-2
- Add GBM loader library symlink also for i686 libraries (#156).
- Also own the %%_libdir/gbm directory.

* Wed May 22 2024 Simone Caronni <negativo17@gmail.com> - 3:555.42.02-1
- Update to 555.42.02.

* Fri Apr 26 2024 Simone Caronni <negativo17@gmail.com> - 3:550.78-1
- Update to 550.78.

* Fri Apr 26 2024 Simone Caronni <negativo17@gmail.com> - 3:550.76-2
- Install Vulkan loader in a more similar way to Mesa packages.

* Thu Apr 18 2024 Simone Caronni <negativo17@gmail.com> - 3:550.76-1
- Update to 550.76.

* Mon Apr 15 2024 Simone Caronni <negativo17@gmail.com> - 3:550.67-2
- Fix egl requirements.

* Sun Mar 24 2024 Simone Caronni <negativo17@gmail.com> - 3:550.67-1
- Update to 550.67.

* Thu Mar 14 2024 Simone Caronni <negativo17@gmail.com> - 3:550.54.14-3
- Clean up SPEC file.

* Fri Mar 08 2024 Simone Caronni <negativo17@gmail.com> - 3:550.54.14-2
- Add support for aarch64.
- Clean up SPEC file.

* Sun Mar 03 2024 Simone Caronni <negativo17@gmail.com> - 3:550.54.14-1
- Update to 550.54.14.

* Thu Feb 22 2024 Simone Caronni <negativo17@gmail.com> - 3:550.40.07-1
- Update to 550.40.07.

* Fri Feb 16 2024 Simone Caronni <negativo17@gmail.com> - 3:545.29.06-3
- Re-add explicit egl-wayland dependency (reverts
  cd6f2b9044d90f71f94fa91be1cc0cad343a1560).
