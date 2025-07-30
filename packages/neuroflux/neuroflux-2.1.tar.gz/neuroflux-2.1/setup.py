from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()


setup(
    name="neuroflux",
    version="2.1",
    description="MRI Brain Tumor Diagnosis and Grad-CAM Visualization",
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Neuroflux-AI/neuroflux",
    install_requires=[
        "numpy",
        "nibabel",
        "opencv-python",
        "tensorflow>=2.0",
        "matplotlib"
    ],
)