#!/bin/sh

$1/verifyta -u $2 $3 | tee $4 >/dev/null 2>&1