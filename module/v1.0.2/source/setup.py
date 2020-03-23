import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="py-loading-screen",
    version="1.0.2",
    author="a.s.akulov",
    author_email="a.c.akulov@mail.ru",
    description="Animated loading screen",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/a-s-akulov/py-loading-screen/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
    ],
    python_requires='>=3.0',
    install_requires=[
        'PyQt5>=5.8'
    ]
)