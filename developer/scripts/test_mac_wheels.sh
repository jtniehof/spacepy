#!/usr/bin/env zsh

# Run unit tests on all the wheels, mac version

VERSIONS="3.7 3.8 3.9 3.10 3.11 3.12 3.13"

for PYVER in ${=VERSIONS}
do
    ENVNAME=spacepy${PYVER//.}
    ~/opt/miniconda/bin/conda create -y -n ${ENVNAME} python=${PYVER}
    source ~/opt/miniconda/bin/activate ${ENVNAME}
    # From local directory of wheels
    # This is not a valid version. This isn't how it's supposed to work, but
    # somehow installs latest prerelease while keeping deps stable
    pip install --find-links ../dist/ --only-binary spacepy "spacepy>=0.0.0.dev0"
    # From test pypi
#    pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ --only-binary spacepy "spacepy>=0.0.0.dev0"
    python test_all.py > test_output_${PYVER}.txt 2>&1
    conda deactivate
    ~/opt/miniconda/bin/conda env remove -y --name ${ENVNAME}
done
