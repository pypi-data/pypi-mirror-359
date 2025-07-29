"""This module contains constances used in the alpaka job coverage framework.
"""

from typing import List, Dict

# index positions of the name version tuple, used in the paramer list
NAME: int = 0
VERSION: int = 1

# parameter key names, whit special meaning
HOST_COMPILER: str = "host_compiler"
DEVICE_COMPILER: str = "device_compiler"
BACKENDS: str = "backends"

# name of the used compilers
GCC: str = "gcc"
CLANG: str = "clang"
NVCC: str = "nvcc"
CLANG_CUDA: str = "clang-cuda"
HIPCC: str = "hipcc"
ICPX: str = "icpx"

# alpaka backend names
ALPAKA_ACC_CPU_B_SEQ_T_SEQ_ENABLE: str = "alpaka_ACC_CPU_B_SEQ_T_SEQ_ENABLE"
ALPAKA_ACC_CPU_B_SEQ_T_THREADS_ENABLE: str = "alpaka_ACC_CPU_B_SEQ_T_THREADS_ENABLE"
ALPAKA_ACC_CPU_B_SEQ_T_FIBERS_ENABLE: str = "alpaka_ACC_CPU_B_SEQ_T_FIBERS_ENABLE"
ALPAKA_ACC_CPU_B_TBB_T_SEQ_ENABLE: str = "alpaka_ACC_CPU_B_TBB_T_SEQ_ENABLE"
ALPAKA_ACC_CPU_B_OMP2_T_SEQ_ENABLE: str = "alpaka_ACC_CPU_B_OMP2_T_SEQ_ENABLE"
ALPAKA_ACC_CPU_B_SEQ_T_OMP2_ENABLE: str = "alpaka_ACC_CPU_B_SEQ_T_OMP2_ENABLE"
ALPAKA_ACC_ANY_BT_OMP5_ENABLE: str = "alpaka_ACC_ANY_BT_OMP5_ENABLE"
ALPAKA_ACC_GPU_CUDA_ENABLE: str = "alpaka_ACC_GPU_CUDA_ENABLE"
ALPAKA_ACC_GPU_HIP_ENABLE: str = "alpaka_ACC_GPU_HIP_ENABLE"
ALPAKA_ACC_SYCL_ENABLE: str = "alpaka_ACC_SYCL_ENABLE"
BACKENDS_LIST: List[str] = [
    ALPAKA_ACC_CPU_B_SEQ_T_SEQ_ENABLE,
    ALPAKA_ACC_CPU_B_SEQ_T_THREADS_ENABLE,
    ALPAKA_ACC_CPU_B_SEQ_T_FIBERS_ENABLE,
    ALPAKA_ACC_CPU_B_TBB_T_SEQ_ENABLE,
    ALPAKA_ACC_CPU_B_OMP2_T_SEQ_ENABLE,
    ALPAKA_ACC_CPU_B_SEQ_T_OMP2_ENABLE,
    ALPAKA_ACC_ANY_BT_OMP5_ENABLE,
    ALPAKA_ACC_GPU_CUDA_ENABLE,
    ALPAKA_ACC_GPU_HIP_ENABLE,
    ALPAKA_ACC_SYCL_ENABLE,
]

# if want to use version comparison functions from util.py, you need to use ON_VER and OFF_VER
ON: str = "on"
OFF: str = "off"

# backend states
ON_VER: str = "1.0.0"
OFF_VER: str = "0.0.0"

# additional parameters, like alpaka software dependencies, compiler configurations and so one
UBUNTU: str = "ubuntu"
CMAKE: str = "cmake"
BOOST: str = "boost"
CXX_STANDARD: str = "cxx_standard"

# Is required because allpairspy uses a List for each row. The ordering of the entries in a row
# is the same, like the order of the keys of the parameters dict. To make the filter function
# independent of the number and ordering of the entries in parameters, the param_map is
# required.
#
# the map is filled up by the main_functions.create_job_list() function
param_map: Dict[str, int] = {}
