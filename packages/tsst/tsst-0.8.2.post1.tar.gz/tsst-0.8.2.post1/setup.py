from setuptools import setup, find_packages

setup(
    name="tsst",
    version="0.8.2.post1",
    description="TSST is an integration platform for Taiwan brokerage Python APIs, enabling quick switching between different brokerage APIs using a unified trading logic.",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)