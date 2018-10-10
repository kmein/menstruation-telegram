with import <nixpkgs> {};
stdenv.mkDerivation {
  name = "menstruation";
  buildInputs = with pkgs; [
    libxml2 libxslt
  ];
  shellHook = ''
    set -f
    test -e venv || python -m venv venv
    source venv/bin/activate
    pip install gdom
  '';
}
