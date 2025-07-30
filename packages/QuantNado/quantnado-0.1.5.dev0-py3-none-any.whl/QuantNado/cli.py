import warnings
warnings.filterwarnings("ignore", message="pkg_resources*")


import argparse
import sys
from pathlib import Path

from loguru import logger

from QuantNado.call_quantile_peaks import call_peaks_from_bigwig_dir
from QuantNado.make_dataset import make_dataset


def call_peaks_main():
    parser = argparse.ArgumentParser(description="Call quantile-based peaks from bigWig files")
    parser.add_argument("--bigwig-dir", required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--chromsizes", required=True)
    parser.add_argument("--blacklist", default=None)
    parser.add_argument("--tilesize", type=int, default=128)
    parser.add_argument("--quantile", type=float, default=0.98)
    parser.add_argument("--merge", action="store_true")
    parser.add_argument("--tmp-dir", default="tmp")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    _setup_logging(args.output_dir, args.verbose)
    result = call_peaks_from_bigwig_dir(
        bigwig_dir=args.bigwig_dir,
        output_dir=args.output_dir,
        chromsizes_file=args.chromsizes,
        blacklist_file=args.blacklist,
        tilesize=args.tilesize,
        quantile=args.quantile,
        tmp_dir=args.tmp_dir,
        merge=args.merge,
    )
    sys.exit(0 if result else 1)


def make_dataset_main():
    parser = argparse.ArgumentParser(description="Generate an AnnData or MuData dataset from bigWigs")
    parser.add_argument("--bigwig-dir", required=True)
    parser.add_argument("--output-file", required=True)
    parser.add_argument("--chromsizes", required=True)
    parser.add_argument("--regions", default=None)
    parser.add_argument("--binsize", type=int, default=128)
    parser.add_argument("--blacklist", default=None)
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    output_dir = Path(args.output_file).parent
    _setup_logging(output_dir, args.verbose)
    result = make_dataset(
        bigwig_dir=args.bigwig_dir,
        output_file=args.output_file,
        chromsizes_file=args.chromsizes,
        regions_bed=args.regions,
        binsize=args.binsize,
        blacklist_file=args.blacklist,
    )
    sys.exit(0 if result else 1)


def _setup_logging(log_dir, verbose):
    logger.remove()
    log_format = "{time:YYYY-MM-DD HH:mm:ss} [{level}] {message}"
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    logger.add(Path(log_dir) / "quantnado_run.log", level="DEBUG", format=log_format)
    logger.add(sys.stderr, level="DEBUG" if verbose else "INFO", format=log_format)
