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
        flask-moment = pkgs.python3Packages.buildPythonPackage rec {
          pname = "flask-moment";
          version = "v1.0.6";
          pyproject = true;

          src = pkgs.fetchFromGitHub {
            owner = "miguelgrinberg";
            repo = "Flask-Moment";
            tag = version;
            hash = "sha256-sqpU3ki32+7dC4RM06tOF9Cu/vSqvq9qy92pcNedKDg=";
          };

          build-system = [ pkgs.python3Packages.flit-core ];

          meta = {
            description = "Flask extension providing moment-js";
            homepage = "https://github.com/miguelgrinberg/Flask-Moment/tree/v1.0.6";
            changelog = "https://github.com/miguelgrinberg/Flask-Moment/blob/v1.0.6/CHANGES.md";
            license = pkgs.lib.licenses.mit;
          };
        };
        python-env = pkgs.python3.withPackages(p: [ 
          p.flask 
          p.flask-wtf 
          p.flask-sqlalchemy
          p.flask-migrate
          p.flask-login
          p.flask-mail
          p.pyjwt
          p.email-validator
          p.pytest
          p.hypothesis
          flask-moment
        ]);
        flaskApp = "microblog.py";
        topLevelFiles = [ flaskApp "config.py" ];
        databaseUrl = "sqlite:///app.db";
      in rec {
        packages.default = pkgs.stdenv.mkDerivation {
          pname = "flask-mega-tutorial";
          version = "0.0.1";
          src = ./.;
          buildInputs = [ python-env ];
          buildPhase = ''py.test'';
          installPhase = ''
            mkdir -p $out/bin
            cp -R app $out/app
            ${builtins.concatStringsSep "\n" (map (f: "cp ${f} $out/${f}") topLevelFiles)}
            cat > $out/bin/run-app << EOF
            #!${pkgs.stdenv.shell}
            export FLASK_APP=$out/${flaskApp}
            export DATABASE_URL=${databaseUrl}
            ${python-env}/bin/python $out/${flaskApp}
            EOF
            chmod +x $out/bin/run-app
          '';
        };
        devShells.default = pkgs.mkShell {
          packages = [ python-env packages.default ];
          shellHook=''
            export DATABASE_URL=${databaseUrl}
            export FLASK_APP=./${flaskApp}
            export FLASK_DEBUG=1
          '';
        };
      }
    );
}

