with import <nixpkgs> {};
let secret = import ./secret.nix;
in stdenv.mkDerivation rec {
  name = "menstruation";

  buildInputs = [
    python36Packages.virtualenvwrapper
    libffi
    openssl
    (pkgs.writeShellScriptBin "telegram-test" ''
      MENSTRUATION_DEBUG=1 MENSTRUATION_ENDPOINT=${secret.endpoint} MENSTRUATION_TOKEN=${secret.token} python3 menstruation/bot.py
    '')
  ];

  shellHook = ''
    SOURCE_DATE_EPOCH=$(date +%s)
    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt

    ${pkgs.redis}/bin/redis-server >/dev/null &
  '';
}
