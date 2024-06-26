#!/usr/bin/env zsh

# Get miniconda if you need it
#wget https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh
#bash ./Miniconda3-latest-MacOSX-x86_64.sh -b -p ~/opt/miniconda
VERSIONS=(
    "3.6|numpy~=1.12.0"
    "3.7|numpy~=1.15.1"
    "3.8|numpy~=1.17.0"
    "3.9|numpy~=1.17.0"
    "3.10|numpy~=1.21.0"
    "3.11|numpy~=1.22.0"
    "3.12|numpy~=1.24.0"
)
for thisBuild in "${VERSIONS[@]}"
do
    IFS='|' read -r PYVER NUMPY <<< "$thisBuild"
    ENVNAME=spacepy${PYVER//.}
    ~/opt/miniconda/bin/conda create -y -n ${ENVNAME} python=${PYVER}
    source ~/opt/miniconda/bin/activate ${ENVNAME}
    if [ ${PYVER} = "3.6" ]; then
	conda install -y wheel ${NUMPY} gfortran~=11.2.0
	pip install build
	BUILD=pyproject-build
    elif [ ${PYVER} = "3.9" ]; then
	conda install -y python-build wheel gfortran~=11.2.0 "cython<3"
	SDKROOT=/opt/MacOSX10.9.sdk pip install --no-build-isolation ${NUMPY}
	BUILD=python-build
    elif [ ${PYVER} = "3.12" ]; then
	conda install -y python-build wheel gfortran~=11.2.0 "cython<3"
	SDKROOT=/opt/MacOSX10.9.sdk pip install --no-build-isolation ${NUMPY}
	BUILD=python-build
    else
	conda install -y python-build wheel ${NUMPY} gfortran~=11.2.0
	BUILD=python-build
    fi
    rm -rf build
    PYTHONNOUSERSITE=1 PYTHONPATH= SPACEPY_RELEASE=1 SDKROOT=/opt/MacOSX10.9.sdk ${BUILD} -w -n -x .
    conda deactivate
    # if these vars aren't cleared, next conda env will use them for compilers
    badvars=$(env | sed -n 's/^\(CONDA_BACKUP_[^=]*\)=.*/\1/p')
    unset $(echo $badvars)
    export $(echo $badvars)
    ~/opt/miniconda/bin/conda env remove -y --name ${ENVNAME}
done
#rm -rf ~/opt/miniconda
#rm ./Miniconda3-latest-MacOSX-x86_64.sh
