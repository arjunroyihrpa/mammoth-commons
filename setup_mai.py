import setuptools

# Developer self-reminder for uploading in pypi:
# - install: wheel, twine
# - build  : python setup.py bdist_wheel
# - build  : python setup_mai.py bdist_wheel
# - deploy : twine upload dist/*
# https://kynan.github.io/blog/2020/05/23/how-to-upload-your-package-to-the-python-package-index-pypi-test-server

with open("README.md", "r") as file:
    long_description = "This is the desktop version of the MAI-BIAS toolkit.\nFor more information visit the [homepage](https://github.com/mammoth-eu/mammoth-commons)."

setuptools.setup(
    name="MAI-Bias",
    version="0.1.17",
    author="Emmanouil (Manios) Krasanakis",
    author_email="maniospas@hotmail.com",
    description="Desktop app version of the MAI-Bias toolkit.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mammoth-eu/mammoth-commons",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["mammoth-commons[all]"],
)
