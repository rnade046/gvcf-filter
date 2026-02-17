import pandas as pd
import matplotlib.pyplot as plt


def plot_het_count_age(samples: pd.DataFrame, cohort_name, output_path):
    """
    Generates boxplots for Age and Het_count from a summary dataframe
    :param samples: merged (dataframe) containing meta-data, cohort info and het_counts
    :param cohort_name: (String)
    :param output_path: (Path) for output visualizations .pdf
    :return:
    """

    # plot layout
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(10, 5))

    # Age boxplot
    axes[0].boxplot(samples["Age"])
    axes[0].set_title("Age Summary")
    axes[0].set_ylabel("Age")
    axes[0].set_xticks([1])
    axes[0].set_xticklabels([cohort_name])

    # Het_count boxplot
    axes[1].boxplot(samples["Het_Count"])
    axes[1].set_title("Heterogeneous Count")
    axes[1].set_ylabel("Count")
    axes[1].set_xticks([1])
    axes[1].set_xticklabels([cohort_name])

    plt.tight_layout()
    fig.savefig(output_path)  # generate output pdf
    plt.close(fig)
