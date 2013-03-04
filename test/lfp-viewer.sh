#!/bin/bash
set -e
cd `dirname $0`

SCRIPT_DIR=".."
SAMPLE_DIR="../samples"
SCRIPT_CMD="lfp-viewer.py"
: ${PYTHON_CMD:="/usr/bin/env python"}


function _test {
	params=$@
	echo
	echo "################################"
	echo "# $SCRIPT_CMD"
	echo
	$PYTHON_CMD $SCRIPT_DIR/$SCRIPT_CMD -d $params
	echo
}


_test \
	$SAMPLE_DIR/IMG_0001-stk.lfp	\
	$SAMPLE_DIR/IMG_0002-stk.lfp

