%global debug_package %{nil}
%global __strip /bin/true

%if 0%{?rhel} == 6
# RHEL 6 does not have _udevrulesdir defined
%global _udevrulesdir   %{_prefix}/lib/udev/rules.d/
%global _dracutopts     nouveau.modeset=0 rdblacklist=nouveau nomodeset vga=normal
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
%global _dracutopts     nouveau.modeset=0 rd.driver.blacklist=nouveau nomodeset gfxpayload=vga=normal
%global _modprobe_d     %{_prefix}/lib/modprobe.d/
%global _grubby         %{_sbindir}/grubby --update-kernel=ALL

# Prevent nvidia-driver-libs being pulled in place of mesa. This is for all
# libraries in the "nvidia" subdirectory.
%global __provides_exclude_from %{_libdir}/nvidia
%global __requires_exclude_from %{_libdir}/nvidia
%endif

Name:           nvidia-driver
Version:        352.79
Release:        1%{?dist}
Summary:        NVIDIA's proprietary display driver for NVIDIA graphic cards
Epoch:          2
License:        NVIDIA License
URL:            http://www.nvidia.com/object/unix.html
ExclusiveArch:  %{ix86} x86_64 armv7hl

Source0:        %{name}-%{version}-i386.tar.xz
Source1:        %{name}-%{version}-x86_64.tar.xz
Source2:        %{name}-%{version}-armv7hl.tar.xz
Source10:       99-nvidia-modules.conf
# X.org "OutputClass" only on server 1.16+
Source11:       10-nvidia-driver.conf
Source12:       99-nvidia-ignoreabi.conf
Source13:       xorg.conf.nvidia
Source20:       blacklist-nouveau.conf
Source21:       alternate-install-present
Source22:       60-nvidia-uvm.rules
Source23:       nvidia-uvm.conf
Source99:       nvidia-generate-tarballs.sh

# For execstack removal
%if 0%{?fedora} >= 23 || 0%{?rhel} > 7
BuildRequires:  execstack
%else
BuildRequires:  prelink
%endif

# UDev rule location (_udevrulesdir)
%if 0%{?fedora} || 0%{?rhel} >= 7
BuildRequires:  systemd
%endif

Requires:       grubby
Requires:       nvidia-driver-libs%{?_isa} = %{?epoch}:%{version}
Requires:       nvidia-kmod = %{?epoch}:%{version}
Provides:       nvidia-kmod-common = %{?epoch}:%{version}
Requires:       nvidia-settings%{?_isa} = %{?epoch}:%{version}
Requires:       libva-vdpau-driver%{?_isa}
Requires:       xorg-x11-server-Xorg%{?_isa}

Conflicts:      nvidia-x11-drv-beta
Conflicts:      nvidia-x11-drv-71xx
Conflicts:      nvidia-x11-drv-96xx
Conflicts:      nvidia-x11-drv-173xx
Conflicts:      nvidia-x11-drv-304xx
Conflicts:      xorg-x11-drv-nvidia-beta
Conflicts:      xorg-x11-drv-nvidia-71xx
Conflicts:      xorg-x11-drv-nvidia-96xx
Conflicts:      xorg-x11-drv-nvidia-173xx
Conflicts:      xorg-x11-drv-nvidia-304xx
Conflicts:      fglrx-x11-drv
Conflicts:      catalyst-x11-drv
Conflicts:      catalyst-x11-drv-legacy

Obsoletes:      xorg-x11-drv-nvidia < %{?epoch}:%{version}-%{release}
Provides:       xorg-x11-drv-nvidia = %{?epoch}:%{version}-%{release}
Obsoletes:      nvidia-x11-drv < %{?epoch}:%{version}-%{release}
Provides:       nvidia-x11-drv = %{?epoch}:%{version}-%{release}

%description
This package provides the most recent NVIDIA display driver which allows for
hardware accelerated rendering with NVIDIA chipsets GeForce8 series and newer.
GeForce5 and below are NOT supported by this release.

For the full product support list, please consult the release notes for driver
version %{version}.

%package libs
Summary:        Libraries for %{name}
Requires(post): ldconfig
Requires:       %{name} = %{?epoch}:%{version}-%{release}
Requires:       libvdpau%{?_isa} >= 0.5

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

%description NVML
A C-based API for monitoring and managing various states of the NVIDIA GPU
devices. It provides a direct access to the queries and commands exposed via
nvidia-smi. The run-time version of NVML ships with the NVIDIA display driver,
and the SDK provides the appropriate header, stub libraries and sample
applications. Each new version of NVML is backwards compatible and is intended
to be a platform for building 3rd party applications.

%package devel
Summary:        Development files for %{name}
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

%ifarch armv7hl
%setup -q -T -b 2 -n %{name}-%{version}-armv7hl
%endif

# Print and remove execstack from binaries
execstack -q nvidia-cuda-mps-control nvidia-cuda-mps-server lib*.so.*
execstack -c nvidia-cuda-mps-control nvidia-cuda-mps-server lib*.so.*

# Create symlinks for shared objects
ldconfig -vn .

%build

%install
# Create empty tree
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/nvidia/
mkdir -p %{buildroot}%{_datadir}/X11/xorg.conf.d/
mkdir -p %{buildroot}%{_includedir}/nvidia/GL/
mkdir -p %{buildroot}%{_libdir}/nvidia/xorg/
mkdir -p %{buildroot}%{_libdir}/vdpau/
mkdir -p %{buildroot}%{_libdir}/xorg/modules/drivers/
mkdir -p %{buildroot}%{_mandir}/man1/
mkdir -p %{buildroot}%{_prefix}/lib/modules-load.d/
mkdir -p %{buildroot}%{_sysconfdir}/X11/xorg.conf.d/
mkdir -p %{buildroot}%{_sysconfdir}/ld.so.conf.d/
mkdir -p %{buildroot}%{_sysconfdir}/nvidia/
mkdir -p %{buildroot}%{_udevrulesdir}
mkdir -p %{buildroot}%{_modprobe_d}/
%ifarch %{ix86} x86_64
mkdir -p %{buildroot}%{_sysconfdir}/OpenCL/vendors/
%endif

# Install headers
install -p -m 0644 *.h %{buildroot}%{_includedir}/nvidia/GL/

%ifarch %{ix86} x86_64
# OpenCL config
install -p -m 0755 nvidia.icd %{buildroot}%{_sysconfdir}/OpenCL/vendors/
%endif

# Library search path
echo "%{_libdir}/nvidia" > %{buildroot}%{_sysconfdir}/ld.so.conf.d/nvidia-%{_lib}.conf

# Blacklist nouveau
install -p -m 0644 %{SOURCE20} %{buildroot}%{_modprobe_d}/

# Autoload nvidia-uvm module
install -p -m 0644 %{SOURCE23} %{buildroot}%{_prefix}/lib/modules-load.d/

# Install binaries
install -p -m 0755 nvidia-{debugdump,smi,cuda-mps-control,cuda-mps-server,bug-report.sh} %{buildroot}%{_bindir}

# Install man pages
install -p -m 0644 nvidia-{smi,cuda-mps-control}*.gz %{buildroot}%{_mandir}/man1/

# X configuration
install -p -m 0644 %{SOURCE10} %{buildroot}%{_sysconfdir}/X11/xorg.conf.d/99-nvidia-modules.conf
sed -i -e 's|@LIBDIR@|%{_libdir}|g' %{buildroot}%{_sysconfdir}/X11/xorg.conf.d/99-nvidia-modules.conf

%if 0%{?rhel}
install -p -m 0644 %{SOURCE13} %{buildroot}%{_sysconfdir}/X11/xorg.conf.nvidia
%endif

%if 0%{?fedora} || 0%{?rhel} > 7
install -p -m 0644 %{SOURCE11} %{buildroot}%{_datadir}/X11/xorg.conf.d/10-nvidia-driver.conf
%endif

%if 0%{?fedora} > 23 || 0%{?rhel} > 7
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

# Install text files for alternate installation
install -p -m 644 %{SOURCE21} %{buildroot}%{_libdir}/nvidia/alternate-install-present

# UDev rules for nvidia-uvm
install -p -m 644 %{SOURCE22} %{buildroot}%{_udevrulesdir}

# Install system conflicting libraries
cp -a \
    libGL.so* \
    libGLESv1_CM.so* \
    libGLESv2.so* \
    libEGL.so* \
%ifarch %{ix86} x86_64
    libOpenCL.so* \
%endif
    %{buildroot}%{_libdir}/nvidia/

# Install unique libraries
cp -a libcuda.so* libnv*.so* \
    %{buildroot}%{_libdir}/
ln -sf libcuda.so.%{version} %{buildroot}%{_libdir}/libcuda.so

# VDPAU libraries
cp -a libvdpau_nvidia.so* %{buildroot}%{_libdir}/vdpau/


%post
if [ "$1" -eq "1" ]; then
  %{_grubby} --args='%{_dracutopts}' &>/dev/null
%if 0%{?fedora} || 0%{?rhel} >= 7
  sed -i -e 's/GRUB_CMDLINE_LINUX="/GRUB_CMDLINE_LINUX="%{_dracutopts} /g' /etc/default/grub
%endif
fi || :

%post libs -p /sbin/ldconfig

%post cuda-libs -p /sbin/ldconfig

%post NvFBCOpenGL -p /sbin/ldconfig

%post NVML -p /sbin/ldconfig

%if 0%{?rhel}
%posttrans
[ -f %{_sysconfdir}/X11/xorg.conf ] || cp -p %{_sysconfdir}/X11/xorg.conf.nvidia %{_sysconfdir}/X11/xorg.conf || :
%endif

%preun
if [ "$1" -eq "0" ]; then
  %{_grubby} --remove-args='%{_dracutopts}' &>/dev/null
%if 0%{?fedora} || 0%{?rhel} >= 7
  sed -i -e 's/%{_dracutopts} //g' /etc/default/grub
%endif
%if 0%{?rhel}
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
%{_datadir}/nvidia
%{_libdir}/nvidia/alternate-install-present
%{_libdir}/nvidia/xorg
%{_libdir}/xorg/modules/drivers/nvidia_drv.so
%{_modprobe_d}/blacklist-nouveau.conf
# X.org configuration files
%config(noreplace) %{_sysconfdir}/X11/xorg.conf.d/99-nvidia-modules.conf

%if 0%{?rhel}
%config(noreplace) %{_sysconfdir}/X11/xorg.conf.nvidia
%endif

%if 0%{?fedora} || 0%{?rhel} > 7
%{_datadir}/X11/xorg.conf.d/10-nvidia-driver.conf
%endif

%if 0%{?fedora} > 23 || 0%{?rhel} > 7
%config(noreplace) %{_sysconfdir}/X11/xorg.conf.d/99-nvidia-ignoreabi.conf
%endif

%files cuda
%ifarch %{ix86} x86_64
%{_sysconfdir}/OpenCL/vendors/*
%endif
%{_bindir}/nvidia-cuda-mps-control
%{_bindir}/nvidia-cuda-mps-server
%{_bindir}/nvidia-debugdump
%{_bindir}/nvidia-smi
%{_mandir}/man1/nvidia-cuda-mps-control.1.*
%{_mandir}/man1/nvidia-smi.*
%{_udevrulesdir}/60-nvidia-uvm.rules
%{_prefix}/lib/modules-load.d/nvidia-uvm.conf

%files libs
%dir %{_libdir}/nvidia
%{_libdir}/nvidia/libEGL.so.1
%{_libdir}/nvidia/libEGL.so.%{version}
%{_libdir}/nvidia/libGL.so.1
%{_libdir}/nvidia/libGL.so.%{version}
%{_libdir}/nvidia/libGLESv1_CM.so.1
%{_libdir}/nvidia/libGLESv1_CM.so.%{version}
%{_libdir}/nvidia/libGLESv2.so.2
%{_libdir}/nvidia/libGLESv2.so.%{version}
%{_libdir}/libnvidia-cfg.so.1
%{_libdir}/libnvidia-cfg.so.%{version}
%{_libdir}/libnvidia-eglcore.so.%{version}
%{_libdir}/libnvidia-glcore.so.%{version}
%{_libdir}/libnvidia-glsi.so.%{version}
%{_libdir}/libnvidia-tls.so.%{version}
%{_libdir}/vdpau/libvdpau_nvidia.so.1
%{_libdir}/vdpau/libvdpau_nvidia.so.%{version}
%{_sysconfdir}/ld.so.conf.d/nvidia-%{_lib}.conf

%files cuda-libs
%{_libdir}/libcuda.so
%{_libdir}/libcuda.so.1
%{_libdir}/libcuda.so.%{version}
%{_libdir}/libnvcuvid.so.1
%{_libdir}/libnvcuvid.so.%{version}
%{_libdir}/libnvidia-encode.so.1
%{_libdir}/libnvidia-encode.so.%{version}
%{_libdir}/libnvidia-opencl.so.1
%{_libdir}/libnvidia-opencl.so.%{version}
%ifarch %{ix86} x86_64
%{_libdir}/nvidia/libOpenCL.so.1
%{_libdir}/nvidia/libOpenCL.so.1.0.0
%{_libdir}/libnvidia-compiler.so.%{version}
%endif

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

%changelog
* Tue Jan 26 2016 Simone Caronni <negativo17@gmail.com> - 2:352.79-1
- Update to 352.79.

* Wed Nov 18 2015 Simone Caronni <negativo17@gmail.com> - 2:352.63-1
- Update to 352.63.

* Wed Nov 18 2015 Simone Caronni <negativo17@gmail.com> - 2:352.55-2
- Add kernel command line also to Grub default files for grub2-mkconfig
  consumption.
- Create new macro for grubby command in post
- Remove support for Grub 0.97 in Fedora or CentOS/RHEL 7.
- Ignore ABI configuration file moved to Fedora 24+ (driver
  supports video driver ABI 20).
- Update modprobe configuration file position in CentOS/RHEL 6.
- Update isa requirements.

* Tue Oct 20 2015 Simone Caronni <negativo17@gmail.com> - 2:352.55-1
- Update to 352.55.

* Fri Aug 28 2015 Simone Caronni <negativo17@gmail.com> - 2:352.41-1
- Update to 352.41.

* Sat Aug 22 2015 Simone Caronni <negativo17@gmail.com> - 2:352.30-3
- Re-add nvidia-driver-libs requirement mistakenly removed in latest
  reorganization.

* Fri Aug 14 2015 Simone Caronni <negativo17@gmail.com> - 2:352.30-2
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

* Tue Dec 09 2014 Simone Caronni <negativo17@gmail.com> - 2:346.22-1
- Update to 346.22.

* Fri Nov 14 2014 Simone Caronni <negativo17@gmail.com> - 2:346.16-1
- Update to 346.16.

* Mon Sep 22 2014 Simone Caronni <negativo17@gmail.com> - 2:343.22-1
- Update to 343.22.

* Thu Aug 07 2014 Simone Caronni <negativo17@gmail.com> - 2:343.13-1
- Update to 343.13.

* Tue Aug 05 2014 Simone Caronni <negativo17@gmail.com> - 2:340.24-5
- Split xorg.conf.d configuration in multiple files.

* Mon Jul 14 2014 Simone Caronni <negativo17@gmail.com> - 2:340.24-4
- Split out NVML library.

* Mon Jul 14 2014 Simone Caronni <negativo17@gmail.com> - 2:340.24-3
- Rely on built in generator for some requirements.
- Rpmlint fixes.
- Provides nvidia-driver-NVML for GPU Deployment kit.

* Fri Jul 11 2014 Simone Caronni <negativo17@gmail.com> - 2:340.24-2
- Move nvidia-ml/nvidia-debugdump to cuda packages.
- Use new OutputClass to load the driver on X.org server 1.16 (Fedora 21):
  https://plus.google.com/118125769023950376556/posts/YqyEgcpZmJU
- Add udev rule in nvidia-driver-cuda for nvidia-uvm module (Jan P. Springer).
- Move X.org NVIDIA Files section to be loaded latest (overwrite all Files
  section - Jan P. Springer).
- Remove nvidia-modprobe requirement.

* Tue Jul 08 2014 Simone Caronni <negativo17@gmail.com> - 2:340.24-1
- Update to 340.24.

* Fri Jun 13 2014 Simone Caronni <negativo17@gmail.com> - 2:340.17-3
- Add IgnoreABI server flag for Fedora 21.

* Wed Jun 11 2014 Simone Caronni <negativo17@gmail.com> - 2:340.17-2
- Move application profiles configuration in proper place where the driver
  expects defaults.

* Mon Jun 09 2014 Simone Caronni <negativo17@gmail.com> - 2:340.17-1
- Update to 340.17.

* Mon Jun 02 2014 Simone Caronni <negativo17@gmail.com> - 2:337.25-1
- Update to 337.25.

* Thu May 15 2014 Simone Caronni <negativo17@gmail.com> - 2:337.19-2
- Update RPM filters for autogenerated Provides/Requires.

* Tue May 06 2014 Simone Caronni <negativo17@gmail.com> - 2:337.19-1
- Update to 337.19.

* Tue Apr 08 2014 Simone Caronni <negativo17@gmail.com> - 2:337.12-1
- Update to 337.12.

* Tue Mar 04 2014 Simone Caronni <negativo17@gmail.com> - 2:334.21-1
- Update to 334.21.
- Added application profiles to the main package.

* Sat Feb 08 2014 Simone Caronni <negativo17@gmail.com> - 2:334.16-1
- Update to 334.16.
- Add EGL/GLES libraries to x86_64 package.
- Add NvFBCOpenGL libraries to armv7hl.
- Added new nvidia-modprobe dependency.

* Tue Jan 14 2014 Simone Caronni <negativo17@gmail.com> - 2:331.38-1
- Update to 331.38.

* Wed Jan 08 2014 Simone Caronni <negativo17@gmail.com> - 2:331.20-4
- CUDA subpackage requires opencl-filesystem on Fedora & RHEL 7.
- Update filters on libraries so all libGL, libEGL and libGLES libraries are
  excluded.

* Tue Dec 17 2013 Simone Caronni <negativo17@gmail.com> - 2:331.20-3
- Update libGL filters with recent packaging guidelines for Fedora and RHEL 7.

* Wed Nov 13 2013 Simone Caronni <negativo17@gmail.com> - 2:331.20-2
- Disable glamoregl X.org module.

* Thu Nov 07 2013 Simone Caronni <negativo17@gmail.com> - 2:331.20-1
- Update to 331.20.
- Create NvFBCOpenGL subpackage.

* Mon Nov 04 2013 Simone Caronni <negativo17@gmail.com> - 2:331.17-1
- Update to 331.17.
- Added new libraries:
    libnvidia-fbc (i686, armv7hl, x86_64)
    libvdpau_nvidia, libEGL (armv7hl)
    libGLESv* libraries (i686, armv7hl)
- Removed libraries (they will probably be re-added):
    libnvidia-vgxcfg libraries (i686, x86_64)

* Fri Oct 04 2013 Simone Caronni <negativo17@gmail.com> - 2:331.13-1
- Update to 331.13.
- Add new libEGL library to i686.

* Mon Sep 09 2013 Simone Caronni <negativo17@gmail.com> - 2:325.15-1
- Update to 325.15.
- Add new libnvidia-vgxcfg (i686, x86_64).

* Thu Aug 22 2013 Simone Caronni <negativo17@gmail.com> - 2:319.49-2
- Move nvidia-debugdump in main package.
- Remove libvdpau from driver tarball.

* Wed Aug 21 2013 Simone Caronni <negativo17@gmail.com> - 2:319.49-1
- Updated to 319.49.
- Add new libnvidia-ifr where appropriate.

* Tue Aug 06 2013 Simone Caronni <negativo17@gmail.com> - 2:319.32-6
- Fix duplicated binaries in non CUDA packages.
- Removed libnvidia-wfb.
- Deleted unused libnvidia-tls libraries.

* Mon Aug 05 2013 Simone Caronni <negativo17@gmail.com> - 2:319.32-5
- Fedora 17 has gone EOL.

* Thu Jul 25 2013 Simone Caronni <negativo17@gmail.com> - 2:319.32-4
- Remove dependency on nvidia-xconfig.

* Tue Jul 02 2013 Simone Caronni <negativo17@gmail.com> - 2:319.32-2
- Add armv7hl support.

* Fri Jun 28 2013 Simone Caronni <negativo17@gmail.com> - 1:319.32-1
- Update to 319.32.
- Bump Epoch.

* Fri May 24 2013 Simone Caronni <negativo17@gmail.com> - 1:319.23-1
- Update to 319.23.

* Wed May 22 2013 Simone Caronni <negativo17@gmail.com> - 1:319.17-5
- Obsolete also xorg-x11-drv-nvidia-libs.
- Add dracut options depending on distribution.
- Add grubby to requirements.

* Tue May 21 2013 Simone Caronni <negativo17@gmail.com> - 1:319.17-3
- Split CUDA into subpackages.

* Thu May 02 2013 Simone Caronni <negativo17@gmail.com> - 1:319.17-2
- Update to 319.17.
- Switch nvidia-cuda-proxy* to nvidia-cuda-mps*.
- Add dependency on nvidia-persistenced and versioned nvidia tools.

* Tue Apr 30 2013 Simone Caronni <negativo17@gmail.com> - 1:319.12-3
- Remove all filters except libGL.so*.

* Mon Apr 22 2013 Simone Caronni <negativo17@gmail.com> - 1:319.12-2
- Started off from rpmfusion-nonfree packages.
- Updated to 319.12.
- Simplify packaging.
- Add conflict to drivers 304xx.
- Add dependency on libva-vdpau-driver.
- Obsoletes xorg-x11-drv-nvidia.
- Switched to no-compat32 x86_64 archive.
- Switch to generated sources.
