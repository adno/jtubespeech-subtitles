#!/bin/bash

# Sample 120k valid vids for each language

# --check: Only check all files (output to stderr), do not sample.
# --list-bad: Output bad filenames only to stdout.
# --list-ok: Output bad filenames only to stdout.

check=''
list=''
list_bad=''
exit_value=0
if [ "$1" = '--check' ]
then
	check=1
	shift
elif [ "$1" = '--list-bad' ] || [ "$1" = '--list-ok' ]
then
	check=1
	list=1
	[ "$1" = '--list-bad' ]
	list_bad="$?"
	shift
fi

if [ -z "$*" ]
then
	LANGS="ja en ja ps es fr pt zh it pl de ru cs"
else
	LANGS="$*"
fi


HEADER='videoid,auto,sub,nsub,categories,duration,view_count,upload_date,channel_id,uploader_id,language'

count_cols(){
	echo $(($(sed -e 's/[^,]//g' | wc -c) + 1))
}
HEADER_COLS="$(echo "$HEADER" | count_cols)"

for lang in $(echo $LANGS)
do
	if [ -z "$check" ]
	then
		echo "$HEADER" > sub/${lang}/${lang}_header.csv
		rm sub/${lang}/${lang}_sample.csv 2>/dev/null
	fi
	
	# Check input files before concatenating:
	for f in sub/${lang}/${lang}_*.csv
	do
		if [ "$f" == "sub/${lang}/${lang}_sample.csv" ] || \
		   [ "$f" == "sub/${lang}/${lang}_header.csv" ]
		then
			continue
		fi
		f_cols="$(head -n1 "$f" | count_cols)"
		if [ -n "$list" ]
		then
			[ "$f_cols" -ne "$HEADER_COLS" ]
			is_bad="$?"
			if [ "$is_bad" = "$list_bad" ]
			then
				echo "$f"
			fi
		elif [ "$f_cols" -ne "$HEADER_COLS" ]
		then
			echo "Error: File $f has $f_cols columns. Expected $HEADER_COLS." >&2
			if [ -z "$check" ]
			then
				exit 1
			else
				exit_value=1
			fi
		fi
	done
	
	if [ -z "$check" ]
	then
		cat sub/${lang}/${lang}_*.csv > sub/${lang}/${lang}.csv
		python scripts/sample.py ${lang} sub/${lang}/${lang}.csv
	fi
	
	# sample saved in sub/${lang}/${lang}_sample.csv
done

exit "$exit_value"
