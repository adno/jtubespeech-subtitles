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
        '--outname', type=str, default=None,
        help='Output filename (default: LANG_sample.csv)'
        )
    parser.add_argument(
        '--size', '-n', type=int, default=DEFAULT_SIZE,
        help=f'Sample size (default: {DEFAULT_SIZE})'
        )

    sub = parser.add_argument_group('Subtitle conditions (matches any)')
    sub.add_argument(
        '--auto', action=argparse.BooleanOptionalAction, default=False,
        help='Auto subtitles in target language (default: false)'
        )
    sub.add_argument(
        '--manual', action=argparse.BooleanOptionalAction, default=True,
        help='Manual subtitles in target language (default: true)'
        )

    lang = parser.add_argument_group('Language conditions (matches any)')
    lang.add_argument(
        '--video-lang', action=argparse.BooleanOptionalAction, default=True,
        help='Video in the target language (default: true)'
        )
    lang.add_argument(
        '--any-lang', action=argparse.BooleanOptionalAction, default=False,
        help='No conditions on language (default: false)'
        )
    lang.add_argument(
        '--sub-lang', action=argparse.BooleanOptionalAction, default=False,
        help='Manual subtitles only in target language (default: false)'
        )
    lang.add_argument(
        '--sub-lang-video-lang-na', action=argparse.BooleanOptionalAction,
        default=False,
        help=('Manual subtitles only in target language and video language is N/A '
              '(default: false)')
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

    assert (
        args.any_lang or args.video_lang or args.sub_lang or args.sub_lang_video_lang_na
        )
    if not args.any_lang:
        lang_cond = False

        if args.video_lang:
            lang_cond |= df['language'].str.startswith(args.lang)

        if args.sub_lang:
            lang_cond |= df['sub'] & (df['nsub'] == 1)
        elif args.sub_lang_video_lang_na:
            lang_cond |= df['sub'] & (df['nsub'] == 1) & df['language'].isna()

        cond &= lang_cond

    valid = df.loc[cond]

    sys.stderr.write(
        f'Valid data size: {len(valid)}\n'
        )
    if len(valid) < args.size:
        sys.stderr.write(
            f'Warning: Data is smaller than the requested sample '
            f'size {len(valid)} < {args.size}.\n'
            )
    filename = os.path.join(
        args.outdir, args.lang,
        args.outname or f'{args.lang}_sample.csv'
        )

    # Data is ordered randomly (by video id):
    valid[:args.size].to_csv(filename, index=None)

    print(f"Saved {args.lang.upper()} sample to {filename}.")


if __name__ == '__main__':
    args = parse_args()
    main(args)
