import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="spin-and-heave",
    version="3.2.0",
    author="Andy Klier, Gus Clemens",
    author_email="andyklier@gmail.com",
    description="package and zip lambdas then run terraform.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/shindagger/spin-and-heave",
    license="MIT",
    packages = ['spinandheave', 'spinandheave.scripts'],
    include_package_data=True,
    install_requires= ['setuptools'],
    entry_points = {
        'console_scripts': ['spin-and-heave=spinandheave.main:main'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
