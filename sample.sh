#!/bin/bash

# Sample 120k valid vids for each language:

if [ -z "$*" ]
then
	LANGS="ja en ja ps es fr pt zh it pl de ru cs"
else
	LANGS="$*"
fi

for lang in $(echo $LANGS)
do
	echo 'videoid,auto,sub,nsub,categories,duration,view_count,upload_date,channel_id,uploader_id,language' > sub/${lang}/${lang}_header.csv
	rm sub/${lang}/${lang}_sample.csv 2>/dev/null
	cat sub/${lang}/${lang}_*.csv > sub/${lang}/${lang}.csv
	python scripts/sample.py ${lang} sub/${lang}/${lang}.csv
	# sample saved in sub/${lang}/${lang}_sample.csv
done
