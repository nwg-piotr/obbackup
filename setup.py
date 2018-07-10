from setuptools import setup

setup(
    name="obbackup",
    version="0.0.1",
    author="Piotr Miller",
    author_email="nwg.piotr@gmail.com",

    packages=["obbackup"],

    include_package_data=True,

    # Details
    url="https://github.com/nwg-piotr/obbackup",

    license='GPL3',
    description="Arcade-puzzle game",

    long_description=open("README.txt").read(),
    install_requires=[
          'python',
      ],
    platforms=['any'],
)