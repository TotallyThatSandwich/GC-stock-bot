{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.python3
    pkgs.python3Packages.virtualenv
  ];

  shellHook = ''
    if [ ! -d venv ]; then
      echo "[nix] Creating virtualenv in ./venv"
      virtualenv venv
    fi

    source ./venv/bin/activate

    if [ -f requirements.txt ]; then
      echo "[nix] Installing packages from requirements.txt"
      pip install --upgrade pip
      pip install -r requirements.txt
    else
      echo "[nix] No requirements.txt found"
    fi
  '';
}

