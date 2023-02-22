{
  description = "Menstruation telegram frontend";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/695b3515251873e0a7e2021add4bba643c56cde3";
    flake-utils.url = "github:numtide/flake-utils";
    menstruation-backend.url = "github:kmein/menstruation.rs";
  };

  outputs = inputs: with inputs;
  flake-utils.lib.eachDefaultSystem (system: let
    pkgs = import nixpkgs {inherit system;};
    menstruation = inputs.menstruation-backend.defaultPackage.${system};
  in {
    devShell = pkgs.mkShell rec {
      buildInputs = [
        menstruation
        (pkgs.writers.writeDashBin "run" ''
          ( ${pkgs.redis}/bin/redis-server &
            ${menstruation}/bin/menstruation_server
          ) &
          ${pkgs.python3Packages.poetry}/bin/poetry run menstruation-telegram
        '')
      ];
      MENSTRUATION_DEBUG = 1;
      ROCKET_PORT = 8000;
      MENSTRUATION_ENDPOINT = "http://localhost:${toString ROCKET_PORT}";
    };
    defaultPackage = self.packages.${system}.menstruation-telegram;
    packages.menstruation-telegram = pkgs.poetry2nix.mkPoetryApplication {
      projectDir = ./.;
    };
  });
}
