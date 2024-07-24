import time
import requests
import argparse
import sys
from pathlib import Path
from util import make_query_url, html2videoids
from tqdm import tqdm

def parse_args():
  parser = argparse.ArgumentParser(
    description="Obtaining video IDs from search words",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
  )
  parser.add_argument("lang",     type=str, help="language code (ja, en, ...)")
  parser.add_argument("wordlist", type=str, help="filename of word list")
  parser.add_argument("--outdir", type=str, default="videoid", help="dirname to save video IDs")
  parser.add_argument("--wait",   type=float, default=0.0, help="seconds to wait between words (default: 0.0)")
  parser.add_argument("--keep-alive",       action=argparse.BooleanOptionalAction, default=True, help='HTTP keep-alive')
  parser.add_argument("--google",           action=argparse.BooleanOptionalAction, default=False, help='Search using Google instead of YouTube')
  parser.add_argument("--google-max-pages", type=int, default=2, help='Max search result pages (100 results) retrieved from Google per query')
  return parser.parse_args(sys.argv[1:])


def obtain_video_id(lang, fn_word, outdir="videoid", wait_sec=0.2,
                    keep_alive=True, google=False, max_pages=2):
  fn_videoid = Path(outdir) / lang / f"{Path(fn_word).stem}.txt"
  fn_videoid.parent.mkdir(parents=True, exist_ok=True)

  get_url = requests.Session().get if keep_alive else requests.get

  with open(fn_videoid, "w") as f:
    for word in tqdm(list(open(fn_word, "r").readlines())):
      try:

        videoids_found = set()
        for i in range(max_pages if google else 1):
            # download search results
            url = make_query_url(word, google=google, index=i)
            html = get_url(url).content
            # find video IDs
            page_videoids = html2videoids(html, google=google)
            if not page_videoids:
                break
            videoids_found.update(page_videoids)

        # write
        f.writelines([v + "\n" for v in videoids_found])
        f.flush()
      except Exception as e:
        # TODO: not found causes an exception?
        print(f"No video found for {word}, error = {e}.")

      # wait
      if wait_sec > 0.01:
        time.sleep(wait_sec)

  return fn_videoid


if __name__ == "__main__":
  args = parse_args()

  filename = obtain_video_id(args.lang, args.wordlist, args.outdir,
    wait_sec=args.wait, keep_alive=args.keep_alive,
    google=args.google, max_pages=args.google_max_pages
    )
  print(f"save {args.lang.upper()} video IDs to {filename}.")
