{ pkgs }: {
  deps = [
    pkgs.google-chrome-stable
    pkgs.xvfb_run
    pkgs.xorg.libxshmfence
  ];
}
