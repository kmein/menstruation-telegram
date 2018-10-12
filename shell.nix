with import <nixpkgs> {};
stdenv.mkDerivation {
  name = "menstruation";

  buildInputs = [
    python36Packages.pip
    python36Full
    python36Packages.virtualenv

    libxml2 libxslt # for gdom
    automake autoconf libtool # for jq
  ];

  shellHook = ''
    SOURCE_DATE_EPOCH=$(date +%s)
    virtualenv --no-setuptools venv
    export PATH=$PWD/venv/bin:$PATH
    pip install -r requirements.txt
  '';
}
