from distutils.core import setup, Extension
import platform

_DEBUG = True

extra_compile_args = []
extra_link_args = []
if platform.system()=='Windows':
    if _DEBUG:
        extra_compile_args += ['-Od', '-Zi', '-UNDEBUG']
        extra_link_args += ['-debug']
    else:
        extra_compile_args += ['-DNDEBUG', '-Ox']
elif platform.system()=='Linux':
    if _DEBUG:
        extra_compile_args += ['-g']
    else:
        extra_compile_args += ['-DNDEBUG', '-O3']

native_module = Extension('particle_paint.native',
                          language="c++11",
                          extra_compile_args=extra_compile_args,
                          extra_link_args=extra_link_args,
                          sources = ['particle_paint/native/paint.cpp',
                                     'particle_paint/native/module.cpp'])

setup (name = 'particle_paint_native',
       version = '1.0',
       description = 'The native paint code for particle_paint',
       packages = ['particle_paint'],
       ext_modules = [native_module])