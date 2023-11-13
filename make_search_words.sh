#!/bin/bash

true > word/tasks.csv

#task_id=1
for lang in en ja ps es fr pt zh it pl de ru cs
do
    # python scripts/make_search_word.py $lang
    # split -l 10000 -d -a 6 "word/word/${lang}/${lang}wiki-latest-pages-articles-multistream-index.txt" "word/word/${lang}/${lang}wiki-latest-pages-articles-multistream-index_part"
    for part in $(seq -w 0 999999)
    do
        words="word/word/${lang}/${lang}wiki-latest-pages-articles-multistream-index_part${part}"
        if ! [ -e "$words" ]; then break; fi
        # echo $lang$part
        # sbatch -A lang -p lang_short -c 1 -J $lang$part ./obtain_video_id_lang_words.sh $lang $words
        printf "$lang,$words\n" >> word/tasks.csv
		#task_id="$(($task_id+1))"
    done
done
