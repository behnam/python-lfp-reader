#!/bin/bash
set -e
cd `dirname $0`

SCRIPT_DIR=".."
SAMPLE_DIR="../samples"
SCRIPT_CMD="lfp-file.py"

function _test {
	subcmd=$1
	shift 1
	params=$@
	echo
	echo "################################"
	echo "# $SCRIPT_CMD $subcmd"
	echo
	$SCRIPT_DIR/$SCRIPT_CMD -d $subcmd $params
	echo
}

_test 'info' \
	$SAMPLE_DIR/IMG_0001.lfp	\
	$SAMPLE_DIR/IMG_0001-stk.lfp	\
	$SAMPLE_DIR/IMG_0002.lfp	\
	$SAMPLE_DIR/IMG_0002-stk.lfp	\
	$SAMPLE_DIR/IMG_0002-dm.lfp

_test 'export' \
	$SAMPLE_DIR/IMG_0001.lfp	\
	$SAMPLE_DIR/IMG_0001-stk.lfp	\
	$SAMPLE_DIR/IMG_0002.lfp	\
	$SAMPLE_DIR/IMG_0002-stk.lfp	\
	$SAMPLE_DIR/IMG_0002-dm.lfp

_test 'extract' \
	$SAMPLE_DIR/IMG_0001.lfp sha1-992ae2d9f755077e50de7b9b1357e873885b3382

