{ pkgs ? import <nixpkgs> {} }:
pkgs.stdenv.mkDerivation {
  name = "menstruation";
  buildInputs = with pkgs; [
    libxml2 libxslt # for gdom
    automake autoconf libtool # for jq
  ];
  shellHook = ''
    set -f
    test -e venv || python3 -m venv venv
    source venv/bin/activate
    pip3 install -r requirements.txt
  '';
}
