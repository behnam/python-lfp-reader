#!/bin/bash
set -e
cd `dirname $0`

SCRIPT_DIR=".."
SAMPLE_DIR="../samples"

function _test {
	cmd=lfp_storage_$1.py
	shift 1
	params=$@
	echo
	echo "################################"
	echo "# $cmd"
	echo
	$SCRIPT_DIR/$cmd $params
}

_test 'info' \
	$SAMPLE_DIR/data_0001.lfp

_test 'exporter' \
	$SAMPLE_DIR/data_0001.lfp

_test 'get_file' \
	$SAMPLE_DIR/data_0001.lfp "C:\\CALIB\\ACC.TXT"

