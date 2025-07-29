# alpaka-job-matrix-library
A library to provide a job generator for CI's for alpaka based projects.

The library provides everything needed to generate a sparse combination matrix for alpaca-based projects, including a set of general-purpose combination rules.

The provision of the input parameters, the reordering of the jobs, the filtering of the job matrix and the generation of the job yaml are project specific. Therefore, the library provides an example of how most parts can be implemented.

# Installation

Install via pip:

```bash
pip install alpaka-job-coverage
```

See [pypi.org](https://pypi.org/project/alpaka-job-coverage/)

# Usage

The main function of the library is `create_job_list()`. It takes a list of parameters, creates the combinations, applies the combination rules, thins them and returns the sparse job matrix.

The thinning is done according to the principle [all-pairs testing](https://en.wikipedia.org/wiki/All-pairs_testing). The principle means that every combination of the values of at least two parameters must be part of a job, unless a filter rule forbids this. The `pair_size` parameter of the `create_job_list()` function decides how large the combination tuple must be. For example, if we have the parameter fields `A, B, C` and `D` and pair size 2, each combination of the values of `AB, AC, AD, BC, BD and CD` must be part of a job. If the parameter is 3, any combination of the values of `ABC, ABD and BCD` must be part of a job. Normally, a larger pairwise factor increases the calculation time and the number of orders.

The general form of the parameter matrix is an `OrderedDict` of `List[Tuples[str, str]]`. The first value of a tuple is the name of the software and the second value is the version. An exception is the parameter field `BACKENDS`. `BACKENDS` is a `list[list[tuple[str, str]]`. The inner list contains a combination of alpaka backends. This can be a complete combination matrix of all backends (the inner list contains n entries), or it can be only one backend (size of the inner list is 1), as required for [cupla](https://github.com/alpaka-group/cupla). A mixture of both is also possible, e.g. `[(ALPAKA_ACC_CPU_B_SEQ_T_SEQ_ENABLE, ON), (ALPAKA_ACC_CPU_B_OMP2_T_SEQ_ENABLE, ON), (ALPAKA_ACC_CPU_B_SEQ_T_OMP2_ENABLE, ON)],[(ALPAKA_ACC_GPU_CUDA_ENABLE, "11. 0")],[(ALPAKA_ACC_GPU_CUDA_ENABLE, "11.0")] ...]`.

In order to apply the filter rules correctly, it is necessary to use the variables defined in `alpaka_job_coverage.global`.

There are 3 parameters with special meaning:
* `HOST_COMPILER`: Compiler for the host code, or if there is no host device code separation, the compiler for all the code.
* `DEVICE_COMPILER`: Compiler for the device code, or if there is no host device code separation, the compiler is the same as the host compiler.
* `BACKENDS`: See description above.

If one of these 3 parameter fields is missing, it is not guaranteed that the generator will provide correct results. All other parameter fields provided by the `alpaka_job_coverage.global` are optional.

## Adding own parameter and rules

If you want to use a project-specific parameter, you can simply add it to the parameter list and the library will apply it. To limit the possible combinations of your new parameter, you need to add a new filter function. The `create_job_list()` function applies a chain of filter functions to each possible combination. Before and after each filter function is a function hook where you can insert your own filter function. The order is described in the doc string of `create_job_list()`. When you create a new filter rule, you must comply with the following rules:

* The filter returns `True` if a combination is valid and `False` if not. All filters in the library follow the rule that every combination is valid until it is forbidden (blacklist).
* The input of the filter is a combination of the values of the individual parameter fields, and the combination does not have to be complete. The list can contain at least 2 parameter fields up to all. You must check whether a parameter field is included in the current combination.
* If a parameter field is not included in the current combination, it means that it can contain any possible value of this parameter. In practice, this means that if you only check for the presence of the parameter and return `False`, if the parameter is not present, no combination is possible.

# ajc-validate

`ajc-validate` is a tool which is installed together with the `alpaka-job-coverage` library. The tool allows to check whether a combination of parameters passes the different filters and displays the reason if not.

![ajc-validate example](docs/images/ajc-validator-example.png)

**Hint:** The source code of the tool is located in the file [validate.py](src/alpaka_job_coverage/validate.py).

# Developing

It is strongly recommended to use a Python environment for developing the code, such as `virtualenv` or a `conda` environment. The following code uses a `virtualenv`.

1. Create the environment: `virtualenv -p python3 env`
2. Activate the environment: `source env/bin/activate`
3. Install the library: `python setup.py develop`
4. Test the installation with the example: `python3 example/example.py 3.0`
5. You can run the unit tests by going to the `test` directory and running `python -m unittest`

If the example works correctly, a `job.yml` will be created in the current directory. You can also run `python3 example/example.py --help` to see additional options.

Now the library is available in the environment. Therefore you can easily use the library in your own projects via `import alpaka_job_coverage as ajc`.

## Formatting the source code

The source code is formatted using the [black](https://pypi.org/project/black/) formatter and the default style guide. You must install it and run `black /path/to/file` to format a file. A CI job checks that all files are formatted correctly. If the job fails, a PR cannot be merged.

## Contribution

This section contains some hints for developing new functions. The hints are mainly for people who have no experience with `setuptools` and building `pip` packages.

* The `python setup.py develop` command installs the source code files as a symbolic link. This means that changes in the source code of the Python files in the `src/alpaka_job_coverage` folder are directly available without any additional installation step (only a restart of the Python process/interpreter is required).
* The software requirements are defined in `setup.py` and not in an additional `requirements.txt`.
* It is necessary to increase the version number in `version.txt` before a new feature can be merged in the master branch. Otherwise the upload to pypy.org will fail because existing versions cannot be changed.
