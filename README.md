
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

Try out the tool in your own junifer pipeline. Alternatively you can use the example
provided in this repository if you have not run a junifer pipeline yet.

```
git clone https://github.com/LeSasse/junilog.git --recurse-submodules
cd junilog/example/aomic-fc/code/junifer_jobs
