from distutils.core import setup, Extension

setup(name = "mycsg", version = "1.0",
  ext_modules = [
    Extension("mycsg", ["mycsg.c","bsp.c", "mesh.c", "poly.c","vector.c", "util.c","dbg.c","stl.c","export.c","reader.c","stl_mesh.c" ], extra_compile_args=["-Wno-sign-compare","-Wno-strict-prototypes"])
    ]
)
