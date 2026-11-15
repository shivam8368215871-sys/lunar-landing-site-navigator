#!/usr/bin/env bash

set -euo pipefail

KERNEL_DIR="data/kernels"

mkdir -p "$KERNEL_DIR"

echo "============================================================"
echo "SPICE KERNEL SETUP"
echo "============================================================"

download_kernel() {
    local url="$1"
    local filename="$2"
    local destination="$KERNEL_DIR/$filename"

    if [ -s "$destination" ]; then
        echo "PASS: $filename already exists"
        return
    fi

    echo
    echo "Downloading: $filename"

    wget \
        "$url" \
        -O "$destination"
}

download_kernel \
    "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de440s.bsp" \
    "de440s.bsp"

download_kernel \
    "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/moon_pa_de440_200625.bpc" \
    "moon_pa_de440_200625.bpc"

download_kernel \
    "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/lsk/naif0012.tls" \
    "naif0012.tls"

download_kernel \
    "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/pck00011.tpc" \
    "pck00011.tpc"

echo
echo "============================================================"
echo "VERIFYING REQUIRED KERNELS"
echo "============================================================"

for kernel in \
    de440s.bsp \
    moon_pa_de440_200625.bpc \
    naif0012.tls \
    pck00011.tpc
do
    if [ -s "$KERNEL_DIR/$kernel" ]; then
        echo "PASS: $kernel"
    else
        echo "FAIL: $kernel"
        exit 1
    fi
done

echo
echo "============================================================"
echo "SPICE KERNEL SET READY"
echo "============================================================"
