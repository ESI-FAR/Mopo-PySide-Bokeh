{
  description = "Bokeh viz in PySide6";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = nixpkgs.legacyPackages.${system};
      py = pkgs.python311;
      py-deps = ps: with ps; [
        bokeh
        pyside6
      ];
      deps = with pkgs; [
        #bash

        (py.withPackages py-deps)
      ];
    in {
      devShells.default = pkgs.mkShell rec {
        packages = deps;
      };
    });
}
