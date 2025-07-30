from setuptools import setup, find_packages

setup(
    name="win2utc",
    version="0.2.0",
    description="Convert Windows timezone datetimes to UTC (with DST support)",
    author="Andrew Babu Augustine",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "backports.zoneinfo; python_version<'3.9'",
    ],
    package_data={"win2utc": ["data/*"]},
    python_requires='>=3.6',
    entry_points={
        "console_scripts": [
            "win2utc=win2utc.cli:main"
        ]
    },
)
