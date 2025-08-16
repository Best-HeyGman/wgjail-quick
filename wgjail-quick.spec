Name:       wgjail-quick
Version:    1.0.0
Release:    1%{?dist}
Summary:    A tool to create a Wireguard jail for split tunneling and killswitch
License:    GPL-3.0-or-later
URL:        https://github.com/Best-HeyGman/wgjail-quick
Source:     https://github.com/Best-HeyGman/wgjail-quick/archive/refs/tags/v%{version}.tar.gz

Requires:   wireguard-tools
Requires:   socat
Requires:   bubblewrap

%description
Wgjail-quick gives you the ability to create a "Wireguard jail", i.e. a network namespace where a program that is running inside that namespace can only see and use the one wireguard connection you have given it. There are two main reasons why you would want to do this:
1. For split tunneling, which means that only some of the programs on your pc shall use the wireguard vpn, while the rest just uses your normal network connection
2. To prevent a program from using your normal internet connection in case the wireguard vpn connection is shut down / crashes (a killswitch).

%global debug_package %{nil}

%prep
%setup -q

%build

%install
mkdir -p %{buildroot}/%{_bindir}
mkdir -p %{buildroot}/%{_mandir}/man8
install -m 0755 wgjail-quick %{buildroot}/%{_bindir}
install -m 0644 man/wgjail-quick.8 %{buildroot}/%{_mandir}/man8

%files
%{_bindir}/wgjail-quick
%{_mandir}/man8/wgjail-quick.8*

%changelog
* Sat Aug 16 2025 Stephan Hegemann <stephanhegemann@pm.me> - 1.0.0
- Now ready for RPM packaging
* Sat Jan 11 2025 Stephan Hegemann <stephanhegemann@pm.me> - 0.1.1
- Initial package
