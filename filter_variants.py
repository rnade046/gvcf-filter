import pandas as pd
from pathlib import Path
import argparse
import viz
from gvcf_utils import load_records, count_variants


def parse_arguments():
    """
    Parse arguments to obtain working directory
    :return p.parse_args(): arguments
    """
    p = argparse.ArgumentParser()
    p.add_argument("--wd", type=Path, required=True,
                   help="Working directory containing cohort folders (e.g., ~/technical_test/)")
    return p.parse_args()


def load_meta(meta_file):
    """
    load meta data as dataframe
    :param meta_file: path
    :return: sample (data frame)
    """
    samples = pd.read_csv(meta_file, sep="\t", dtype={"SampleID": "string", "Ancestry": "string"})
    # samples = samples.set_index("SampleID") # if row index is needed
    return samples


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

    # obtain working directory containing cohort directories as command line argument (--wd)
    wd = parse_arguments().wd
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
