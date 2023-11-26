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
        "job_directory",
        type=Path,
        help="Directory to a junifer pipeline directory.",
    )
    parser.add_argument(
        "--outfile",
        "-o",
        help="Path to outfile.",
        type=Path,
        default=Path("junilog.csv"),
    )
    parser.add_argument(
        "--ipython",
        "-i",
        help=(
            "Jump into IPython session to work "
            "with the DataFrame straightaway.",
        ),
        action="store_true",
    )
    return parser.parse_args()


def element_indices_from_filename(filename):
    """Get the element from the filename."""
    element_str = Path(filename.name).stem.replace("junifer_run_", "")
    return element_str.split("_")


def match_log_file_content(log_file_content):
    """Match log file using regex to extract ressources used."""
    patterns = {
        "job_terminated": r"Job terminated.\n\s+\((\d+)\)",
        "return_value": r"Normal termination \(return value (\d+)\)",
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
        match = re.findall(pattern, log_file_content)
        if match:
            # consider only last match from .log file
            log_file_dict[field] = [match[-1]]

    return pd.DataFrame(log_file_dict)


def extract_lib_versions(log_data):
    """Extract library version information from *.out files."""
    # Define the regular expression pattern
    # to extract library versions within the specified markers
    pattern = r"(?<====== Lib Versions =====\n)((?:.*\n)*?)(?<========================\n)"

    # Find the match within the log data
    match = re.search(pattern, log_data)

    lib_section = match.group(1) if match else ""

    # Define the pattern to extract library names and versions within the section
    lib_pattern = r"(?P<lib_name>\S+):\s(?P<lib_version>\S+)"

    # Find all matches in the library section
    lib_matches = re.findall(lib_pattern, lib_section)

    # Create a dictionary from the matches
    return {lib_name: [lib_version] for lib_name, lib_version in lib_matches}


def extract_errors(out_file_content):
    """Extract errors from log file using regex."""
    # collect a list of all errors
    error_pattern = (
        r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} - JUNIFER - ERROR - .+"
    )

    # Find all matches for errors in the log data
    return re.findall(error_pattern, out_file_content)


def match_out_file_content(out_file_content):
    """Extract info from *.out files using regex."""
    out_file_dict = extract_lib_versions(out_file_content)

    # collect a list of all warnings
    warning_pattern = (
        r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} - JUNIFER - WARNING - (.+)"
    )

    # Find all matches for warnings in the log data
    warnings = re.findall(warning_pattern, out_file_content)
    warnings = list(set(warnings))
    warnings_str = "\n".join(warnings)

    # extract error matches
    errors = extract_errors(out_file_content)
    errors_str = "\n".join(list(set(errors)))
    out_file_dict["warnings"] = [warnings_str]
    out_file_dict["errors_out_file"] = [errors_str]

    return out_file_dict


def main():
    """Run main program."""
    args = parse_args()
    log_dir = args.job_directory / "logs"
    elements = log_dir.glob("*.out")
    element_df_list = []
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

        with open(file_name_out, "r") as f_out:
            out_file_content = f_out.read()
            out_file_dict = match_out_file_content(out_file_content)

        with open(file_name_err, "r") as f_err:
            err_file_content = f_err.read()
            additional_errors = "".join(
                list(set(extract_errors(err_file_content)))
            )
            out_file_dict["errors_err_file"] = [additional_errors]

        out_file_df = pd.DataFrame(out_file_dict)
        out_file_df.index = pd.MultiIndex.from_tuples([tuple(element_indices)])
        element_df_list.append(
            pd.concat([log_content_df, out_file_df], axis=1)
        )

    out_df = pd.concat(element_df_list)

    exts = {".csv": ",", ".tsv": "\t"}
    ext = args.outfile.suffix
    sep = exts[ext]
    out_df.to_csv(args.outfile, sep=sep)

    if args.ipython:
        from IPython import embed

        print("The DataFrame is stored in the variable 'out_df'\n")
        print("You can access it for example as:")
        print("'print(out_df)'")
        embed()
