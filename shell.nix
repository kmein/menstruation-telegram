with import <nixpkgs> {};
let secret = import ./secret.nix;
in stdenv.mkDerivation rec {
  name = "menstruation";

  buildInputs = [
    python36Packages.virtualenvwrapper
    libffi
    openssl
  ];

  MENSTRUATION_ENDPOINT = secret.endpoint;
  MENSTRUATION_DEBUG = "1";
  MENSTRUATION_TOKEN = secret.token;

  shellHook = ''
    SOURCE_DATE_EPOCH=$(date +%s)
    virtualenv venv
    source venv/bin/activate

    ${pkgs.redis}/bin/redis-server >/dev/null &
  '';
}
