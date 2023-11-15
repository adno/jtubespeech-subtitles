#!/bin/bash

TASKS="$1"
if [ -z "$TASKS" ]
then
	TASKS="word/tasks.csv"
fi

LOG="$2"
if [ -z "$LOG" ]
then
	LOG="obtain_vid.log"
fi

parallel --gnu --joblog "$LOG" --colsep ',' python scripts/obtain_video_id.py < "$TASKS"
