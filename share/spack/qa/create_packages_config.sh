#!/bin/bash
mkdir -p ~/.spack/
cat > ~/.spack/packages.yaml <<EOF
packages:
  cmake:
    paths:
      cmake@2.8.12%gcc@4.8.4 arch=linux-ubuntu14-x86_64: /usr
    buildable: False
  openmpi:
    paths:
      openmpi@1.6.5%gcc@4.8.4 arch=linux-ubuntu14-x86_64: /usr
    buildable: False
  all:
    providers:
      mpi: [openmpi]
EOF
