{
  description = "The Flask Mega-Tutorial";
  inputs = {
    nixpkgs.url = github:NixOS/nixpkgs/nixos-25.11;
    flake-utils.url = github:numtide/flake-utils;
  };
  outputs = { self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem(
      system: 
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python-env = pkgs.python3.withPackages(p: [p.flask]);
        flaskApp = "microblog.py"; 
      in {
        packages.default = pkgs.stdenv.mkDerivation {
          pname = "flask-mega-tutorial";
          version = "0.0.1";
          src = ./.;
          buildInputs = [ python-env ];
          installPhase = ''
            mkdir -p $out/bin
            cp -R app $out/app
            cp ${flaskApp} $out/${flaskApp}
            cat > $out/bin/run-app << EOF
            #!${pkgs.stdenv.shell}
            export FLASK_APP=$out/${flaskApp}
            ${python-env}/bin/python $out/${flaskApp}
            EOF
            chmod +x $out/bin/run-app
          '';
        };
        devShells.default = pkgs.mkShell {
          packages = [ python-env ];
        };
      }
    );
}
