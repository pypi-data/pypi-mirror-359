import warnings

warnings.filterwarnings("ignore", message="pkg_resources*")

import argparse
import sys
import traceback
from pathlib import Path

from loguru import logger

from QuantNado.call_quantile_peaks import call_peaks_from_bigwig_dir
from QuantNado.make_dataset import make_dataset


def call_peaks_main():
    parser = argparse.ArgumentParser(
        description="Call quantile-based peaks from bigWig files"
    )
    parser.add_argument(
        "--bigwig-dir",
        required=True,
        type=Path,
        help="Directory containing bigWig files",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="Directory to save output peak files (BED format)",
    )
    parser.add_argument(
        "--chromsizes",
        required=True,
        help="Path to a two-column chromsizes file (chromosome, size)",
    )
    parser.add_argument(
        "--blacklist", default=None, help="Path to a BED file with regions to exclude"
    )
    parser.add_argument(
        "--tilesize",
        type=int,
        default=128,
        help="Size of genomic tiles to create (default: 128 bp)",
    )
    parser.add_argument(
        "--quantile",
        type=float,
        default=0.98,
        help="Quantile threshold for peak calling (default: 0.98)",
    )
    parser.add_argument(
        "--merge",
        action="store_true",
        help="Merge overlapping peaks after quantile calling (default: False)",
    )
    parser.add_argument(
        "--tmp-dir",
        default="tmp",
        type=Path,
        help="Temporary directory for intermediate files (default: 'tmp')",
    )
    parser.add_argument(
        "--log-file",
        default="logs/quantnado.log",
        type=Path,
        help="Path to the log file (default: 'logs/quantnado.log')",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()
    
    if not args.log_file.parent.exists():
        args.log_file.parent.mkdir(parents=True, exist_ok=True)

    if args.log_file.exists():
        args.log_file.unlink()
        
    _setup_logging(args.log_file, args.verbose)

    try:
        call_peaks_from_bigwig_dir(
            bigwig_dir=args.bigwig_dir,
            output_dir=args.output_dir,
            chromsizes_file=args.chromsizes,
            blacklist_file=args.blacklist,
            tilesize=args.tilesize,
            quantile=args.quantile,
            merge=args.merge,
            tmp_dir=args.tmp_dir,
        )
        logger.success(f"Finished calling peaks: {args.output_dir}")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Peak calling failed: {type(e).__name__}: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)


def make_dataset_main():
    parser = argparse.ArgumentParser(
        description="Generate an AnnData or MuData dataset from bigWigs"
    )
    parser.add_argument(
        "--bigwig-dir",
        required=True,
        type=Path,
        help="Directory containing bigWig files",
    )
    parser.add_argument(
        "--output-file",
        required=True,
        type=Path,
        help="Output file path for the dataset (AnnData with .h5ad extension)",
    )
    parser.add_argument(
        "--chromsizes",
        required=True,
        help="Path to a two-column chromsizes file (chromosome, size)",
    )
    parser.add_argument(
        "--regions", default=None, help="Path to a BED file with regions to use"
    )
    parser.add_argument(
        "--binsize",
        type=int,
        default=128,
        help="Size of genomic bins to create (if --regions is not provided)",
    )
    parser.add_argument(
        "--blacklist", default=None, help="Path to a BED file with regions to exclude"
    )
    parser.add_argument(
        "--log-file",
        default="logs/quantnado.log",
        type=Path,
        help="Path to the log file (default: 'logs/quantnado.log')",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    
    if not args.log_file.parent.exists():
        args.log_file.parent.mkdir(parents=True, exist_ok=True)

    if args.log_file.exists():
        args.log_file.unlink()
        
    _setup_logging(args.log_file, args.verbose)
    
    try:
        make_dataset(
            bigwig_dir=args.bigwig_dir,
            output_file=args.output_file,
            chromsizes_file=args.chromsizes,
            regions_bed=args.regions,
            blacklist_file=args.blacklist,
            binsize=args.binsize,
        )
        logger.success(f"Finished building dataset: {args.output_file}")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Dataset generation failed: {type(e).__name__}: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)


def _setup_logging(log_path: Path, verbose: bool):
    logger.remove()
    log_format = "{time:YYYY-MM-DD HH:mm:ss} [{level}] {message}"
    logger.add(log_path, level="DEBUG", format=log_format)
    logger.add(sys.stderr, level="DEBUG" if verbose else "INFO", format=log_format)