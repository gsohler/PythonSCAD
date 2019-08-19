from distutils.core import setup, Extension

setup(name = "mycsg", version = "1.0",
  ext_modules = [
    Extension("mycsg", ["mycsg.c"])
    ]
)
