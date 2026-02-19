# gVCF-filter — Variant Filtering and Het Count Summary

### Project description
Given a working directory containing one or more cohort folders, this pipeline processes each cohort by:

1. Loading cohort metadata
2. Locating and reading the corresponding gzipped gVCF file (`<SampleID>.gvcf.gz`) for each `SampleID` listed in the metadata
3. Extracting genotype and QC fields (`GT`, `DP`, `GQ`) from the sample field
4. Filtering variant records using genotype and QC thresholds
5. Counting the number of sites that pass filtering per sample
6. Writing a cohort-level `.parquet` summary (metadata + per-sample counts) and generating summary boxplots (e.g., Age and Het_Count)

**Het_Count** is the number of heterozygous variant sites (`0/1`, `1/0`, `1|0`, `0|1`) per sample passing the thresholds (`DP > 20` and `GQ ≥ 30`)

### Project structure
Recommended: create a parent directory to store cloned repository and input data.
```
new_project_directory/
├─ gvcf-filter/             # cloned repo
│  ├─ filter_variants.py    # main script
│  ├─ gvcf_utils.py         # functions for gVCF loading + processing
│  ├─ viz.py                # visualization functions
│  └─ requirements.txt      # dependencies
└─ technical_test/          # input data directory
```

## Requirements
### Input directory structure
The working directory passed to the script must contain one or more cohort folders with prefix `Cohort_`. 
```
technical_test/
├─ Cohort_A/
│  ├─ metadata.tsv
│  └─ <SampleID>.gvcf.gz
└─ Cohort_B/
   ├─ metadata.tsv
   └─ <SampleID>.gvcf.gz
```

### Input assumptions
+ Each sample file is named `<SampleID>.gvcf.gz` where `SampleID` matches the `SampleID` column in metadata.tsv
+ The implementation currently supports only `FORMAT=GT:AD:DP:GQ` and assumes the sample field values follow the same order

### Programming
- Python 3.10+ required
- Dependencies are listed in `requirements.txt`

## How to run

### Step 1: Clone repository
Repository should be cloned under `new_project_directory/` (see above project structure)
```
git clone https://github.com/rnade046/gvcf-filter.git
cd gvcf-filter
````

### Step 2: Set up virtual environment
```
python3 -m venv .gcvfenv            # create environment
source .gcvfenv/bin/activate        # activate environment
pip install -r requirements.txt     # install required libraries
```

### Step 3: Run pipeline
```
python filter_variants.py --wd /path/to/technical_test
```
The script automatically:
+ Detects cohort directories under `--wd` (directories starting with `Cohort_`)
+ Generates a summary table (.parquet) and visualization (.pdf) under a new created `outputs/` directory for each cohort.

## Outputs
Example outputs for Cohort_A and Cohort_B are provided under the `outputs/` directory.

A typical output structure is shown below:
```
Cohort_A/
└─ outputs/
   ├─ Cohort_A_output.parquet   # output summary table
   └─ Cohort_A_boxplots.pdf     # boxplot visualization
```

## Report
The written response to the optimization, benchmarking and scaling question is available in the `report/` directory.

## Additional notes
- Cross-platform paths are handled using `pathlib`
- Total runtime is computed using `datetime`