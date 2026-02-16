import pandas as pd
import gzip

# load meta data as dataframe
def load_meta(meta_file):
   samples = pd.read_csv(meta_file, sep="\t", dtype={"SampleID": "string", "Ancestry": "string"})
   # samples = samples.set_index("SampleID") # if need index of rows
   return samples


# load variant records
# possible memory issue if datasets ++size
def load_records(gvcf_file):
    # find the line number where the column header starts (#CHROM)
    header_line_idx = None
    with gzip.open(gvcf_file, "rt", encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f):
            if line.startswith("#CHROM"):
                header_line_idx = i
                break

    # sanity check : found #CHROM header
    if header_line_idx is None:
        raise ValueError("Could not find #CHROM header in gVCF")

    # load records
    records = pd.read_csv(
        gvcf_file,
        sep="\t",
        compression="gzip",
        skiprows=header_line_idx,  # skips all the '##' meta lines before #CHROM
        header=0,
        skip_blank_lines=True,
    )
    print(f"loaded records: {records.shape}")
    print(records.head())

    return records


if __name__ == "__main__":
    wd = "/Users/rnadeau2/Documents/Technical_test/Cohort_A/"
    meta_file = wd + "metadata.tsv"
    gvcf_file = wd + "l1m7WayG.gvcf.gz"

    samples = load_meta(meta_file)
    records = load_records(gvcf_file)