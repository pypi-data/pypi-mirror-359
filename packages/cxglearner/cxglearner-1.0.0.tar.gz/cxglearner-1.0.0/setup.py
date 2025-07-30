import os
import sys
import shutil
import logging
from setuptools import setup, find_packages, Extension
from setuptools.command.sdist import sdist
from Cython.Build import cythonize
import numpy as np

# 设置详细日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 验证关键文件是否存在
REQUIRED_FILES = [
    "cxglearner/tools/patternpiece/ac_matcher.pyx",
    "cxglearner/tools/mdlgraph/mdl_ds.pyx",
    "cxglearner/tools/mdlgraph/atomic_operations.c"
]

for file in REQUIRED_FILES:
    if not os.path.exists(file):
        logger.error(f"Missing required file: {file}")
        logger.error(f"Current working directory: {os.getcwd()}")
        logger.error(f"Directory contents: {os.listdir('.')}")
        sys.exit(1)


# 清理构建产物
class CleanSdist(sdist):
    def run(self):
        # 记录清理前状态
        logger.info("Running CleanSdist...")
        logger.info(f"Current directory: {os.getcwd()}")

        # 清理路径列表
        clean_paths = [
            'cxglearner/tools/patternpiece/ac_matcher.cpp',
            'cxglearner/tools/mdlgraph/mdl_ds.c',
            'cxglearner.egg-info',
            'build',
            'dist'
        ]

        for path in clean_paths:
            if os.path.exists(path):
                logger.info(f"Removing: {path}")
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)

        # 验证源文件存在
        for file in REQUIRED_FILES:
            if not os.path.exists(file):
                logger.error(f"File missing after cleaning: {file}")
                sys.exit(1)

        super().run()


# 编译器配置
compiler_directives = {
    'boundscheck': False,
    'wraparound': False,
    'profile': True,
    'linetrace': True,
}


# 使用绝对路径确保可靠性
def abs_path(path):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), path))


extensions = [
    Extension("cxglearner.tools.patternpiece.ac_matcher",
              sources=[abs_path("cxglearner/tools/patternpiece/ac_matcher.pyx")],
              extra_compile_args=["-fopenmp"],
              extra_link_args=["-fopenmp"]),
    Extension("cxglearner.tools.mdlgraph.mdl_ds",
              sources=[
                  abs_path("cxglearner/tools/mdlgraph/mdl_ds.pyx"),
                  abs_path("cxglearner/tools/mdlgraph/atomic_operations.c")
              ],
              extra_compile_args=["-fopenmp"],
              extra_link_args=["-fopenmp"])
]

# 记录扩展模块详细信息
logger.info("Building extensions:")
for ext in extensions:
    logger.info(f"Module: {ext.name}")
    for source in ext.sources:
        logger.info(f"  Source: {source}")
        if not os.path.exists(source):
            logger.error(f"Source file does not exist: {source}")

setup(
    name="cxglearner",
    version="1.0.0",
    packages=find_packages(),
    package_dir={'': '.'},
    ext_modules=cythonize(extensions, compiler_directives=compiler_directives),
    include_dirs=[np.get_include()],
    include_package_data=True,
    package_data={
        'cxglearner': ['*.py'],
        'cxglearner.tools': ['*.py'],
        'cxglearner.tools.patternpiece': ['*.pyx'],
        'cxglearner.tools.mdlgraph': ['*.pyx', '*.c'],
    },
    cmdclass={'sdist': CleanSdist},
    setup_requires=[
        'cython>=3.0.0',
        'numpy>=1.21.0',
        'setuptools>=62.1.0'
    ],
    install_requires=[
        'numpy>=1.21.0'
    ]
)