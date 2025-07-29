from setuptools import setup, find_packages

setup(
    name="snapshot_integration_package",
    version="1.0.7_dev",
    author="Varchas Solutions Pty Ltd",
    license="MIT",
    author_email="pritesh.patel@varchassolutions.com.au",
    description="This package is useful for PSS®E power system assessment.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url='https://',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'numpy>=1.26.4',
        'pandas>=2.2.2',
        'requests>=2.32.3',
        'openpyxl>=3.1.5',
    ],
    package_data={
        "snapshot_integration_package": ["EULA", "DISCLAIMER"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
        "License :: Other/Proprietary License",
    ],
    python_requires=">=3.9,<3.12",
)
