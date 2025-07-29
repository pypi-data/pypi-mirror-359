from setuptools import setup

setup(
    name="ehk",
    version="1.2.0",
    author="Eren",
    author_email="senin.email@example.com",
    description="Türkçe temel matematik modülü",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    py_modules=["ehk"],
    url="https://pynet.neocities.org",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
