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
	echo "# lfp_file_$cmd.py"
	echo
	$SCRIPT_DIR/lfp_file_$cmd.py $inputs
}

_test 'info' \
	$SAMPLE_DIR/IMG_0001.lfp	\
	$SAMPLE_DIR/IMG_0001-stk.lfp	\
	$SAMPLE_DIR/IMG_0002.lfp	\
	$SAMPLE_DIR/IMG_0002-stk.lfp	\
	$SAMPLE_DIR/IMG_0002-dm.lfp

_test 'get_chunk' \
	$SAMPLE_DIR/IMG_0001.lfp sha1-992ae2d9f755077e50de7b9b1357e873885b3382

_test 'exporter' \
	$SAMPLE_DIR/IMG_0001.lfp	\
	$SAMPLE_DIR/IMG_0001-stk.lfp	\
	$SAMPLE_DIR/IMG_0002.lfp	\
	$SAMPLE_DIR/IMG_0002-stk.lfp	\
	$SAMPLE_DIR/IMG_0002-dm.lfp

