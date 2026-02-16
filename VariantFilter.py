import pandas as pd

# load meta data as dataframe
def load_meta(meta_file):
   samples = pd.read_csv(meta_file, sep="\t", dtype={"SampleID": "string", "Ancestry": "string"})
   return samples


if __name__ == "__main__":
    wd = "/Users/rnadeau2/Documents/Technical_test/Cohort_A/"
    meta_file = wd + "metadata.tsv"

    samples = load_meta(meta_file)
