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
  return parser.parse_args(sys.argv[1:])


def retrieve_subtitle_exists(lang, fn_videoid, outdir="sub", wait_sec=0.0, fn_checkpoint=None):
  fn_sub = Path(outdir) / lang / f"{Path(fn_videoid).stem}.csv"
  fn_sub.parent.mkdir(parents=True, exist_ok=True)

  # if file exists, load it and restart retrieving.
  if fn_checkpoint is None:
    subtitle_exists = pd.DataFrame({"videoid": [], "auto": [], "sub": []}, dtype=str)
  else:
    subtitle_exists = pd.read_csv(fn_checkpoint)

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
     'subtitleslangs': [f'{lang}']}
  with YoutubeDL(ydl_opts) as ydl:
    # load video ID list
    n_video = 0
    for videoid in tqdm(open(fn_videoid).readlines()):
      videoid = videoid.strip(" ").strip("\n")
      if videoid in set(subtitle_exists["videoid"]):
        continue

      # send query to YouTube
      url = make_video_url(videoid)
      try:
        # DELETEME result = subprocess.check_output(f"yt-dlp --list-subs --sub-lang {lang} --skip-download {url}", \
        #  shell=True, universal_newlines=True)
        # DELETEME auto_lang, manu_lang = get_subtitle_language(result)
        info = ydl.extract_info(url, download=False)
        manu_lang = info['subtitles']
        auto_lang = info['automatic_captions']
        subtitle_exists = subtitle_exists.append( \
          {"videoid": videoid, "auto": lang in auto_lang, "sub": lang in manu_lang},
          ignore_index=True)
        n_video += 1
      except:
        pass

      # write current result
      if n_video % 100 == 0:
        subtitle_exists.to_csv(fn_sub, index=None)

      # sleep
      if wait_sec > 0.01:
        time.sleep(wait_sec)

  # write
  subtitle_exists.to_csv(fn_sub, index=None)
  return fn_sub

if __name__ == "__main__":
  args = parse_args()

  filename = retrieve_subtitle_exists(args.lang, args.videoidlist, \
    args.outdir, fn_checkpoint=args.checkpoint, wait_sec=args.wait)
  print(f"save {args.lang.upper()} subtitle info to {filename}.")
