#!/bin/bash
set -e
cd `dirname $0`

SCRIPT_DIR=".."
SAMPLE_DIR="../samples"

function _test {
	cmd=$1
	shift 1
	inputs=$@
	echo
	echo "################################"
	echo "# lfp_picture_$cmd.py"
	echo
	$SCRIPT_DIR/lfp_picture_$cmd.py $inputs
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

