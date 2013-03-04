#!/bin/bash
set -e
cd `dirname $0`

SCRIPT_DIR=".."
SAMPLE_DIR="../samples"
SCRIPT_CMD="lfp-storage.py"
: ${PYTHON_CMD:="/usr/bin/env python"}


function _test {
	subcmd=$1
	shift 1
	params=$@
	echo
	echo "################################"
	echo "# $SCRIPT_CMD $subcmd"
	echo
	$PYTHON_CMD $SCRIPT_DIR/$SCRIPT_CMD $subcmd -d $params
	echo
}


_test 'info' \
	$SAMPLE_DIR/data_0001.lfp

_test 'export' \
	$SAMPLE_DIR/data_0001.lfp

_test 'extract' \
	$SAMPLE_DIR/data_0001.lfp "C:\\CALIB\\ACC.TXT"

