from setuptools import setup, find_packages
import pathlib

# বর্তমান ডিরেক্টরি (প্রজেক্ট রুট)
here = pathlib.Path(__file__).parent.resolve()

# README.md ফাইল থেকে long description পড়া
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="hanifx",
    version="7.0.1",
    author="Hanif",
    author_email="sajim4653@gmail.com",  # তোমার ইমেইল দিতে পারো (যদি থাকে)
    description="Advanced Color Testing and Utilities Module",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hanifx/hanifx",  # তোমার প্রকল্পের url (যদি থাকে)
    packages=find_packages(where="."),  # "hanifx" প্যাকেজ অটো ফাইন্ড করবে
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.7',
    include_package_data=True,
    keywords="color testing utilities hex rgb python module",
    project_urls={
        "Bug Tracker": "https://github.com/hanifx/hanifx/issues",
        "Source": "https://github.com/hanifx/hanifx",
        "Facebook Profile": "https://facebook.com/hanifx540",
        "Facebook Page": "https://facebook.com/pyhanifx",
    },
)
