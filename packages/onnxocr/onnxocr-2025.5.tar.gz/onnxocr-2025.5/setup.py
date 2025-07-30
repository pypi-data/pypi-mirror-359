from setuptools import setup, find_packages

setup(
    name="onnxocr",
    version="2025.5.21",
    description="A lightweight OCR system based on PaddleOCR",
    author="jingsongliujing",
    author_email="45508593+jingsongliujing@users.noreply.github.com",
    url="https://github.com/jingsongliujing/OnnxOCR",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=[
        "opencv-python-headless",
        "opencv-contrib-python",
        "onnxruntime",
        "shapely",
        "pyclipper",
        "numpy<2.0.0",
        "pymupdf",
        "pdf2image",
    ],
    license="Apache-2.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
    ],
    include_package_data=True,
)
