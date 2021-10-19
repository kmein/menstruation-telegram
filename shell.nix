{ pkgs ? import <nixpkgs> {} }:
let
  menstruation-src = import (builtins.fetchTarball https://github.com/kmein/menstruation.rs/archive/f3c0d9937ad4d5fc92c75c6a6270c288a828bda2.tar.gz);
  menstruation = pkgs.callPackage menstruation-src {};
in
pkgs.mkShell {
  buildInputs = with pkgs; [
    (pkgs.writeDashBin "run" ''
      ( ${pkgs.redis}/bin/redis-server &
        ${menstruation}/bin/menstruation_server
      ) &
      ${pkgs.python3Packages.poetry}/bin/poetry run menstruation-telegram
    '')
  ];

  MENSTRUATION_DEBUG = 1;

  ROCKET_PORT = 8000;
  MENSTRUATION_ENDPOINT = "http://localhost:8000";
}
