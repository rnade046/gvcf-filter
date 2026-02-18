import pandas as pd
import gzip


def load_records(gvcf_file, sample_id):
    """
    load variant records
    possible memory issue if datasets ++size
    :param gvcf_file: path
    :param sample_id: string
    :return records: (data frame)
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
        skiprows=header_line_idx,  # skips all the '##' header lines before #CHROM
        header=0,
        skip_blank_lines=True,
    )
    print(f"loaded records: {records.shape}")

    # parse FORMAT column assuming constant order [GT:AD:DP:GQ]
    # parts[0]=GT, parts[1]=AD, parts[2]=DP, parts[3]=GQ
    parts = records[sample_id].str.split(":", expand=True)

    records["GT"] = parts[0]
    records["DP"] = parts[2].astype("int64")
    records["GQ"] = parts[3].astype("int64")
    return records


def count_variants(records):
    """
    Filter records data frame and count variants
    :param records: data frame
    :return count: int
    """
    # set filter for GT, DP, GQ columns
    # For scaling: consider using a config file
    qc_filters = (
            records["GT"].isin(["0/1", "1/0", "0|1", "1|0"])  # heterogeneous phased or un-phased
            & (records["DP"] > 20)
            & (records["GQ"] >= 30)
    )

    # filter data frame
    passing_records = records[qc_filters]
    # #rows in filtered df corresponds to #variants
    return len(passing_records)
