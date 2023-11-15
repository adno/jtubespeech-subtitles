#!/bin/bash

# for lang in en ja ps # es fr pt zh it pl de ru cs
# do
# 	cat videoid/${lang}/${lang}wiki-latest-pages-articles-multistream-index_part*.txt \
# 		| sort -u > videoid/${lang}/${lang}.txt
# done

# for lang in en ja ps es # fr pt zh it pl de ru cs
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

# split -l 96 -d -a 6 videoid/tasks_jaenpses.csv videoid/tasks_jaenpses_part

TASKNO="$1"
if [ -z "$TASKNO" ]
then
	echo "Need TASKNO as argument." >&2
	exit 1
fi

TASKNO="$(printf '%06d' $TASKNO)"
TASKS="videoid/tasks_jaenpses_part$TASKNO"
LOG="retrieve_${TASKNO}.log"
 
parallel --joblog "$LOG" --colsep ',' python scripts/retrieve_subtitle_exists.py --no-header < "$TASKS"

exit 0

# Sample 120k "valid" vids for each language:

for lang in ja # en ja ps es # fr pt zh it pl de ru cs
do
	echo 'videoid,auto,sub,categories,duration,view_count,upload_date,channel_id,uploader_id,language' > sub/${lang}/${lang}_header.csv
	cat sub/${lang}/${lang}_*.csv > sub/${lang}/${lang}.csv
	python scripts/sample.py ja sub/${lang}/${lang}.csv
	# sample saved in sub/${lang}/${lang}_sample.csv
done