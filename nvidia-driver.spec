%global debug_package %{nil}
%global __strip /bin/true
%global __brp_ldconfig %{nil}

# systemd 248+
%if 0%{?rhel} == 7 || 0%{?rhel} == 8
%global _systemd_util_dir %{_prefix}/lib/systemd
%endif

Name:           nvidia-driver
Version:        555.58.02
Release:        1%{?dist}
Summary:        NVIDIA's proprietary display driver for NVIDIA graphic cards
Epoch:          3
License:        NVIDIA License
URL:            http://www.nvidia.com/object/unix.html
ExclusiveArch:  %{ix86} x86_64 aarch64

Source0:        %{name}-%{version}-i386.tar.xz
Source1:        %{name}-%{version}-x86_64.tar.xz
Source2:        %{name}-%{version}-aarch64.tar.xz
Source9:        70-nvidia.preset
Source10:       10-nvidia.conf
Source13:       alternate-install-present

Source40:       com.nvidia.driver.metainfo.xml
Source41:       parse-supported-gpus.py
Source42:       %{name}.png

Source99:       nvidia-generate-tarballs.sh

%ifarch x86_64 aarch64

%if 0%{?fedora} || 0%{?rhel} >= 8
BuildRequires:  libappstream-glib
BuildRequires:  python3
BuildRequires:  systemd-rpm-macros
%else
BuildRequires:  systemd
%endif

%endif

Requires:       nvidia-driver-libs%{?_isa} = %{?epoch:%{epoch}:}%{version}
Requires:       nvidia-kmod-common = %{?epoch:%{epoch}:}%{version}
Requires:       xorg-x11-server-Xorg%{?_isa}

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
Requires:       libvdpau%{?_isa} >= 0.5
Requires:       libglvnd%{?_isa} >= 1.0
Requires:       libglvnd-egl%{?_isa} >= 1.0
Requires:       libglvnd-gles%{?_isa} >= 1.0
Requires:       libglvnd-glx%{?_isa} >= 1.0
Requires:       libglvnd-opengl%{?_isa} >= 1.0

%if 0%{?fedora} || 0%{?rhel} >= 9
Requires:       egl-gbm%{?_isa} >= 1.1.1
Requires:       egl-wayland%{?_isa} >= 1.1.13
%elif 0%{?rhel} == 8
Requires:       egl-wayland%{?_isa} >= 1.1.13
%else
Requires:       egl-wayland%{?_isa} >= 1.1.7
%endif

%if 0%{?fedora} || 0%{?rhel} >= 8
Requires:       vulkan-loader
%else
Requires:       vulkan-filesystem
%endif

Conflicts:      nvidia-x11-drv-libs
Conflicts:      nvidia-x11-drv-470xx-libs
Conflicts:      xorg-x11-drv-nvidia-libs
Conflicts:      xorg-x11-drv-nvidia-470xx-libs

%description libs
This package provides the shared libraries for %{name}.

%package cuda-libs
Summary:        Libraries for %{name}-cuda
Provides:       %{name}-devel%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Obsoletes:      %{name}-devel < %{?epoch:%{epoch}:}%{version}-%{release}

Conflicts:      xorg-x11-drv-nvidia-cuda-libs
Conflicts:      xorg-x11-drv-nvidia-470xx-cuda-libs

%description cuda-libs
This package provides the CUDA libraries for %{name}-cuda.

%package NvFBCOpenGL
Summary:        NVIDIA OpenGL-based Framebuffer Capture libraries
# Loads libnvidia-encode.so at runtime
Requires:       %{name}-cuda-libs%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}

%description NvFBCOpenGL
This library provides a high performance, low latency interface to capture and
optionally encode the composited framebuffer of an X screen. NvFBC are private
APIs that are only available to NVIDIA approved partners for use in remote
graphics scenarios.

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

%ifarch x86_64 aarch64

%package cuda
Summary:        CUDA integration for %{name}
Requires:       %{name}-cuda-libs%{?_isa} = %{?epoch:%{epoch}:}%{version}
Requires:       %{name}-NVML%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Requires:       nvidia-kmod-common = %{?epoch:%{epoch}:}%{version}
Requires:       nvidia-persistenced = %{?epoch:%{epoch}:}%{version}
Requires:       opencl-filesystem
Requires:       ocl-icd

Conflicts:      xorg-x11-drv-nvidia-cuda
Conflicts:      xorg-x11-drv-nvidia-470xx-cuda

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

%ifarch aarch64
%setup -q -T -b 2 -n %{name}-%{version}-aarch64
%endif

%ifarch x86_64
%if 0%{?rhel} == 7 || 0%{?rhel} == 8
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

# Fix file format specification for Vulkan layers
sed -i -e 's/"file_format_version" : "1.0.0"/"file_format_version" : "1.0.1"/g' nvidia_layers.json

%build

%install
# EGL loader
install -p -m 0644 -D 10_nvidia.json %{buildroot}%{_datadir}/glvnd/egl_vendor.d/10_nvidia.json

# Vulkan loader
install -p -m 0644 -D nvidia_icd.json %{buildroot}%{_datadir}/vulkan/icd.d/nvidia_icd.%{_target_cpu}.json
sed -i -e 's|libGLX_nvidia|%{_libdir}/libGLX_nvidia|g' %{buildroot}%{_datadir}/vulkan/icd.d/nvidia_icd.%{_target_cpu}.json

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
install -p -m 0755 nvidia-{debugdump,smi,cuda-mps-control,cuda-mps-server,bug-report.sh,ngx-updater,powerd} %{buildroot}%{_bindir}

# Man pages
mkdir -p %{buildroot}%{_mandir}/man1/
install -p -m 0644 nvidia-{smi,cuda-mps-control}*.gz %{buildroot}%{_mandir}/man1/

# X stuff
install -p -m 0644 -D %{SOURCE10} %{buildroot}%{_sysconfdir}/X11/xorg.conf.d/10-nvidia.conf
install -p -m 0755 -D nvidia_drv.so %{buildroot}%{_libdir}/xorg/modules/drivers/nvidia_drv.so
install -p -m 0755 -D libglxserver_nvidia.so.%{version} %{buildroot}%{_libdir}/xorg/modules/extensions/libglxserver_nvidia.so

# NVIDIA specific configuration files
mkdir -p %{buildroot}%{_datadir}/nvidia/
install -p -m 0644 nvidia-application-profiles-%{version}-key-documentation \
    %{buildroot}%{_datadir}/nvidia/
install -p -m 0644 nvidia-application-profiles-%{version}-rc \
    %{buildroot}%{_datadir}/nvidia/

# OptiX
install -p -m 0644 nvoptix.bin %{buildroot}%{_datadir}/nvidia/

# Systemd units and script for suspending/resuming
install -p -m 0644 -D %{SOURCE9} %{buildroot}%{_systemd_util_dir}/system-preset/70-nvidia.preset
mkdir -p %{buildroot}%{_unitdir}/
install -p -m 0644 systemd/system/*.service %{buildroot}%{_unitdir}/
install -p -m 0755 systemd/nvidia-sleep.sh %{buildroot}%{_bindir}/
install -p -m 0755 -D systemd/system-sleep/nvidia %{buildroot}%{_systemd_util_dir}/system-sleep/nvidia
install -p -m 0644 -D nvidia-dbus.conf %{buildroot}%{_datadir}/dbus-1/system.d/nvidia-dbus.conf

# Ignore powerd binary exiting if hardware is not present
# We should check for information in the DMI table
sed -i -e 's/ExecStart=/ExecStart=-/g' %{buildroot}%{_unitdir}/nvidia-powerd.service

%if 0%{?fedora} || 0%{?rhel} >= 8
# Vulkan layer
install -p -m 0644 -D nvidia_layers.json %{buildroot}%{_datadir}/vulkan/implicit_layer.d/nvidia_layers.json

# install AppData and add modalias provides
install -p -m 0644 -D %{SOURCE40} %{buildroot}%{_metainfodir}/com.nvidia.driver.metainfo.xml
%{SOURCE41} supported-gpus/supported-gpus.json | xargs appstream-util add-provide %{buildroot}%{_metainfodir}/com.nvidia.driver.metainfo.xml modalias
mkdir -p %{buildroot}%{_datadir}/pixmaps/
cp %{SOURCE42} %{buildroot}%{_datadir}/pixmaps/

%check
appstream-util validate --nonet %{buildroot}%{_metainfodir}/com.nvidia.driver.metainfo.xml
%endif

%endif

%ldconfig_scriptlets libs

%ldconfig_scriptlets cuda-libs

%ldconfig_scriptlets NvFBCOpenGL

%ldconfig_scriptlets NVML

%ifarch x86_64 aarch64

%post
%systemd_post nvidia-hibernate.service
%systemd_post nvidia-powerd.service
%systemd_post nvidia-resume.service
%systemd_post nvidia-suspend.service

%preun
%systemd_preun nvidia-hibernate.service
%systemd_preun nvidia-powerd.service
%systemd_preun nvidia-resume.service
%systemd_preun nvidia-suspend.service

%postun
%systemd_postun nvidia-hibernate.service
%systemd_postun nvidia-powerd.service
%systemd_postun nvidia-resume.service
%systemd_postun nvidia-suspend.service

%endif

%ifnarch %{ix86}

%files
%license LICENSE
%doc NVIDIA_Changelog README.txt html supported-gpus/supported-gpus.json
%dir %{_sysconfdir}/nvidia
%config(noreplace) %{_sysconfdir}/X11/xorg.conf.d/10-nvidia.conf
%{_bindir}/nvidia-bug-report.sh
%{_bindir}/nvidia-powerd
%{_bindir}/nvidia-sleep.sh
%if 0%{?fedora} || 0%{?rhel} >= 8
%{_metainfodir}/com.nvidia.driver.metainfo.xml
%endif
%{_datadir}/dbus-1/system.d/nvidia-dbus.conf
%{_datadir}/nvidia/nvidia-application-profiles*
%{_datadir}/pixmaps/%{name}.png
%{_libdir}/xorg/modules/extensions/libglxserver_nvidia.so
%{_libdir}/xorg/modules/drivers/nvidia_drv.so
%{_prefix}/lib/nvidia/alternate-install-present
%{_systemd_util_dir}/system-preset/70-nvidia.preset
%{_systemd_util_dir}/system-sleep/nvidia
%{_unitdir}/nvidia-hibernate.service
%{_unitdir}/nvidia-powerd.service
%{_unitdir}/nvidia-resume.service
%{_unitdir}/nvidia-suspend.service

%files cuda
%{_sysconfdir}/OpenCL/vendors/*
%{_bindir}/nvidia-cuda-mps-control
%{_bindir}/nvidia-cuda-mps-server
%{_bindir}/nvidia-debugdump
%{_bindir}/nvidia-ngx-updater
%{_bindir}/nvidia-smi
%{_mandir}/man1/nvidia-cuda-mps-control.1.*
%{_mandir}/man1/nvidia-smi.*

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
%{_libdir}/libnvidia-gpucomp.so.%{version}
%{_libdir}/libnvidia-tls.so.%{version}
%{_libdir}/vdpau/libvdpau_nvidia.so.1
%{_libdir}/vdpau/libvdpau_nvidia.so.%{version}
%ifarch x86_64 aarch64
%if 0%{?fedora} || 0%{?rhel} >= 8
%{_datadir}/vulkan/implicit_layer.d/nvidia_layers.json
%endif
%{_libdir}/libnvidia-api.so.1
%{_libdir}/libnvidia-cfg.so.1
%{_libdir}/libnvidia-cfg.so.%{version}
%{_libdir}/libnvidia-ngx.so.1
%{_libdir}/libnvidia-ngx.so.%{version}
%{_libdir}/libnvidia-rtcore.so.%{version}
%{_libdir}/libnvoptix.so.1
%{_libdir}/libnvoptix.so.%{version}
%{_datadir}/nvidia/nvoptix.bin
%endif
%ifarch x86_64
%dir %{_libdir}/nvidia
%dir %{_libdir}/nvidia/wine
%{_libdir}/nvidia/wine/*.dll
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
%endif
%ifarch x86_64
%if 0%{?rhel} ==7 || 0%{?rhel} == 8
%{_libdir}/libnvidia-pkcs11.so.%{version}
%else
%{_libdir}/libnvidia-pkcs11-openssl3.so.%{version}
%endif
%endif

%files NvFBCOpenGL
%{_libdir}/libnvidia-fbc.so.1
%{_libdir}/libnvidia-fbc.so.%{version}

%files NVML
%{_libdir}/libnvidia-ml.so.1
%{_libdir}/libnvidia-ml.so.%{version}

%changelog
* Tue Jul 02 2024 Simone Caronni <negativo17@gmail.com> - 3:555.58.02-1
- Update to 555.58.02.

* Sat Jun 29 2024 Simone Caronni <negativo17@gmail.com> - 3:555.58-4
- Adjust Appstream icon path.

* Fri Jun 28 2024 Simone Caronni <negativo17@gmail.com> - 3:555.58-3
- Switch to local icon for Appstream metadata before madness takes over.

* Fri Jun 28 2024 Simone Caronni <negativo17@gmail.com> - 3:555.58-2
- Make sure there are no redirects in the Appstream metadata URLs.

* Thu Jun 27 2024 Simone Caronni <negativo17@gmail.com> - 3:555.58-1
- Update to 555.58.

* Wed Jun 26 2024 Simone Caronni <negativo17@gmail.com> - 3:550.90.07-2
- Update AppData metadata, add new custom key entry:
  https://gitlab.gnome.org/GNOME/gnome-software/-/merge_requests/2034

* Wed Jun 05 2024 Simone Caronni <negativo17@gmail.com> - 3:550.90.07-1
- Update to 550.90.07.

* Fri May 31 2024 Simone Caronni <negativo17@gmail.com> - 3:550.78-3
- Fix file format specification for Vulkan layers.

* Mon May 27 2024 Simone Caronni <negativo17@gmail.com> - 3:550.78-2
- Add GBM loader library symlink also for i686 libraries (#156).
- Also own the %%_libdir/gbm directory.

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

* Mon Dec 18 2023 Simone Caronni <negativo17@gmail.com> - 3:545.29.06-2
- Do not mark nvidia-powerd unit as failed if the binary exits.

* Fri Dec 01 2023 Simone Caronni <negativo17@gmail.com> - 3:545.29.06-1
- Update to 545.29.06.

* Mon Nov 13 2023 Simone Caronni <negativo17@gmail.com> - 3:545.29.02-2
- Create kernel module tarball with proprietary and open source modules.

* Tue Oct 31 2023 Simone Caronni <negativo17@gmail.com> - 3:545.29.02-1
- Update to 545.29.02.

* Wed Oct 18 2023 Simone Caronni <negativo17@gmail.com> - 3:545.23.06-1
- Update to 545.23.06.

* Fri Sep 22 2023 Simone Caronni <negativo17@gmail.com> - 3:535.113.01-1
- Update to 535.113.01.

* Thu Aug 24 2023 Simone Caronni <negativo17@gmail.com> - 3:535.104.05-1
- Update to 535.104.05.

* Wed Aug 09 2023 Simone Caronni <negativo17@gmail.com> - 3:535.98-1
- Update to 535.98.

* Wed Jul 19 2023 Simone Caronni <negativo17@gmail.com> - 3:535.86.05-1
- Update to 535.86.05.

* Thu Jun 15 2023 Simone Caronni <negativo17@gmail.com> - 3:535.54.03-1
- Update to 535.54.03.

* Fri May 12 2023 Simone Caronni <negativo17@gmail.com> - 3:525.116.04-1
- Update to 525.116.04.

* Mon May 01 2023 Simone Caronni <negativo17@gmail.com> - 3:525.116.03-1
- Update to 525.116.03.

* Fri Feb 10 2023 Simone Caronni <negativo17@gmail.com> - 3:525.89.02-1
- Update to 525.89.02.

* Fri Jan 20 2023 Simone Caronni <negativo17@gmail.com> - 3:525.85.05-1
- Update to 525.85.05.

* Mon Jan 09 2023 Simone Caronni <negativo17@gmail.com> - 3:525.78.01-1
- Update to 525.78.01.

* Tue Dec 13 2022 Simone Caronni <negativo17@gmail.com> - 3:525.60.11-2
- Drop nvidia-driver-devel subpackage.
- Trim changelog.

* Tue Nov 29 2022 Simone Caronni <negativo17@gmail.com> - 3:525.60.11-1
- Update to 525.60.11.

* Thu Oct 13 2022 Simone Caronni <negativo17@gmail.com> - 3:520.56.06-1
- Update to 520.56.06.

* Wed Sep 21 2022 Simone Caronni <negativo17@gmail.com> - 3:515.76-1
- Update to 515.76.

* Mon Aug 08 2022 Simone Caronni <negativo17@gmail.com> - 3:515.65.01-1
- Update to 515.65.01.

* Wed Jun 29 2022 Simone Caronni <negativo17@gmail.com> - 3:515.57-1
- Update to 515.57.

* Wed Jun 01 2022 Simone Caronni <negativo17@gmail.com> - 3:515.48.07-1
- Update to 515.48.07.
- Rename libnvidia-vulkan-producer.so versioned library (#128).

* Tue May 31 2022 Simone Caronni <negativo17@gmail.com> - 3:510.73.05-1
- Update to 510.73.05.

* Mon May 02 2022 Simone Caronni <negativo17@gmail.com> - 3:510.68.02-1
- Update to 510.68.02.

* Mon Mar 28 2022 Simone Caronni <negativo17@gmail.com> - 3:510.60.02-1
- Update to 510.60.02.

* Thu Mar 03 2022 Simone Caronni <negativo17@gmail.com> - 3:510.54-3
- nvidia-resume is no longer triggered by nvidia-sleep.sh.

* Fri Feb 25 2022 Simone Caronni <negativo17@gmail.com> - 3:510.54-2
- nvidia-smi dlopens NVML, add explicit dependency to cuda subpackage.

* Mon Feb 14 2022 Simone Caronni <negativo17@gmail.com> - 3:510.54-1
- Update to 510.54.

* Sat Feb 12 2022 Simone Caronni <negativo17@gmail.com> - 3:510.47.03-4
- Drop libva-vdpau-driver hard dependency.

* Mon Feb 07 2022 Simone Caronni <negativo17@gmail.com> - 3:510.47.03-3
- Fix GBM condition.

* Sat Feb 05 2022 Simone Caronni <negativo17@gmail.com> - 3:510.47.03-2
- Drop explicit dependency on egl-wayland, it's auto generated and not needed on
  i686 libs. Minimum version 1.1.7 required.

* Wed Feb 02 2022 Simone Caronni <negativo17@gmail.com> - 3:510.47.03-1
- Update to 510.47.03.
- Use external GBM library.
- Install GBM only on CentOS/RHEL 9+ and Fedora 35. It's also supported in
  CentOS Stream 8 (8.6+/Mesa 21.2), but there's no easy way to check for Stream
  in the SPEC file.
