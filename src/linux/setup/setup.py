from distutils.core import setup
# Use "Extension" from Cython.Distutils so that "cython_directives" works.
# from distutils.extension import Extension
from Cython.Distutils import build_ext, Extension
import sys
import platform
from Cython.Compiler import Options
import Cython

print("Cython version: %s" % Cython.__version__)

BITS = platform.architecture()[0]
assert (BITS == "32bit" or BITS == "64bit")

# Stop on first error, otherwise hundreds of errors appear in the console.
Options.fast_fail = True

# Python version string: "27" or "32".
PYTHON_VERSION = str(sys.version_info.major) + str(sys.version_info.minor)

def CompileTimeConstants():

    print("Generating: compile_time_constants.pxi")
    with open("./../../compile_time_constants.pxi", "w") as fd:
        fd.write('# This file was generated by setup.py\n')
        # A way around Python 3.2 bug: UNAME_SYSNAME is not set.
        fd.write('DEF UNAME_SYSNAME = "%s"\n' % platform.uname()[0])
        fd.write('DEF PY_MAJOR_VERSION = %s\n' % sys.version_info.major)

CompileTimeConstants()

ext_modules = [Extension(

    "cefpython_py%s" % PYTHON_VERSION,
    ["cefpython.pyx"],

    # Ignore the warning in the console:
    # > C:\Python27\lib\distutils\extension.py:133: UserWarning:
    # > Unknown Extension options: 'cython_directives' warnings.warn(msg)
    cython_directives={
        # Any conversion to unicode must be explicit using .decode().
        "c_string_type": "bytes",
        "c_string_encoding": "utf-8",
    },

    language='c++',
    include_dirs=[
        r'./../',
        r'./../../',
        r'./../../cython_includes/',
        '/usr/include/gtk-2.0',
        '/usr/include/glib-2.0',
        '/usr/include/gtk-unix-print-2.0',
        '/usr/include/cairo',
        '/usr/include/pango-1.0',
        '/usr/include/gdk-pixbuf-2.0',
        '/usr/include/atk-1.0',
        # Ubuntu
        '/usr/lib/x86_64-linux-gnu/gtk-2.0/include',
        '/usr/lib/x86_64-linux-gnu/gtk-unix-print-2.0',
        '/usr/lib/x86_64-linux-gnu/glib-2.0/include',
        '/usr/lib/i386-linux-gnu/gtk-2.0/include',
        '/usr/lib/i386-linux-gnu/gtk-unix-print-2.0',
        '/usr/lib/i386-linux-gnu/glib-2.0/include',
        # Fedora
        '/usr/lib64/gtk-2.0/include',
        '/usr/lib64/gtk-unix-print-2.0',
        '/usr/lib64/glib-2.0/include',
        '/usr/lib/gtk-2.0/include',
        '/usr/lib/gtk-2.0/gtk-unix-print-2.0',
        '/usr/lib/glib-2.0/include',
    ],

    # http_authentication not implemented on Linux.
    library_dirs=[
        r'./lib_%s' % BITS,
        r'./../../client_handler/',
        r'./../../subprocess/', # libcefpythonapp
        r'./../../cpp_utils/'
    ],

    # Static libraries only. Order is important, if library A depends on B,
    # then B must be included before A.
    libraries=[
        'X11',
        'gobject-2.0',
        'glib-2.0',
        'gtk-x11-2.0',
        # CEF and CEF Python libraries
        'cef_dll_wrapper',
        'cefpythonapp',
        'client_handler',
        'cpp_utils',
    ],

    # When you put "./" in here, loading of libcef.so will only work when
    # running scripts from the same directory that libcef.so resides in.
    # runtime_library_dirs=[
    #    './'
    #],

    # Fix "ImportError ... undefined symbol ..." caused by CEF's include/base/
    # headers by adding the -flto flag (Issue #230). Unfortunately -flto
    # prolongs compilation time significantly.
    # More on the other flags: https://stackoverflow.com/questions/6687630/
    extra_compile_args=['-flto', '-fdata-sections', '-ffunction-sections',
                        '-std=gnu++11'],
    extra_link_args=['-flto', '-Wl,--gc-sections'],

    # Defining macros:
    # define_macros = [("UNICODE","1"), ("_UNICODE","1"), ]
)]

setup(
    name = 'cefpython_py%s' % PYTHON_VERSION,
    cmdclass = {'build_ext': build_ext},
    ext_modules = ext_modules
)
