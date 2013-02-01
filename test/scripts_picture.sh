#!/bin/bash
set -e
cd `dirname $0`

SCRIPT_DIR=".."
SAMPLE_DIR="../samples"

function _test {
	cmd=lfp_picture_$1.py
	shift 1
	params=$@
	echo
	echo "################################"
	echo "# $cmd"
	echo
	$SCRIPT_DIR/$cmd $params
}

_test 'info' \
	$SAMPLE_DIR/IMG_0001.lfp	\
	$SAMPLE_DIR/IMG_0001-stk.lfp	\
	$SAMPLE_DIR/IMG_0002.lfp	\
	$SAMPLE_DIR/IMG_0002-stk.lfp	\
	$SAMPLE_DIR/IMG_0002-dm.lfp

_test 'exporter' \
	$SAMPLE_DIR/IMG_0001.lfp	\
	$SAMPLE_DIR/IMG_0001-stk.lfp	\
	$SAMPLE_DIR/IMG_0002.lfp	\
	$SAMPLE_DIR/IMG_0002-stk.lfp	\
	$SAMPLE_DIR/IMG_0002-dm.lfp

_test 'all_focused' \
	$SAMPLE_DIR/IMG_0001-stk.lfp	\
	$SAMPLE_DIR/IMG_0002-stk.lfp

_test 'viewer' \
	$SAMPLE_DIR/IMG_0001-stk.lfp	\
	$SAMPLE_DIR/IMG_0002-stk.lfp

