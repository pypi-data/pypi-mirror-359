import pathlib
import tempfile
import warnings
from pathlib import Path

import pandas as pd
import pyranges as pr
from crested import import_bigwigs


def make_dataset(
    bigwig_dir,
    output_file,
    chromsizes_file,
    regions_bed=None,
    binsize=128,
    blacklist_file=None,
):
    tmp_regions = None
    """
    Create a dataset from bigWig files by importing regions and applying optional filters.
    Parameters:
    - bigwig_dir: Directory containing bigWig files.
    - output_file: Path to save the output AnnData object.
    - chromsizes_file: Path to a chrom.sizes file (tab-delimited with columns: chromosome name and size).
    - regions_bed: Optional path to a BED file defining specific regions to import.
    - binsize: Size of genomic bins to create if regions_bed is None (default: 128).
    - blacklist_file: Optional BED file with regions to exclude from analysis.

    Returns:
    - None, but saves an AnnData object to output_file.
    """

    tmp_dir = Path(output_file).parent

    if regions_bed is None:
        chromsizes = pd.read_csv(
            chromsizes_file,
            sep="\t",
            header=None,
            usecols=[0, 1],
            names=["chrom", "size"],
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

    if blacklist_file:
        regions = pr.read_bed(regions_bed)
        blacklist = pr.read_bed(blacklist_file)
        filtered = regions.subtract(blacklist)
        tmp_filtered = tempfile.NamedTemporaryFile(delete=False, suffix=".bed", mode="w", dir=tmp_dir)
        filtered.to_bed(tmp_filtered.name)
        regions_bed = tmp_filtered.name


    def ensure_two_column_chromsizes(chromsizes_path: str | pathlib.Path) -> str:
        """ Ensure the chromsizes file has exactly two columns: chromosome name and size.
        If it has more than two columns, it will be cleaned to keep only the first two.
        If it has less than two columns, it will raise an error.
        """
        chromsizes_path = str(chromsizes_path)

        sample = pd.read_csv(chromsizes_path, sep="\t", header=None, nrows=5)
        
        if sample.shape[1] < 2:
            raise ValueError(f"{chromsizes_path} has fewer than 2 columns.")

        if sample.shape[1] > 2:
            chromsizes_df = pd.read_csv(
                chromsizes_path,
                sep="\t",
                header=None,
                usecols=[0, 1],
                names=["chrom", "size"],
            )

            tmp = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".tsv", dir=tmp_dir)
            chromsizes_df.to_csv(tmp.name, sep="\t", header=False, index=False)
            return tmp.name
        else:
            return chromsizes_path
    cleaned_chromsizes = ensure_two_column_chromsizes(chromsizes_file)


    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Variable names are not unique*")

        adata = import_bigwigs(
            regions_file=regions_bed,
            bigwigs_folder=bigwig_dir,
            chromsizes_file=cleaned_chromsizes,
            target="mean"
        )
    adata.var_names_make_unique()
    adata = adata.T

    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    adata.write_h5ad(output_file)

    # Clean up temporary file
    if tmp_regions is not None:
        Path(tmp_regions.name).unlink(missing_ok=True)

    if "tmp_filtered" in locals():
        Path(tmp_filtered.name).unlink(missing_ok=True)

    if "cleaned_chromsizes" in locals() and str(cleaned_chromsizes) != str(chromsizes_file):
        Path(cleaned_chromsizes).unlink(missing_ok=True)

    print(f"Dataset saved to {output_file}")