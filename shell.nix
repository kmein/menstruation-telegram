with import <nixpkgs> {};
let secret = import ./secret.nix;
in stdenv.mkDerivation rec {
  name = "menstruation";

  buildInputs = [
    libffi
    openssl
    (pkgs.writeShellScriptBin "telegram-test" ''
      MENSTRUATION_DEBUG=1 MENSTRUATION_ENDPOINT=${secret.endpoint} MENSTRUATION_TOKEN=${secret.token} python3 menstruation/bot.py
    '')
  ];

  shellHook = ''
    SOURCE_DATE_EPOCH=$(date +%s)
    ${pkgs.redis}/bin/redis-server >/dev/null &
  '';
}
