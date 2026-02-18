# gVCF-filter — Variant Filtering and Het Count Summary

### Project description
Given a working directory containing one or more cohort folders, this pipeline processes each cohort by:

1. Loading cohort metadata
2. Locating and reading the corresponding gzipped gVCF file (`<SampleID>.gvcf.gz`) for each `SampleID` listed in the metadata
3. Extracting genotype QC fields (`GT`, `DP`, `GQ`) from the record format
4. Filtering records using genotype and QC thresholds, then counts the number of sites that pass the filter per sample.
5. Writing a cohort-level `.parquet` summary (metadata + per-sample counts) and generating summary boxplots (e.g., Age and Het_Count)

**Het_Count** is the number of heterozygous variant sites (0/1, 1/0, 1|0, 0|1) per sample passing the thresholds (DP > 20 and GQ ≥ 30)

### Project structure
Recommended: create a new parent directory to store cloned repository and input data.
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
### Input data directory structure
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

### Input files / assumptions
+ Each sample file is named `<SampleID>.gvcf.gz` where `SampleID` matches the `SampleID` column in metadata.tsv
+ The implementation currently supports only `FORMAT=GT:AD:DP:GQ` and assumes the sample field values follow the same order

### Programming
- Python 3.10+ recommended
- Dependencies are listed in `requirements.txt`

## How to run

### Step 1: clone repository
Repository should be cloned under `new_project_directory/` (see above project structure)
```
git clone https://github.com/rnade046/gvcf-filter.git
cd gvcf-filter
````

### Step 2: set up virtual environment
```
python -m venv .gcvfenv             # create environment
source .gcvfenv/bin/activate        # activate environment
pip install -r requirements.txt     # install required libraries
```

### Step 3: run pipeline
```
python filter_variants.py --wd /path/to/technical_test
```
The script automatically finds cohort directories under --wd (directories starting with `Cohort_`) and generates a summary table (.parquet) and visualization (.pdf) under a new created `outputs/` directory for eqach cohort.

### Outputs
```
Cohort_A/
└─ outputs/
   ├─ Cohort_A_output.parquet
   └─ Cohort_A_boxplots.pdf
```

## Additional notes
- Cross-platform paths are handled using `pathlib`
- (in future) add runtime per sample and peak RAM reporting.
- (in future) move hard-coded parameters (thresholds, file names) into a config file.