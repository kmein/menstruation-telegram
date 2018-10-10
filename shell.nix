{ pkgs ? import <nixpkgs> {} }:
let python = import ./requirements.nix { inherit pkgs; };
in pkgs.stdenv.mkDerivation {
  name = "menstruation";
  buildInputs = with pkgs; [
    jq
    python36Packages.termcolor
    python.packages."gdom"
  ];
}
