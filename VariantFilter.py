import pandas as pd
import gzip

def load_meta(meta_file):
    """
    load meta data as dataframe
    :param meta_file:
    :return: sample (data frame)
    """
    samples = pd.read_csv(meta_file, sep="\t", dtype={"SampleID": "string", "Ancestry": "string"})
    # samples = samples.set_index("SampleID") # if need index of rows
    return samples


def load_records(gvcf_file):
    """
    load variant records
    possible memory issue if datasets ++size
    :param gvcf_file:
    :return: records (data frame)
    """
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

    # parse FORMAT column assuming constant order [GT:AD:DP:GQ]
    sample_col = "l1m7WayG"   # TO UPDATE: in future use SampleID

    # parts[0]=GT, parts[1]=AD, parts[2]=DP, parts[3]=GQ
    parts = records[sample_col].str.split(":", expand=True)

    records["GT"] = parts[0]
    records["DP"] = parts[2].astype("int64")
    records["GQ"] = parts[3].astype("int64")
    print(records.head())

    return records


def count_variants(records):
    """
    Filter records data frame and count variants
    :param records: data frame
    :return count: int
    """
    # set filter for GT, DP, GQ columns
    filter = (
            records["GT"].isin(["0/1", "1/0", "0|1", "1|0"]) # heterogeneous phased or un-phased
            & (records["DP"] > 20)
            & (records["GQ"] >= 30)
    )

    # filter data frame
    passing_records = records[filter]
    # #rows in filtered df corresponds to #variants
    return len(passing_records)


if __name__ == "__main__":
    wd = "/Users/rnadeau2/Documents/Technical_test/Cohort_A/"
    meta_file = wd + "metadata.tsv"
    gvcf_file = wd + "l1m7WayG.gvcf.gz"
    
    sampleID = "l1m7WayG"
    het_counts = {}

    samples = load_meta(meta_file)
    records = load_records(gvcf_file)
    het_counts[sampleID] = count_variants(records)
    het_counts[sampleID] = count_variants(records)