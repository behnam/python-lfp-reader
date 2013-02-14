#!/bin/bash
set -e
cd `dirname $0`

SCRIPT_DIR=".."
SAMPLE_DIR="../samples"
LIB_DIR="../lfp_reader"
: ${PYTHON_CMD:="/usr/bin/env python"}


echo
echo "################################"
echo "# lfp-file.py export"
echo
$PYTHON_CMD $SCRIPT_DIR/lfp-file.py export $SAMPLE_DIR/IMG_0002-stk.lfp


echo
echo "################################"
echo "# gst_h264_splitter.py"
echo
$PYTHON_CMD $LIB_DIR/gst_h264_splitter.py $SAMPLE_DIR/IMG_0002-stk__d300027c386a49a97bdd9ea10c7702ff1d369ba7.data
echo
$PYTHON_CMD $LIB_DIR/gst_h264_splitter.py $SAMPLE_DIR/IMG_0002-stk__3162eacac8d6ee78951f0077ac3366c6bad08543.data

