with import <nixpkgs> {};
stdenv.mkDerivation {
  name = "menstruation";

  buildInputs = [
    python36Packages.pip
    python36Full
    python36Packages.virtualenv
  ];

  shellHook = ''
    SOURCE_DATE_EPOCH=$(date +%s)
    virtualenv --no-setuptools venv
    export PATH=$PWD/venv/bin:$PATH
    pip install -r client-cli/requirements.txt -r client-telegram/requirements.txt
  '';
}
