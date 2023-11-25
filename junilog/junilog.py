"""Provide tool to parse junifer logs and provide main info as DataFrame."""


from pathlib import Path
import argparse
import re
import numpy as np
import pandas as pd


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Parse and sum up junifer logs."
    )
    parser.add_argument(
        "jobs_directory",
        type=Path,
        help="Directory to a junifer pipeline directory.",
    )
    return parser.parse_args()


def element_indices_from_filename(filename):
    """Get the element from the filename."""
    element_str = Path(filename.name).stem.replace("junifer_run_", "")
    return element_str.split("_")


def match_log_file_content(log_file_content):
    """Match log file using regex to extract ressources used."""
    patterns = {
        "job_terminated": r"Job terminated.\n\s+\((\d+)\) Normal termination \(return value (\d+)\)",
        "CPUs": r"Cpus\s+:\s+([\d.]+)",
        "disk_in_kb": r"Disk \(KB\)\s+:\s+([\d.]+)",
        "memory_in_mb": r"Memory \(MB\)\s+:\s+([\d.]+)",
        "run_remote_usage_usr": r"Usr (?:\d+) (\d{2}:\d{2}:\d{2}), [^<>]*Run Remote Usage",
        "run_remote_usage_sys": r"Sys (?:\d+) (\d{2}:\d{2}:\d{2}) [^<>]*Run Remote Usage",
        "run_local_usage_usr": r"Run Remote Usage[^<>]*Usr (?:\d+) (\d{2}:\d{2}:\d{2}), [^<>]*Run Local Usage",
        "run_local_usage_sys": r"Run Remote Usage[^<>]*Sys (?:\d+) (\d{2}:\d{2}:\d{2}) [^<>]*Run Local Usage",
        "total_remote_usage_usr": r"Run Local Usage[^<>]*Usr (?:\d+) (\d{2}:\d{2}:\d{2}), [^<>]*Total Remote Usage",
        "total_remote_usage_sys": r"Run Local Usage[^<>]*Sys (?:\d+) (\d{2}:\d{2}:\d{2}) [^<>]*Total Remote Usage",
        "total_local_usage_usr": r"Total Remote Usage[^<>]*Usr (?:\d+) (\d{2}:\d{2}:\d{2}), [^<>]*Total Local Usage",
        "total_local_usage_sys": r"Total Remote Usage[^<>]*Sys (?:\d+) (\d{2}:\d{2}:\d{2}) [^<>]*Total Local Usage",
    }

    log_file_dict = {field: np.nan for field in patterns}

    for field, pattern in patterns.items():
        match = re.search(pattern, log_file_content)
        if match:
            log_file_dict[field] = [match.group(1)]

    return pd.DataFrame(log_file_dict)


def main():
    """Run main program."""
    args = parse_args()
    log_dir = args.jobs_directory / "logs"
    elements = log_dir.glob("*.out")
    for file_name_out in elements:
        element_indices = element_indices_from_filename(file_name_out)
        file_name_log = file_name_out.with_suffix(".log")
        file_name_err = file_name_out.with_suffix(".err")

        with open(file_name_log, "r") as f_log:
            log_file_content = f_log.read()
            log_content_df = match_log_file_content(log_file_content)
            log_content_df.index = pd.MultiIndex.from_tuples(
                [tuple(element_indices)]
            )
            print(log_content_df)

        with open(file_name_out, "r") as f_out:
            out_file_content = f_out.read()
            # print(out_file_content)
