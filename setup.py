import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="keeplerite",
    version="0.1",
    author="Irmak Akdogan",
    author_email="irmak.akdogan@yale.edu",
    description="A package for retrieving TPF, lightcurves and periodograms from lightkurve",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["keeplerite","keeplerite/astronomyobject"],
    install_requires=["numpy","lightkurve","matplotlib"]
)
