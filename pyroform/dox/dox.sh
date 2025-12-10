#!/bin/bash
#

BUILD_TOOLING='./utils/dox_build.sh'

for arg in "$@"; do
    case $arg in
        --TPS)
            $BUILD_TOOLING -t='./TPS' -o='./TPS.md' -p='TC' -N='Test Performance Specification' -P -S -F
            shift
            ;;
        --TAR)
            $BUILD_TOOLING -t='./TAR' -o='./TAR.md' -p='TC' -N='Test Archive' -P -S -F
            shift
            ;;
        *)
            echo "Unknown argument: $arg"
            exit 1
            ;;
    esac
done


