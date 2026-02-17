import pandas as pd
from pathlib import Path
import gzip
import viz


def load_meta(meta_file):
    """
    load meta data as dataframe
    :param meta_file:
    :return: sample (data frame)
    """
    samples = pd.read_csv(meta_file, sep="\t", dtype={"SampleID": "string", "Ancestry": "string"})
    # samples = samples.set_index("SampleID") # if row index is needed
    return samples


def load_records(gvcf_file, sample_id):
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
    # parts[0]=GT, parts[1]=AD, parts[2]=DP, parts[3]=GQ
    parts = records[sample_id].str.split(":", expand=True)

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
            records["GT"].isin(["0/1", "1/0", "0|1", "1|0"])  # heterogeneous phased or un-phased
            & (records["DP"] > 20)
            & (records["GQ"] >= 30)
    )

    # filter data frame
    passing_records = records[filter]
    # #rows in filtered df corresponds to #variants
    return len(passing_records)


def create_output_file(samples, het_counts, cohort_name, out_file):
    """
    Writes the samples meta-data, cohort, and het_counts to parquet file
    :param samples: meta-data table (dataframe)
    :param het_counts: cohort heterogeneous counts per sample (dict)
    :param cohort_name: eg. 'Cohort_A' (String)
    :param out_file: .parquet (Path)
    :return combined_df: summary dataframe
    """
    # convert het_count dictionary to dataframe
    het_counts_df = pd.DataFrame(het_counts.items(), columns=["SampleID", "Het_Count"])

    # add cohort information
    cohort = cohort_name.split("_", 1)[1]
    samples["Cohort"] = cohort

    # combine and write dataframe
    combined_df = pd.merge(samples, het_counts_df, on="SampleID")
    combined_df.to_parquet(out_file, index=False)
    return combined_df

if __name__ == "__main__":

    wd = Path("/Users/rnadeau2/Documents/Technical_test/")

    # obtain list of cohorts (must be directory and begin with "Cohort_")
    cohort_dirs = sorted(p for p in wd.iterdir() if p.is_dir() and p.name.startswith("Cohort_"))

    # group by cohort
    for cohort_dir in cohort_dirs:
        cohort_name = cohort_dir.name
        meta_path = cohort_dir / "metadata.tsv"
        out_dir = cohort_dir / "outputs"
        out_dir.mkdir(exist_ok=True)  # create output directory
        output_path = out_dir / f"{cohort_name}_output.parquet"
        viz_path = out_dir / f"{cohort_name}_boxplots.pdf"

        het_counts = {}  # initialize count dict

        # load meta data
        samples = load_meta(meta_path)

        # group by sampleID
        for sample_id in samples["SampleID"]:
            gvcf_path = cohort_dir / f"{sample_id}.gvcf.gz"
            if gvcf_path.exists():
                # load records table & extract {GT, DP and GQ}
                records = load_records(gvcf_path, sample_id)
                # filter records & count heterogeneous variants
                het_counts[sample_id] = count_variants(records)

                print(het_counts[sample_id])

        # generate outputs .parquet file & summary visualizations
        samples2 = create_output_file(samples, het_counts, cohort_name, output_path)
        viz.plot_het_count_age(samples2, cohort_name, viz_path)
