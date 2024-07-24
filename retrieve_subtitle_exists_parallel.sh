#!/bin/bash

# Slice and dice the data from "obtain....sh" - DONE:

# TRY GOOGLE:
# for lang in ja
# do
# 	cat videoid-google/${lang}/${lang}wiki-latest-pages-articles-multistream-index_part*.txt \
# 		| sort -u > videoid-google/${lang}/${lang}.txt
# done
# 

# for lang in en ja ps es fr pt zh it pl de ru cs id ur
# do
# 	cat videoid/${lang}/${lang}wiki-latest-pages-articles-multistream-index_part*.txt \
# 		| sort -u > videoid/${lang}/${lang}.txt
# done
# for lang in en ja ps es # fr pt zh it pl de ru cs id ur
# do
# 	# 4k items can run in reasonable time: 4000 * 3 s = 3h 20min
# 	split -l 4000 -d -a 6 videoid/${lang}/${lang}.txt videoid/${lang}/${lang}_part
# done
# (
# for lang in ja en ps es
# do
# 	for file in videoid/${lang}/${lang}_part*
# 	do
# 		echo "${lang},${file}"
# 	done
# done
# ) > videoid/tasks_jaenpses.csv
# (
# for lang in id ur
# do
# 	for file in videoid/${lang}/${lang}_part*
# 	do
# 		echo "${lang},${file}"
# 	done
# done
# ) > videoid/tasks_idur.csv


# split -l 96 -d -a 6 videoid/tasks_jaenpses.csv videoid/tasks_jaenpses_part
# for lang in fr pt zh it pl de ru cs
# do
# 	(
# 	for file in videoid/${lang}/${lang}_part*
# 	do
# 		echo "${lang},${file}" 
# 	done
# 	) > "videoid/tasks_${lang}.csv"
# 	split -l 96 -d -a 6 "videoid/tasks_${lang}.csv" "videoid/tasks_${lang}_part"
# done
# split -l 96 -d -a 6 videoid/tasks_idur.csv videoid/tasks_idur_part


if [ "$1" = '--lang' ] || [ "$1" = '--language' ]
then
	LANG="$2"
	shift 2
else
	LANG="jaenpses"
fi

TASKNO="$1"
if [ -z "$TASKNO" ]
then
	echo "Need TASKNO as argument." >&2
	exit 1
fi

TASKNO="$(printf '%06d' $TASKNO)"
TASKS="videoid/tasks_${LANG}_part${TASKNO}"
LOG="retrieve_${LANG}_${TASKNO}.log"

if ! [ -e "$TASKS" ]
then
	echo "Invalid LANG/TASKNO combination: $TASKS doesn't exist." >&2
	exit 1
fi
 
parallel --joblog "$LOG" --colsep ',' python scripts/retrieve_subtitle_exists.py --no-header < "$TASKS"
