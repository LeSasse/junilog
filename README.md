
Junilog is a small command line utility to collect and aggregate logging information
from [junifer](https://juaml.github.io/junifer/main/index.html) pipelines into 
convenient DataFrames. This DataFrame contains information about ressources used
(CPUs, time elapsed, memory, disk space used ...), warnings, job success etc. Each
row corresponds to a junifer 'element'. For now, it is assumed that logs are
from [HTCondor](https://htcondor.org/) as no other queueing backends are implemented in junifer.

# Install:

Best to set up a virtual environment, for example:

```
python3 -m venv junilogvenv
source junilogvenv/bin/activate
```

Then install it from GitHub:

```
pip install git+https://github.com/LeSasse/junilog.git
```

# Usage

## Get some example logs
Try out the tool in your own junifer pipeline. Alternatively you can use the example
provided in this repository if you have not run a junifer pipeline yet.

```
git clone https://github.com/LeSasse/junilog.git --recurse-submodules
cd junilog/example/aomic-fc/code/junifer_jobs
```

You can then either get the log files using [datalad](https://www.datalad.org/):
```
datalad get PREPROCESS_PIOP1
```
or directly using [git annex](https://git-annex.branchable.com/):
```
git annex get PREPROCESS_PIOP1
```

## Run `junilog`

To get the aggregate DataFrame containing element-wise logging info, run
`junilog` on the directory with your junifer job. In the provided example, run:

```
junilog PREPROCESS_PIOP1 -o element_logs.csv
```
This will create a `csv` with the aggregated logging information. You can
also use the `--ipython` flag, if you have [ipython](https://ipython.org/)
installed. This will start an IPython session with the DataFrame in memory, so you
can start meddling with it straight away.

## Demonstration:

![Gif Demonstrating Usage](https://github.com/LeSasse/junilog/blob/master/example/demonstration.gif)
