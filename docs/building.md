---
nav_order: 2
---

# Building the add-on

## Grabbing dependencies

The add-on depends on Embree, Intel Threading Building Blocks and pybind11. The first two are already dependencies
of Blender itself and can be grabbed from Blender's 3rd party repository server. There's a predefined script to download
them. Since they are stored on a subversion server, the `svn` command needs to be available in the system's path:

```bash
python scripts/download_blender_dependencies.py <blender-version>
```

This will install precompiled libraries in `build/dependencies`

pybind11 is a header only library and can be fetched by updating the repository's submodules

```bash
git submodules update --init
```

## Compiling

The add-on will be compiled through python's setup-tools. To ensure the right python version, the dependencies
download script also downloads the right python version from blender's subversion server. However there's no unified
structure on the python framework. Depending on the platform and Blender version, the path to the interpreter changes
a bit:

|      | Windows                                     | Linux                                    |
|------|---------------------------------------------|------------------------------------------|
| 2.92 | build/dependencies/python/37/bin/python.exe | build/dependencies/python/bin/python3.7m |
| 2.93 | build/dependencies/python/39/bin/python.exe | build/dependencies/python/bin/python3.9  |

Now this command will build the add-on

```bash
<python-path-to-interpreter> setup.py build --build-lib=build/out/
```

The C++ code will be compiles (assuming the system has a C++ compiler installed) and the python sources are being copied
together with the native module into `build/out/painticle`. It's possible to load the add-on from this location,
e.g. by specifying this directory in the visual studio blender add-on. This is predefined in the project settings and
should work out of the box.

Alternatively there's a Visual Studio Code tasks definition file in the repository, which can be used after specifying
a suitable python interpreter as the common python path to the application.

## Packaging

To create an installable zip, use the deploy script and pass in the source directory and a target zip file:

```bash
scripts/deploy.sh -s build/out/painticle -t PAINTicle.zip
```

The deployment script not only bundles the add-on and license information into the zip, but also creates a version
information file `deployment-version.txt`, which is used to show the add-on version in blender's preferences dialog.