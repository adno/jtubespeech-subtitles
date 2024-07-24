import time
# DELETEME import requests
import argparse
# DELETEME import re
import sys
# DELETEME import subprocess
from yt_dlp import YoutubeDL
from pathlib import Path
from util import make_video_url # DELETEME, get_subtitle_language
import pandas as pd
from tqdm import tqdm
import logging

def parse_args():
  parser = argparse.ArgumentParser(
    description="Retrieving whether subtitles exists or not.",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
  )
  parser.add_argument("lang",         type=str, help="language code (ja, en, ...)")
  parser.add_argument("videoidlist",  type=str, help="filename of video ID list")
  parser.add_argument("--outdir",     type=str, default="sub", help="dirname to save results")
  parser.add_argument("--checkpoint", type=str, default=None, help="filename of list checkpoint (for restart retrieving)")
  parser.add_argument("--wait",       type=float, default=0.0, help="seconds to wait between videos (default: 0.0)")
  parser.add_argument("--header",     action=argparse.BooleanOptionalAction, default=True, help='output header (default: true)')
  parser.add_argument("--intermediate", action=argparse.BooleanOptionalAction, default=False, help='output intermediate results (default: false)')
  return parser.parse_args(sys.argv[1:])


COLS = [
  'videoid', 'auto', 'sub', 'nsub', 'categories', 'duration',
  'view_count', 'upload_date', 'channel_id', 'uploader_id', 'language'
  ]

def retrieve_subtitle_exists(lang, fn_videoid, outdir="sub", wait_sec=0.0,
                             fn_checkpoint=None, header=True, intermediate=False):
  fn_sub = Path(outdir) / lang / f"{Path(fn_videoid).stem}.csv"
  fn_sub.parent.mkdir(parents=True, exist_ok=True)

  # all info fields:
  data_vid = []
  data_auto = []
  data_sub = []
  data_nsub = [] # number of manual sub languages
  data_cat = []
  data_dur = []
  data_vc = []
  data_ud = []
  data_cid = []
  data_uid = []
  data_lang = []

  # if file exists, load it and restart retrieving.
  if fn_checkpoint is None:
    pass
    # subtitle_exists = pd.DataFrame({"videoid": [], "auto": [], "sub": []}, dtype=str)
  else:
    sys.exit(1) # TODO appending not implemented
    df = (
      pd.read_csv(fn_checkpoint) if header else
      pd.read_csv(fn_checkpoint, names=COLS)
      )

  # Options corresponding to:
  # --list-subs --sub-lang {lang} --skip-download
  # --extractor-args youtube:player-client=web
  # including CLI defaults (some of which may not be necessary).
  ydl_opts = {'extract_flat': 'discard_in_playlist',
     'extractor_args': {'youtube': {'player_client': ['web']}},
     'fragment_retries': 10,
     'ignoreerrors': 'only_download',
     # 'listsubtitles': True, --- not necessary, only affects stdout
     'postprocessors': [{'key': 'FFmpegConcat',
                         'only_multi_video': True,
                         'when': 'playlist'}],
     'retries': 10,
     'skip_download': True,
     'subtitleslangs': [lang]}
  with YoutubeDL(ydl_opts) as ydl:
    # load video ID list
    n_video = 0
    for videoid in tqdm(open(fn_videoid).readlines()):
      videoid = videoid.strip(" ").strip("\n")
      # TODO appending not implemented
      # if videoid in set(subtitle_exists["videoid"]):
      #  continue

      # send query to YouTube
      url = make_video_url(videoid)
      try:
        # DELETEME result = subprocess.check_output(f"yt-dlp --list-subs --sub-lang {lang} --skip-download {url}", \
        #  shell=True, universal_newlines=True)
        # DELETEME auto_lang, manu_lang = get_subtitle_language(result)

        # Exceptions may happen here:
        info = ydl.extract_info(url, download=False)
        auto_lang = info['automatic_captions']
        manu_lang = info['subtitles']
        i_cat = '|'.join(info['categories'])
        i_dur = info['duration']
        i_vc = info['view_count']
        i_ud = info['upload_date']
        i_cid = info['channel_id']
        i_uid = info['uploader_id']
        i_lang = info['language']

        # Exceptions should not happen here:

        data_vid.append(videoid)
        data_auto.append(lang in auto_lang)
        data_sub.append(lang in manu_lang)
        data_nsub.append(len(manu_lang))
        data_cat.append(i_cat)
        data_dur.append(i_dur)
        data_vc.append(i_vc)
        data_ud.append(i_ud)
        data_cid.append(i_cid)
        data_uid.append(i_uid)
        data_lang.append(i_lang)

        n_video += 1

      except Exception as e:
        logging.warning('Error retrieving videoidlist=%s, url=%s: %r', fn_videoid, url, e, exc_info=True)

      # write current result
      if intermediate and (n_video % 100 == 0):
        df = pd.DataFrame({
          'videoid': data_vid,
          'auto': data_auto,
          'sub': data_sub,
          'nsub': data_nsub,
          'categories': data_cat,
          'duration': data_dur,
          'view_count': data_vc,
          'upload_date': data_ud,
          'channel_id': data_cid,
          'uploader_id': data_uid,
          'language': data_lang
          })
        df.to_csv(fn_sub, index=None, header=header)

      # sleep
      if wait_sec > 0.01:
        time.sleep(wait_sec)

  # write

  df = pd.DataFrame({
    'videoid': data_vid,
    'auto': data_auto,
    'sub': data_sub,
    'nsub': data_nsub,
    'categories': data_cat,
    'duration': data_dur,
    'view_count': data_vc,
    'upload_date': data_ud,
    'channel_id': data_cid,
    'uploader_id': data_uid,
    'language': data_lang
    })
  df.to_csv(fn_sub, index=None, header=header)
  return fn_sub

if __name__ == "__main__":
  args = parse_args()

  filename = retrieve_subtitle_exists(args.lang, args.videoidlist, \
    args.outdir, fn_checkpoint=args.checkpoint, wait_sec=args.wait, header=args.header,
    intermediate=args.intermediate)
  print(f"save {args.lang.upper()} subtitle info to {filename}.")
