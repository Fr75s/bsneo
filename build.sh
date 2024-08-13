#!/bin/bash

export SERIOUS_PYTHON_P4A_DIST=$HOME/.local/share/python-for-android/dists/bsneopkgs
echo $SERIOUS_PYTHON_P4A_DIST

splash_light="#f2f6ff"
splash_dark="#26282d"

build_no=1
version="1.0.0"

flet build $1 --verbose --splash-color $splash_light --splash-dark-color $splash_dark --build-number $build_no --build-version $version --include-packages flet_permission_handler
