#!/bin/bash
set -e
cd `dirname $0`

SCRIPT_DIR=".."
SAMPLE_DIR="../samples"
LFP_READER_DIR="../lfp_reader"

echo
echo "################################"
echo "# lfp_file_exporter.py"
echo
$SCRIPT_DIR/lfp_file_exporter.py $SAMPLE_DIR/IMG_0002-stk.lfp

echo
echo "################################"
echo "# gst_h264_splitter.py"
echo
$LFP_READER_DIR/gst_h264_splitter.py $SAMPLE_DIR/IMG_0002-stk__d300027c386a49a97bdd9ea10c7702ff1d369ba7.data
echo
$LFP_READER_DIR/gst_h264_splitter.py $SAMPLE_DIR/IMG_0002-stk__3162eacac8d6ee78951f0077ac3366c6bad08543.data

