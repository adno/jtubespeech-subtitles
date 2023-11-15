#!/bin/bash

LANG="$1"
LOG="download_${LANG}.log"
# 120_000 / 96 = 1250
SIZE=1250

seq 0 "$SIZE" 119999 |\
	parallel --gnu --joblog "$LOG" python scripts/download_video.py --start \{\} --size "$SIZE" --subtitles-only ${LANG} sub/${LANG}/${LANG}_sample.csv
