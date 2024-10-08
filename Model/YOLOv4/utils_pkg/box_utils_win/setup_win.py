# # --------------------------------------------------------
# # Fast R-CNN
# # Copyright (c) 2015 Microsoft
# # Licensed under The MIT License [see LICENSE for details]
# # Written by Ross Girshick
# # --------------------------------------------------------
#
# import os
# from os.path import join as pjoin
# from setuptools import setup
# from distutils.extension import Extension
# from Cython.Distutils import build_ext
# import subprocess
# import numpy as np
#
#
# def find_in_path(name, path):
#     "Find a file in a search path"
#     # Adapted fom
#     # http://code.activestate.com/recipes/52224-find-a-file-given-a-search-path/
#     for dir in path.split(os.pathsep):
#         binpath = pjoin(dir, name)
#         if os.path.exists(binpath):
#             return os.path.abspath(binpath)
#     return None
#
#
# def locate_cuda():
#     """Locate the CUDA environment on the system
#
#     Returns a dict with keys 'home', 'nvcc', 'include', and 'lib64'
#     and values giving the absolute path to each directory.
#
#     Starts by looking for the CUDAHOME env variable. If not found, everything
#     is based on finding 'nvcc' in the PATH.
#     """
#
#     # first check if the CUDAHOME env variable is in use
#     if 'CUDAHOME' in os.environ:
#         home = os.environ['CUDAHOME']
#         nvcc = pjoin(home, 'bin')
#     else:
#         # otherwise, search the PATH for NVCC
#         nvcc = find_in_path('nvcc.exe', os.environ['PATH'])
#         if nvcc is None:
#             raise EnvironmentError('The nvcc binary could not be '
#                                    'located in your $PATH. Either add it to your path, or set $CUDAHOME')
#         home = os.path.dirname(os.path.dirname(nvcc))
#
#     cudaconfig = {'home': home, 'nvcc': nvcc,
#                   'include': pjoin(home, 'include'),
#                   'lib64': pjoin(home, 'lib', 'x64')}
#     for k, v in iter(cudaconfig.items()):
#         if not os.path.exists(v):
#             raise EnvironmentError('The CUDA %s path could not be located in %s' % (k, v))
#
#     return cudaconfig
#
#
# CUDA = locate_cuda()
#
#
# # Obtain the numpy include directory.  This logic works across numpy versions.
# try:
#     numpy_include = np.get_include()
# except AttributeError:
#     numpy_include = np.get_numpy_include()
#
#
# def customize_compiler_for_nvcc(self):
#     """inject deep into distutils to customize how the dispatch
#     to gcc/nvcc works.
#
#     If you subclass UnixCCompiler, it's not trivial to get your subclass
#     injected in, and still have the right customizations (i.e.
#     distutils.sysconfig.customize_compiler) run on it. So instead of going
#     the OO route, I have this. Note, it's kindof like a wierd functional
#     subclassing going on."""
#
#     # tell the compiler it can processes .cu
#     self.src_extensions.append('.cu')
#
#     # save references to the default compiler_so and _comple methods
#     default_compiler_so = self.compiler_so
#     super = self._compile
#
#     # now redefine the _compile method. This gets executed for each
#     # object but distutils doesn't have the ability to change compilers
#     # based on source extension: we add it.
#     def _compile(obj, src, ext, cc_args, extra_postargs, pp_opts):
#         if os.path.splitext(src)[1] == '.cu':
#             # use the cuda for .cu files
#             self.set_executable('compiler_so', CUDA['nvcc'])
#             # use only a subset of the extra_postargs, which are 1-1 translated
#             # from the extra_compile_args in the Extension class
#             postargs = extra_postargs['nvcc']
#         else:
#             postargs = extra_postargs['gcc']
#
#         super(obj, src, ext, cc_args, postargs, pp_opts)
#         # reset the default compiler_so, which we might have changed for cuda
#         self.compiler_so = default_compiler_so
#
#     # inject our redefined _compile method into the class
#     self._compile = _compile
#
#
# # run the customize_compiler
# class custom_build_ext(build_ext):
#     def build_extensions(self):
#         customize_compiler_for_nvcc(self.compiler)
#         build_ext.build_extensions(self)
#
#
# ext_modules = [
#     Extension('rbbox_overlaps',
#               ['rbbox_overlaps_kernel.cu', 'rbbox_overlaps.pyx'],
#               library_dirs=[CUDA['lib64']],
#               libraries=['cudart'],
#               language='c++',
#               #runtime_library_dirs=[CUDA['lib64']],
#               # this syntax is specific to this build system
#               # we're only going to use certain compiler args with nvcc and not with
#               # gcc the implementation of this trick is in customize_compiler() below
#               extra_compile_args={'gcc': ["-Wno-unused-function"],
#                                   'nvcc': ['-arch=sm_35',
#                                            '--ptxas-options=-v',
#                                            '-c',
#                                            '--compiler-options',
#                                            "'-fPIC'"]},
#               include_dirs=[numpy_include, CUDA['include']]
#               ),
#     Extension('rotate_polygon_nms',
#         ['rotate_polygon_nms_kernel.cu', 'rotate_polygon_nms.pyx'],
#         library_dirs=[CUDA['lib64']],
#         libraries=['cudart'],
#         language='c++',
#         #runtime_library_dirs=[CUDA['lib64']],
#         # this syntax is specific to this build system
#         # we're only going to use certain compiler args with nvcc and not with
#         # gcc the implementation of this trick is in customize_compiler() below
#         extra_compile_args={'gcc': ["-Wno-unused-function"],
#                             'nvcc': ['-arch=sm_35',
#                                      '--ptxas-options=-v',
#                                      '-c',
#                                      '--compiler-options',
#                                      "'-fPIC'"]},
#         include_dirs=[numpy_include, CUDA['include']]
#     ),
#     Extension('iou_cpu',
#               ['iou_cpu.pyx'],
#               library_dirs=[CUDA['lib64']],
#               libraries=['cudart'],
#               language='c++',
#               #runtime_library_dirs=[CUDA['lib64']],
#               # this syntax is specific to this build system
#               # we're only going to use certain compiler args with nvcc and not with
#               # gcc the implementation of this trick is in customize_compiler() below
#               extra_compile_args={'gcc': ["-Wno-unused-function"],
#                                   'nvcc': ['-arch=sm_35',
#                                            '--ptxas-options=-v',
#                                            '-c',
#                                            '--compiler-options',
#                                            "'-fPIC'"]},
#               include_dirs=[numpy_include, CUDA['include']])
# ]
#
# setup(
#     name='fast_rcnn',
#     ext_modules=ext_modules,
#     # inject our custom trigger
#     cmdclass={'build_ext': custom_build_ext},
# )

# --------------------------------------------------------
# Fast R-CNN
# Copyright (c) 2015 Microsoft
# Licensed under The MIT License [see LICENSE for details]
# Written by Ross Girshick
# --------------------------------------------------------

import os
from os.path import join as pjoin
import numpy as np
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

def find_in_path(name,path):
    "Find a file in a search path"
    #adapted fom http://code.activestate.com/recipes/52224-find-a-file-given-a-search-path/
    for dir in path.split(os.pathsep):
        binpath = pjoin(dir, name)
        if os.path.exists(binpath):
            return os.path.abspath(binpath)
    return None

def locate_cuda():
    """Locate the CUDA environment on the system

    Returns a dict with keys 'home', 'nvcc', 'include', and 'lib64'
    and values giving the absolute path to each directory.

    Starts by looking for the CUDAHOME env variable. If not found, everything
    is based on finding 'nvcc' in the PATH.
    """

    # first check if the CUDAHOME env variable is in use
    if 'CUDAHOME' in os.environ:
        home = os.environ['CUDAHOME']
        nvcc = pjoin(home, 'bin')
    else:
        # otherwise, search the PATH for NVCC
        nvcc = find_in_path('nvcc.exe', os.environ['PATH'])
        if nvcc is None:
            raise EnvironmentError('The nvcc binary could not be '
                'located in your $PATH. Either add it to your path, or set $CUDAHOME')
        home = os.path.dirname(os.path.dirname(nvcc))

    cudaconfig = {'home':home, 'nvcc':nvcc,
                  'include': pjoin(home, 'include'),
                  'lib64': pjoin(home, 'lib', 'x64')}
    for k, v in iter(cudaconfig.items()):
        if not os.path.exists(v):
            raise EnvironmentError('The CUDA %s path could not be located in %s' % (k, v))

    return cudaconfig
CUDA = locate_cuda()

# Obtain the numpy include directory.  This logic works across numpy versions.
try:
    numpy_include = np.get_include()
except AttributeError:
    numpy_include = np.get_numpy_include()

def customize_compiler_for_nvcc(self):
    # _msvccompiler.py imports:
    import os
    import shutil
    import stat
    import subprocess
    import winreg

    from distutils.errors import DistutilsExecError, DistutilsPlatformError, \
                                 CompileError, LibError, LinkError
    from distutils.ccompiler import CCompiler, gen_lib_options
    from distutils import log
    from distutils.util import get_platform

    from itertools import count

    super = self.compile
    self.src_extensions.append('.cu')
    # find python include
    import sys
    py_dir = sys.executable.replace('\\', '/').split('/')[:-1]
    py_include = pjoin('/'.join(py_dir), 'include')

    # override method in _msvccompiler.py, starts from line 340
    def compile(sources,
                output_dir=None, macros=None, include_dirs=None, debug=0,
                extra_preargs=None, extra_postargs=None, depends=None):

        if not self.initialized:
            self.initialize()
        compile_info = self._setup_compile(output_dir, macros, include_dirs,
                                           sources, depends, extra_postargs)
        macros, objects, extra_postargs, pp_opts, build = compile_info

        compile_opts = extra_preargs or []
        compile_opts.append('/c')
        if debug:
            compile_opts.extend(self.compile_options_debug)
        else:
            compile_opts.extend(self.compile_options)

        add_cpp_opts = False

        for obj in objects:
            try:
                src, ext = build[obj]
            except KeyError:
                continue
            if debug:
                # pass the full pathname to MSVC in debug mode,
                # this allows the debugger to find the source file
                # without asking the user to browse for it
                src = os.path.abspath(src)

            if ext in self._c_extensions:
                input_opt = "/Tc" + src
            elif ext in self._cpp_extensions:
                input_opt = "/Tp" + src
                add_cpp_opts = True
            elif ext in self._rc_extensions:
                # compile .RC to .RES file
                input_opt = src
                output_opt = "/fo" + obj
                try:
                    self.spawn([self.rc] + pp_opts + [output_opt, input_opt])
                except DistutilsExecError as msg:
                    raise CompileError(msg)
                continue
            elif ext in self._mc_extensions:
                # Compile .MC to .RC file to .RES file.
                #   * '-h dir' specifies the directory for the
                #     generated include file
                #   * '-r dir' specifies the target directory of the
                #     generated RC file and the binary message resource
                #     it includes
                #
                # For now (since there are no options to change this),
                # we use the source-directory for the include file and
                # the build directory for the RC file and message
                # resources. This works at least for win32all.
                h_dir = os.path.dirname(src)
                rc_dir = os.path.dirname(obj)
                try:
                    # first compile .MC to .RC and .H file
                    self.spawn([self.mc, '-h', h_dir, '-r', rc_dir, src])
                    base, _ = os.path.splitext(os.path.basename(src))
                    rc_file = os.path.join(rc_dir, base + '.rc')
                    # then compile .RC to .RES file
                    self.spawn([self.rc, "/fo" + obj, rc_file])

                except DistutilsExecError as msg:
                    raise CompileError(msg)
                continue
            elif ext == '.cu':
                # a trigger for cu compile
                try:
                    # use the cuda for .cu files
                    # self.set_executable('compiler_so', CUDA['nvcc'])
                    # use only a subset of the extra_postargs, which are 1-1 translated
                    # from the extra_compile_args in the Extension class
                    postargs = extra_postargs['nvcc']
                    arg = [CUDA['nvcc']] + sources + ['-odir', output_dir]
                    #arg = [CUDA['nvcc']] + sources + ['-odir', pjoin(output_dir,'nms')]
                    #arg = [CUDA['nvcc']] + sources
                    for include_dir in include_dirs:
                        arg.append('-I')
                        arg.append(include_dir)
                    arg += ['-I', py_include]
                    # arg += ['-lib', CUDA['lib64']]
                    arg += ['-Xcompiler', '/EHsc,/W3,/nologo,/Ox,/MT']
                    arg += postargs
                    self.spawn(arg)
                    continue
                except DistutilsExecError as msg:
                    # raise CompileError(msg)
                    continue
            else:
                # how to handle this file?
                raise CompileError("Don't know how to compile {} to {}"
                                   .format(src, obj))

            args = [self.cc] + compile_opts + pp_opts
            if add_cpp_opts:
                args.append('/EHsc')
            args.append(input_opt)
            args.append("/Fo" + obj)
            args.extend(extra_postargs)

            try:
                self.spawn(args)
            except DistutilsExecError as msg:
                raise CompileError(msg)

        return objects

    self.compile = compile

# run the customize_compiler
class custom_build_ext(build_ext):
    def build_extensions(self):
        customize_compiler_for_nvcc(self.compiler)
        build_ext.build_extensions(self)

ext_modules = [
    Extension('rbbox_overlaps',
              ['rbbox_overlaps_kernel.cu','rbbox_overlaps.pyx'],
              #['nms/rbbox_overlaps_kernel.cu','rbbox_overlaps.pyx'],
              library_dirs=[CUDA['lib64']],
              libraries=['cudart'],
              language='c++',
              #runtime_library_dirs=[CUDA['lib64']],
              # this syntax is specific to this build system
              # we're only going to use certain compiler args with nvcc and not with
              # gcc the implementation of this trick is in customize_compiler() below
              extra_compile_args={'gcc': ["-Wno-unused-function"],
                                  'nvcc': ['-arch=sm_52',
                                           '--ptxas-options=-v',
                                           '-c']},
              include_dirs=[numpy_include, CUDA['include']]
              ),
    Extension('rotate_polygon_nms',
        ['rotate_polygon_nms_kernel.cu','rotate_polygon_nms.pyx'],
        #['nms/rotate_polygon_nms_kernel.cu','rotate_polygon_nms.pyx'],
        library_dirs=[CUDA['lib64']],
        libraries=['cudart'],
        language='c++',
        #runtime_library_dirs=[CUDA['lib64']],
        # this syntax is specific to this build system
        # we're only going to use certain compiler args with nvcc and not with
        # gcc the implementation of this trick is in customize_compiler() below
        extra_compile_args={'gcc': ["-Wno-unused-function"],
                            'nvcc': ['-arch=sm_52',
                                     '--ptxas-options=-v',
                                     '-c']},
        include_dirs=[numpy_include, CUDA['include']]
    ),
    
    #Extension('iou_cpu',
    #          ['iou_cpu.pyx'],
    #          library_dirs=[CUDA['lib64']],
    #          libraries=['cudart'],
    #          language='c++',
    #          #runtime_library_dirs=[CUDA['lib64']],
    #          # this syntax is specific to this build system
    #          # we're only going to use certain compiler args with nvcc and not with
    #          # gcc the implementation of this trick is in customize_compiler() below
    #          extra_compile_args={'gcc': ["-Wno-unused-function"],
    #                              'nvcc': ['-arch=sm_52',
    #                                       '--ptxas-options=-v',
    #                                       '-c']},
    #          include_dirs=[numpy_include, CUDA['include']])
    
]

setup(
    name='tf_faster_rcnn',
    ext_modules=ext_modules,
    # inject our custom trigger
    cmdclass={'build_ext': custom_build_ext},
)

