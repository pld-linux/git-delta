#
# Conditional build:
%bcond_without	system_libgit2		# use system installed libgit2

%define		crates_ver	0.19.0

Summary:	A viewer for git and diff output
Name:		git-delta
Version:	0.20.1
Release:	1
License:	MIT
Group:		Applications
Source0:	https://github.com/dandavison/delta/archive/%{version}/delta-%{version}.tar.gz
# Source0-md5:	9d957dee711f45e532e099d0da044854
Source1:	delta-crates-%{crates_ver}.tar.xz
# Source1-md5:	24871297667c3833082f1bc1d34e993b
URL:		https://github.com/dandavison/delta
BuildRequires:	cargo
%if %{with system_libgit2}
BuildRequires:	libgit2-devel < 1.10.0
BuildRequires:	libgit2-devel >= 1.9.0
%endif
BuildRequires:	oniguruma-devel >= 6.9.8
BuildRequires:	pkgconfig
BuildRequires:	rpmbuild(macros) >= 2.050
BuildRequires:	rust
BuildRequires:	tar >= 1:1.22
BuildRequires:	xz
%{?rust_req}
Requires:	oniguruma >= 6.9.8
Provides:	delta = %{version}-%{release}
Obsoletes:	delta < 0.20.1-2
ExclusiveArch:	%{rust_arches}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Delta aims to make studying diffs both efficient and enjoyable: it
allows you to make extensive changes to the layout and styling of
diffs, as well as allowing you to stay arbitrarily close to the
default git/diff output, changing just the aspects that you want to
change.

Delta's main features are:

- Language syntax highlighting with color themes
- Within-line highlights based on a Levenshtein edit inference
  algorithm
- Style (foreground color, background color, font attributes) can be
  configured independently for more than 20 different sections of the
  diff
- Stylable box/line decorations to draw attention to commit, file and
  hunk header sections.
- Line numbering (`-n`)
- `--diff-highlight` and `--diff-so-fancy` emulation modes
- Code can be copied directly from the diff (`-/+` markers are removed
  by default).
- `n` and `N` keybindings to move between files in large diffs, and
  between diffs in `log -p` views (`--navigate`)

%prep
%setup -q -n delta-%{version} -a1

%{__mv} delta-%{crates_ver}/* .
sed -i -e 's/@@VERSION@@/%{version}/' Cargo.lock

# use our offline registry
export CARGO_HOME="$(pwd)/.cargo"

mkdir -p "$CARGO_HOME"
cat >.cargo/config.toml <<EOF
[source.crates-io]
registry = 'https://github.com/rust-lang/crates.io-index'
replace-with = 'vendored-sources'

[source.vendored-sources]
directory = '$PWD/vendor'
EOF

%build
export CARGO_HOME="$(pwd)/.cargo"
export RUSTONIG_SYSTEM_LIBONIG=true
%{?with_system_libgit2:export LIBGIT2_NO_VENDOR=1}

%cargo_build --frozen

%install
rm -rf $RPM_BUILD_ROOT
export CARGO_HOME="$(pwd)/.cargo"

export RUSTONIG_SYSTEM_LIBONIG=true
%{?with_system_libgit2:export LIBGIT2_NO_VENDOR=1}
%cargo_install --frozen --root $RPM_BUILD_ROOT%{_prefix} --path $PWD

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README.md
%attr(755,root,root) %{_bindir}/delta
