import pathlib
import tempfile
import warnings
from pathlib import Path
from multiprocessing import Pool, cpu_count

import pandas as pd
import pyranges as pr
from anndata import concat
from crested import import_bigwigs


def _process_chrom(args):
    chrom, chrom_regions, bigwig_dir, chromsizes_file, tmp_dir = args

    with tempfile.NamedTemporaryFile(delete=False, suffix=".bed", mode="w", dir=tmp_dir) as tmp_bed:
        chrom_regions.to_bed(tmp_bed.name)
        tmp_bed.flush()

        try:
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", message="Variable names are not unique*")

                adata = import_bigwigs(
                    regions_file=tmp_bed.name,
                    bigwigs_folder=bigwig_dir,
                    chromsizes_file=chromsizes_file,
                    target="mean"
                )
            adata.var_names_make_unique()
            return adata.T
        finally:
            Path(tmp_bed.name).unlink(missing_ok=True)


def make_dataset(
    bigwig_dir,
    output_file,
    chromsizes_file,
    regions_bed=None,
    binsize=128,
    blacklist_file=None,
    n_threads=None,
):
    tmp_regions = None
    tmp_dir = Path(output_file).parent
    n_threads = n_threads or max(cpu_count() - 1, 1)

    # Generate or load regions
    if regions_bed is None:
        chromsizes = pd.read_csv(
            chromsizes_file, sep="\t", header=None, usecols=[0, 1], names=["chrom", "size"]
        )
        bed_lines = [
            f"{row.chrom}\t{i}\t{min(i + binsize, row.size)}"
            for _, row in chromsizes.iterrows()
            for i in range(0, row.size, binsize)
        ]
        tmp_regions = tempfile.NamedTemporaryFile(delete=False, suffix=".bed", mode="w", dir=tmp_dir)
        tmp_regions.write("\n".join(bed_lines))
        tmp_regions.flush()
        regions_bed = tmp_regions.name

    # Filter blacklist if provided
    if blacklist_file:
        regions = pr.read_bed(regions_bed)
        blacklist = pr.read_bed(blacklist_file)
        filtered = regions.subtract(blacklist)
        tmp_filtered = tempfile.NamedTemporaryFile(delete=False, suffix=".bed", mode="w", dir=tmp_dir)
        filtered.to_bed(tmp_filtered.name)
        regions_bed = tmp_filtered.name

    # Ensure chromsizes is two-column
    def ensure_two_column_chromsizes(chromsizes_path):
        sample = pd.read_csv(chromsizes_path, sep="\t", header=None, nrows=5)
        if sample.shape[1] < 2:
            raise ValueError(f"{chromsizes_path} has fewer than 2 columns.")
        if sample.shape[1] > 2:
            chromsizes_df = pd.read_csv(
                chromsizes_path, sep="\t", header=None, usecols=[0, 1], names=["chrom", "size"]
            )
            tmp = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".tsv", dir=tmp_dir)
            chromsizes_df.to_csv(tmp.name, sep="\t", header=False, index=False)
            return tmp.name
        return chromsizes_path

    cleaned_chromsizes = ensure_two_column_chromsizes(chromsizes_file)

    # Split regions by chromosome
    all_regions = pr.read_bed(regions_bed)
    chrom_tasks = [
        (chrom, group, bigwig_dir, cleaned_chromsizes, tmp_dir)
        for chrom, group in all_regions.groupby("Chromosome")
    ]

    # Parallel processing
    with Pool(processes=n_threads) as pool:
        all_adata = pool.map(_process_chrom, chrom_tasks)

    # Concatenate and save
    combined = concat(all_adata, axis=0)
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    combined.write_h5ad(output_file)

    # Cleanup
    if tmp_regions is not None:
        Path(tmp_regions.name).unlink(missing_ok=True)
    if "tmp_filtered" in locals():
        Path(tmp_filtered.name).unlink(missing_ok=True)
    if str(cleaned_chromsizes) != str(chromsizes_file):
        Path(cleaned_chromsizes).unlink(missing_ok=True)

    print(f"Dataset saved to {output_file}")
