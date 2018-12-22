with import <nixpkgs> {};
let secret = import ./secret.nix;
in stdenv.mkDerivation {
  name = "menstruation";

  buildInputs = [
    python36Packages.pip
    python36Full
    python36Packages.virtualenv
    libffi
    openssl
    (pkgs.writeShellScriptBin "telegram-test" ''
      MENSTRUATION_DIR=/tmp MENSTRUATION_ENDPOINT=${secret.endpoint} MENSTRUATION_TOKEN=${secret.token} python3 bot.py
    '')
  ];

  shellHook = ''
    SOURCE_DATE_EPOCH=$(date +%s)
    virtualenv --no-setuptools venv
    export PATH=$PWD/venv/bin:$PATH
    pip install -r requirements.txt
  '';
}
