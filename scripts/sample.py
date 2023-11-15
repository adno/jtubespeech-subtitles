import pandas as pd
import argparse
import sys
import os

DEFAULT_SIZE = 120_000


def parse_args():
    parser = argparse.ArgumentParser(
        description='Sample videos for the corpus based on retrieved data.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
    parser.add_argument(
        'lang', type=str, help='Language code (ja, en, ...)'
        )
    parser.add_argument(
        'subdata', type=str,
        help='Filename of the retrieved subtitle data, e.g. sub/en/en'
        )
    parser.add_argument(
        '--outdir', type=str, default='sub', help='Dirname to save results'
        )
    parser.add_argument(
        '--size', '-n', type=int, default=DEFAULT_SIZE,
        help=f'Sample size (default: {DEFAULT_SIZE})'
        )
    parser.add_argument(
        '--auto', action=argparse.BooleanOptionalAction, default=False,
        help='Get auto subtitles (default: false)'
        )
    parser.add_argument(
        '--manual', action=argparse.BooleanOptionalAction, default=True,
        help='Get manual subtitles (default: true)'
        )
    parser.add_argument(
        '--require-lang', action=argparse.BooleanOptionalAction, default=True,
        help='Require subtitles to be in the target language (default: true)'
        )
    return parser.parse_args()


def main(args):
    df = pd.read_csv(args.subdata)

    assert len(args.lang) == 2, args.lang

    cond = False
    assert args.auto or args.manual
    if args.manual:
        cond |= df['sub']
    if args.auto:
        cond |= df['auto']

    if args.require_lang:
        cond &= df['language'].str.startswith(args.lang)

    valid = df.loc[cond]

    sys.stderr.write(
        f'Valid data size: {len(valid)}\n'
        )
    if len(valid) < args.size:
        sys.stderr.write(
            f'Warning: Data is smaller than the requested sample '
            f'size {len(valid)} < {args.size}.\n'
            )
    filename = os.path.join(args.outdir, args.lang, f'{args.lang}_sample.csv')

    # Data is ordered randomly (by video id):
    valid[:args.size].to_csv(filename)

    print(f"Saved {args.lang.upper()} sample to {filename}.")


if __name__ == '__main__':
    args = parse_args()
    main(args)
