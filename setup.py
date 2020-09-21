from setuptools import setup, find_packages

setup(
    # Project information
    name="fitbit-data",
    version="1.0.0",
    author="Matt Kaye",
    author_email="mrkaye97@gmail.com",
    url="https://github.com/mrkaye97/fitbit-data",  # 404, just an example
    license="MIT license",

    # Description
    description="Fitbit data pull and save.",

    # Requirements
    python_requires='>=3.6',
    install_requires=[
        "fitbit==0.3.1",
        "pandas==0.23.3",
        "numpy==1.18.1",
        "sqlalchemy==1.3.11"],

    # Packaging
    packages=find_packages(include=["fitbit-data", "fitbit-data.*"]),
    include_package_data=True,
    zip_safe=False,


    # Metadata
    keywords="string strings accent beautify",
    project_urls={
        'Documentation': 'https://github.com/mrkaye97/fitbit-data',
        'Tracker': 'https://github.com/mrkaye97/fitbit-data/issues',
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)