import time
import argparse
import sys
import shutil
# import pydub -- imported contitionally - not necessary for --subtitles-only
from pathlib import Path
from util import make_video_url, make_basename, vtt2txt  # UNUSED: autovtt2txt
import pandas as pd
from tqdm import tqdm
from yt_dlp import YoutubeDL


def parse_args():
  parser = argparse.ArgumentParser(
    description="Downloading videos with subtitle.",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
  )
  parser.add_argument("lang",         type=str, help="language code (ja, en, ...)")
  parser.add_argument("sublist",      type=str, help="filename of list of video IDs with subtitles")
  parser.add_argument("--dry-run",    action='store_true', help='Only print names of videos that would be downloaded (files do not exist yet).')
  parser.add_argument("--start",      type=int, default=0,    help="start index")
  parser.add_argument("--size",       type=int, default=None, help="maximum number of items do download (starting at --start; default: no limit)")
  parser.add_argument("--outdir",     type=str, default="video", help="dirname to save videos")
  parser.add_argument("--keeporg",    action='store_true', default=False, help="keep original audio file.")
  parser.add_argument("--wait",       type=float, default=0.0, help="seconds to wait between videos (default: 0.0)")
  parser.add_argument("--subtitles-only", action='store_true', default=False, help="download subtitles, no audio")
  return parser.parse_args(sys.argv[1:])


def download_video(
  lang, fn_sub, outdir="video", wait_sec=10, keep_org=False, subs_only=False,
  start=0, size=None, dry_run=False
  ):
  """
  Tips:
    If you want to download automatic subtitles instead of manual subtitles, please change as follows.
      1. replace "sub[sub["sub"]==True]" of for-loop with "sub[sub["auto"]==True]"
      2. replace "--write-sub" option of yt-dlp with "--write-auto-sub"
      3. replace vtt2txt() with autovtt2txt()
      4 (optional). change fn["vtt"] (path to save subtitle) to another.
  """

  assert start >= 0, start
  assert size is None or size >= 1, size

  sub = pd.read_csv(fn_sub)

  # e.g. start=0,size=1 => stop=0 (pandas uses inclusive indexing)
  stop = None if (size is None) else (start + size - 1)
  sub = sub.loc[start:stop]

  dl_path_tmpl = str(
    Path(outdir) / lang / ('txt' if subs_only else 'wav') / '%(id).2s' / '%(id)s.%(ext)s'
    ) # TODO messes up the txt dir, but compatible with `base = fn["txt"]...` below

  ydl_opts = {
   'extract_flat': 'discard_in_playlist',
   'extractor_args': {'youtube': {'player_client': ['web']}},
   'fragment_retries': 10,
   'ignoreerrors': 'only_download',
   # Subdirectories based on first 2 chars compatible with make_basename():
   'outtmpl': {'default': dl_path_tmpl},
   'postprocessors': [{'key': 'FFmpegConcat',
                       'only_multi_video': True,
                       'when': 'playlist'}],
   'retries': 10,
   'skip_download': subs_only,
   'subtitleslangs': [lang],
   'writesubtitles': True
   }

  for videoid in tqdm(sub[sub["sub"]]["videoid"]): # manual subtitle only
    fn = {}
    for k in (["vtt", "txt"] if subs_only else ["wav", "wav16k", "vtt", "txt"]):
      fn[k] = Path(outdir) / lang / k / (make_basename(videoid) + "." + k[:3])
      fn[k].parent.mkdir(parents=True, exist_ok=True)

    exists = (subs_only or fn["wav16k"].exists()) and fn["txt"].exists()
    if not exists:
      print(videoid)
      if dry_run:
        continue

      # download
      # TODO: Use "yt-dlp" like the current version, is it worth it?
      url = make_video_url(videoid)
      if subs_only:
        base = fn["txt"].parent.joinpath(fn["txt"].stem)
        # cp = subprocess.run(f"yt-dlp --sub-lang {lang} --extractor-args youtube:player-client=web --skip-download --write-sub {url} -o {base}.\%\(ext\)s", shell=True,universal_newlines=True)
      else:
        base = fn["wav"].parent.joinpath(fn["wav"].stem)
        # cp = subprocess.run(f"yt-dlp --sub-lang {lang} --extract-audio --audio-format wav --write-sub {url} -o {base}.\%\(ext\)s", shell=True,universal_newlines=True)
      with YoutubeDL(ydl_opts) as ydl:
        # Note: creating a new YoutubeDL is the only way to reset the return code,
        # otherwise we keep getting errrors...
        dl_returncode = ydl.download(url)
      if dl_returncode != 0:
        print(f"Failed to download the video: url = {url}, returncode={dl_returncode}")
        continue
      try:
        shutil.move(f"{base}.{lang}.vtt", fn["vtt"])
      except Exception as e:
        print(f"Failed to rename subtitle file. The download may have failed: url = {url}, filename = {base}.{lang}.vtt, error = {e}")
        continue

      # vtt -> txt (reformatting)
      try:
        txt = vtt2txt(open(fn["vtt"], "r").readlines())
        with open(fn["txt"], "w") as f:
          f.writelines([f"{t[0]:1.3f}\t{t[1]:1.3f}\t\"{t[2]}\"\n" for t in txt])
      except Exception as e:
        print(f"Failed to convert subtitle file to txt file: url = {url}, filename = {fn['vtt']}, error = {e}")
        continue


      if not subs_only:
        # wav -> wav16k (resampling to 16kHz, 1ch)
        try:
          wav = pydub.AudioSegment.from_file(fn["wav"], format="wav")
          wav = pydub.effects.normalize(wav, 5.0).set_frame_rate(16000).set_channels(1)
          wav.export(fn["wav16k"], format="wav", bitrate="16k")
        except Exception as e:
          print(f"Failed to normalize or resample downloaded audio: url = {url}, filename = {fn['wav']}, error = {e}")
          continue

        # remove original wav
        if not keep_org:
          fn["wav"].unlink()

      # wait
      if wait_sec > 0.01:
        time.sleep(wait_sec)

  return Path(outdir) / lang


if __name__ == "__main__":
  args = parse_args()

  if not args.subtitles_only:
    import pydub

  dirname = download_video(
    args.lang, args.sublist, args.outdir,
    keep_org=args.keeporg, wait_sec=args.wait, subs_only=args.subtitles_only,
    start=args.start, size=args.size, dry_run=args.dry_run
    )
  print(f"save {args.lang.upper()} videos to {dirname}.")
