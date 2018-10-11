{ pkgs ? import <nixpkgs> {} }:
let python = import ./requirements.nix { inherit pkgs; };
in pkgs.stdenv.mkDerivation {
  name = "menstruation";
  buildInputs = with pkgs; [
    jq
    python36Packages.termcolor
    python.packages."gdom"
    autoconf automake libtool # for jq
  ];
  shellHook = ''
    set -f
    test -e venv || python -m venv venv
    source venv/bin/activate
    pip install jq
  '';
}
