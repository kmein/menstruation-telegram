{ pkgs ? import <nixpkgs> {} }:
let python = import ./requirements.nix { inherit pkgs; };
in pkgs.stdenv.mkDerivation {
  name = "menstruation";
  buildInputs = with pkgs; [
    automake autoconf libtool # for jq
    libxml2 libxslt # for gdom
  ];
  shellHook = ''
    set -f
    test -e venv || python -m venv venv
    source venv/bin/activate
    pip install gdom jq termcolor
  '';
}
