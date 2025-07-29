from setuptools import setup, Extension, find_packages
from Cython.Build import cythonize
import numpy

extensions = [
    Extension(
        "marearts_anpr.marearts_anpr_d",
        ["marearts_anpr/marearts_anpr_d.pyx"],
        include_dirs=[numpy.get_include()],
        extra_compile_args=["-O3"],
        language="c++"
    ),
    Extension(
        "marearts_anpr.marearts_anpr_r",
        ["marearts_anpr/marearts_anpr_r.pyx"],
        include_dirs=[numpy.get_include()],
        extra_compile_args=["-O3"],
        language="c++"
    ),
    Extension(
        "marearts_anpr.marearts_protect",
        ["marearts_anpr/marearts_protect.pyx"],
        extra_compile_args=["-O3"],
        language="c++"
    ),
]

setup(
    name="marearts_anpr",
    packages=find_packages(),
    ext_modules=cythonize(extensions, compiler_directives={'language_level': "3"}),
    package_data={
        'marearts_anpr': ['*.so', '*.pyd'],
    },
    exclude_package_data={
        'marearts_anpr': ['*.pyx', '*.cpp', '*.c'],
    },
    zip_safe=False,
    install_requires=[
        'numpy==1.23.5',
        'opencv-python==4.10.0.84',
        'requests==2.32.3',
        'imageio==2.34.2',
        'pillow==10.4.0',
        'onnxruntime==1.18.1',
        'PyYAML==6.0.1',
        'dotmap==1.3.30',
        'marearts-crystal',
        'tqdm==4.66.4'
    ],
)