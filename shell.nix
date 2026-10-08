{
  pkgs ? import <nixpkgs> { },
}:
with pkgs;
mkShell {
  packages = [
    dbeaver-bin
    mqtt-explorer
    openvpn
    python314
    uv
  ];
}
