from setuptools import setup, Extension
from Cython.Build import cythonize
import shutil
import os
import subprocess
from distutils.sysconfig import get_config_vars
import glob

modules = [
        "semiauto_main.py",
        "semiauto_misc.py",
        "semiauto_ps.py",
        "semiauto_rc.py",
        "__init__.py",
]


# Convert .py to .pyx
pyx_modules = []
for py_file in modules:
    if py_file == "__init__.py":
        continue
    pyx_file = py_file.replace('.py', '.pyx')
    shutil.copyfile(py_file, pyx_file)
    pyx_modules.append(pyx_file)

# Compiler directives
compiler_directives = {
    'language_level': "3",
    'boundscheck': False,
    'wraparound': False,
    'cdivision': True,
    'infer_types': True,
    'nonecheck': False,
    'initializedcheck': False
}

try:
    # Remove debug flags
    for flag in ['OPT', 'CFLAGS']:
        (opt,) = get_config_vars(flag)
        if opt:
            os.environ[flag] = opt.replace('/Zi', '')

    # Compile with Cython
    extensions = [
        Extension(
            pyx_file.replace('.pyx', ''),
            [pyx_file],
            extra_compile_args=["/O2"],
        )
        for pyx_file in pyx_modules
    ]

    setup(
        name='snapshot_integration_package',
        ext_modules=cythonize(
            extensions,
            compiler_directives=compiler_directives
        ),
        zip_safe=False,
    )

    # Strip debug symbols (Windows-specific adjustment)
    for pyx_file in pyx_modules:
        pyd_file = pyx_file.replace('.pyx', '.pyd')
        if os.path.exists(pyd_file):
            try:
                subprocess.run(['llvm-strip', pyd_file], check=True)
            except FileNotFoundError:
                print(f"Skipping strip for {pyd_file}: llvm-strip not found.")


finally:
    # Cleanup
    for pyx_file in pyx_modules:
        # Remove .c files
        c_file = pyx_file.replace('.pyx', '.c')
        if os.path.exists(c_file):
            os.remove(c_file)
        
        # Remove .pyx files
        if os.path.exists(pyx_file):
            os.remove(pyx_file)
        
        # Remove .pyd files
        pyd_file = pyx_file.replace('.pyx', '.pyd')
        if os.path.exists(pyd_file):
            os.remove(pyd_file)
        
        # Remove all .pyd files in the current directory
        for pyd_file in glob.glob("*.pyd"):
            os.remove(pyd_file)