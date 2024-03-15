# Planning Experiments

Planning Experiments is a library designed for conducting planning experiments and collecting data!

With this library, users can input a planning problem in a specific format. Tasks are represented by instances and tools. The input should be a JSON file that explains how the parameters are utilized. The JSON file should include the following information:

- The runs that need to be performed and the corresponding tasks to execute.
- The execution time for the schedule.
- The parameters required for the various runs.

The tool will run all instances concurrently using multiprocess. The output consists of collected data produced during the execution of tasks. The output data are stored in a single file, such as CSV or JSON, representing the results (log files organized to be user-friendly).

The library contains different files that perform various operations:

- **__init__.py:** Initialization file.
- **constants.py:** Defines constants used in the program.
- **launch_experiments.py:** Runs the experiments provided as input.
- **libraries.py:** Installs the libraries needed for execution.
- **save_result.py:** A script that defines how to save the results and performs this operation.
- **script_builder.py:** Produces the script to run the experiments and defines the class `scriptBuilder`.
- **summary.py:** Functions that produce results and create the output as a summary.
- **utils.py:** A script that manages folders and scripts.

Within this project, there is a folder named `examples` that demonstrates how to use the tool with examples of planning experiments.

## Installation

If you haven't installed pip, run the following commands:

```bash
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py
```

To install the library, run the following commands:

```bash
git clone https://github.com/LBonassi95/planning-experiments
cd planning-experiments
pip3 install .
```

## Usage

Explore the `examples/` folder for usage demonstrations!