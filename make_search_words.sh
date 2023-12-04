#!/bin/bash

true > word/tasks.csv

for lang in en ja ps es fr pt zh it pl de ru cs ur id
do
    python scripts/make_search_word.py $lang
    split -l 10000 -d -a 6 "word/word/${lang}/${lang}wiki-latest-pages-articles-multistream-index.txt" "word/word/${lang}/${lang}wiki-latest-pages-articles-multistream-index_part"
    for part in $(seq -w 0 999999)
    do
        words="word/word/${lang}/${lang}wiki-latest-pages-articles-multistream-index_part${part}"
        if ! [ -e "$words" ]; then break; fi
        printf "$lang,$words\n" >> word/tasks.csv
    done
done
