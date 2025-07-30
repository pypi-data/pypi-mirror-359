from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="lazyedabf",
    version="1.0.3",
    description="A package for EDA on CSV, Parquet.",
    author="nicolas_conde_brainfood",
    packages=find_packages(),
    install_requires=[
        "pandas==2.2.2",
        "polars==1.10.0",
        "XlsxWriter==3.2.0",
        "pyarrow==17.0.0",
        "tqdm"
    ],
    python_requires=">=3.7",
    long_description=long_description,
    long_description_content_type="text/markdown",
)

