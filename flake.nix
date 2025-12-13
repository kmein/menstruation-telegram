{
  description = "Menstruation telegram frontend";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/695b3515251873e0a7e2021add4bba643c56cde3";
    menstruation-backend.url = "github:kmein/menstruation.rs";
  };

  outputs =
    {
      menstruation-backend,
      nixpkgs,
      self,
    }:
    let
      pkgsFor = system: import nixpkgs { inherit system; };
      lib = nixpkgs.lib;
      eachSupportedSystem = lib.genAttrs lib.systems.flakeExposed;
    in
    {
      devShell = eachSupportedSystem (
        system:
        let
          pkgs = pkgsFor system;
        in
        pkgs.mkShell rec {
          buildInputs = [
            menstruation-backend.defaultPackage.${system}
            (pkgs.writers.writeDashBin "run" ''
              ( ${pkgs.redis}/bin/redis-server &
                ${menstruation-backend.defaultPackage.${system}}/bin/menstruation_server
              ) &
              ${pkgs.python3Packages.poetry}/bin/poetry run menstruation-telegram
            '')
          ];
          MENSTRUATION_DEBUG = 1;
          ROCKET_PORT = 8000;
          MENSTRUATION_ENDPOINT = "http://localhost:${toString ROCKET_PORT}";
        }
      );
      defaultPackage = eachSupportedSystem (system: self.packages.${system}.menstruation-telegram);
      packages = eachSupportedSystem (system: {
        menstruation-telegram = (pkgsFor system).poetry2nix.mkPoetryApplication {
          projectDir = ./.;
        };
      });
    };
}
