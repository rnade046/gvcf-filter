# gVCF-filter — Variant Filtering and Het Count Summary

The pipeline iterates through each cohort directory, loads the cohort metadata table, and then processes the corresponding gzipped gVCF files (<SampleID>.gvcf.gz) for all sampleIDs listed in the metadata. Leverages Pandas dataframes, for each sample, it extracts genotype QC fields (GT, DP, GQ) from the VCF record format, filters records based on genotype and QC thresholds, and counts the number of sites that pass the filter. Finally, it outputs a cohort-level .parquet file that combines metadata with the per-sample counts and generates summary boxplots (e.g., Age and Het_Count).

## Requirements
### Directory structure

The working directory passed to the script must contain one or more cohort folders with prefix `Cohort_` (required). 
```
technical_test/
├─ Cohort_A/
│  ├─ metadata.tsv
│  ├─ <SampleID>.gvcf.gz
│  └─ <SampleID>.gvcf.gz
└─ Cohort_B/
   ├─ metadata.tsv
   └─ <SampleID>.gvcf.gz
```

### Input files
+ gvcf files prefixed SampleID correspond to meta.data column
+ current implementation assumes gvcf format order is GT:AD:DP:GQ

### Programming
- Python 3.10+ recommended
- Libraries included in requirements.txt


## How to run
```
python filter_variants.py --wd /path/to/technical_test
```

The script automatically finds cohort directories under --wd (directories starting with `Cohort_`) and generates a summary table (.parquet) and visualization (.pdf) under a newkt created outputs/ directory for eqach cohort.

### Outputs
```
Cohort_A/
└─ outputs/
   ├─ Cohort_A_output.parquet
   └─ Cohort_A_boxplots.pdf
```
