from multiprocessing import Pool, cpu_count
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import pyranges as pr
from crested import import_bigwigs
from loguru import logger


def call_quantile_peaks(
    signal: pd.Series,
    chroms: pd.Series,
    starts: pd.Series,
    ends: pd.Series,
    tilesize: int = 128,
    quantile: float = 0.98,
    blacklist_file: Optional[Path] = None,
    merge: bool = True,
) -> Optional[pr.PyRanges]:
    """Call quantile-based peaks from a single bigWig signal."""
    logger.info(f"Calling peaks for sample: {signal.name}")

    nonzero = signal[signal > 0]
    if nonzero.empty:
        logger.warning(f"[{signal.name}] No nonzero signal values.")
        return None

    threshold = nonzero.quantile(quantile)
    logger.debug(f"[{signal.name}] Quantile {quantile} threshold = {threshold:.4f}")

    peaks = signal >= threshold

    peaks_df = pd.DataFrame(
        {
            "Chromosome": chroms,
            "Start": starts,
            "End": ends,
            "Score": signal,
            "is_peak": peaks.astype(int),
        }
    )
    peaks_df = peaks_df[peaks_df["is_peak"] == 1].drop(columns="is_peak")

    if peaks_df.empty:
        logger.warning(f"[{signal.name}] No peak tiles exceed threshold.")
        return None

    peaks_df = peaks_df.astype({"Start": int, "End": int, "Chromosome": str})
    peaks_df = peaks_df.sort_values(["Chromosome", "Start"]).reset_index(drop=True)

    pr_obj = pr.PyRanges(peaks_df)
    if merge:
        pr_obj = pr_obj.merge()

    if blacklist_file and blacklist_file.exists():
        logger.debug(f"[{signal.name}] Subtracting blacklist regions: {blacklist_file}")
        blacklist = pr.read_bed(str(blacklist_file))
        pr_obj = pr_obj.subtract(blacklist)

    logger.info(f"[{signal.name}] Final peak count: {len(pr_obj)}")
    return pr_obj if len(pr_obj) > 0 else None


def _process_sample(args):
    """Wrapper to process one bigWig file."""
    (
        sample_path,
        tiled_df,
        chromsizes_file,
        blacklist_file,
        tilesize,
        quantile,
        output_dir,
    ) = args
    sample_name = sample_path.stem

    logger.info(f"Processing sample: {sample_name}")
    tmp_bed = output_dir / f"{sample_name}.tiled_regions.bed"

    # Save tiled regions to temporary BED file
    pr.PyRanges(tiled_df).to_bed(tmp_bed)

    try:
        adata = import_bigwigs(
            regions_file=str(tmp_bed),
            bigwigs_folder=str(sample_path.parent),
            chromsizes_file=str(chromsizes_file),
            include_files=[sample_path.name],
            target="mean",
        )
        signal = np.log1p(adata.X.squeeze())
    except Exception as e:
        logger.error(f"[{sample_name}] Failed to load or process: {e}")
        return None

    pr_obj = call_quantile_peaks(
        signal=pd.Series(signal, name=sample_name),
        chroms=tiled_df["Chromosome"],
        starts=tiled_df["Start"],
        ends=tiled_df["End"],
        tilesize=tilesize,
        quantile=quantile,
        blacklist_file=blacklist_file,
    )

    if pr_obj is not None:
        output_bed = output_dir / f"{sample_name}.bed"
        pr_obj.to_bed(output_bed)
        logger.success(f"Peak BED saved to: [{output_bed}]")
        return str(output_bed)
    else:
        logger.warning(f"[{sample_name}] No peaks detected.")
        return None


def call_peaks_from_bigwig_dir(
    bigwig_dir: Path,
    output_dir: Path,
    chromsizes_file: Path,
    blacklist_file: Optional[Path] = None,
    tilesize: int = 128,
    quantile: float = 0.98,
    tmp_dir: Path = Path("tmp"),
    n_threads: Optional[int] = None,
) -> list[str]:
    """Call quantile-based peaks from all bigWig files in a directory, in parallel."""
    bigwig_dir = Path(bigwig_dir)
    output_dir = Path(output_dir)
    chromsizes_file = Path(chromsizes_file)
    blacklist_file = Path(blacklist_file) if blacklist_file else None
    tmp_dir = Path(tmp_dir)
    n_threads = n_threads or max(cpu_count() - 1, 1)

    output_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    chromsizes = (
        pd.read_csv(chromsizes_file, sep="\t", names=["Chromosome", "End"], usecols=[0, 1])
        .query("~Chromosome.str.contains('_')", engine="python")
        .assign(Start=0)[["Chromosome", "Start", "End"]]
    )

    logger.info(f"Tiling genome with tilesize {tilesize} bp...")
    full_ranges = pr.PyRanges(chromsizes)
    tiled = full_ranges.tile(tilesize).intersect(full_ranges)

    if blacklist_file and blacklist_file.exists():
        logger.info(f"Applying blacklist from: {blacklist_file}")
        blacklist = pr.read_bed(str(blacklist_file))
        tiled = tiled.subtract(blacklist)

    tiled_df = tiled.df
    tmp_regions_bed = tmp_dir / "tiled_regions.bed"
    tiled.to_bed(tmp_regions_bed)
    logger.info(f"Tiled regions saved to: {tmp_regions_bed}")

    bigwig_paths = sorted(bigwig_dir.glob("*.bw")) + sorted(bigwig_dir.glob("*.bigWig"))
    if not bigwig_paths:
        logger.error(f"No .bw or .bigWig files found in {bigwig_dir}")
        return []

    logger.info(f"Found {len(bigwig_paths)} bigWig file(s)")
    logger.info(f"Processing in parallel with {n_threads} threads...")

    args_list = [
        (
            path,
            tiled_df.copy(),
            chromsizes_file,
            blacklist_file,
            tilesize,
            quantile,
            output_dir,
        )
        for path in bigwig_paths
    ]

    with Pool(n_threads) as pool:
        result_paths = pool.map(_process_sample, args_list)

    result_paths = [r for r in result_paths if r is not None]
    logger.info(f"Finished processing {len(result_paths)} samples.")
    return result_paths
