from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='lakkavokka',
    version='0.1.0',
    description='Command-line JOSM plugin for digitizing indexed colors images',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/Aneurosm/lakkavokka',
    author='Miroff',
    author_email='mr.miroff@gmail.com',
    license='MIT',
    packages=['lakkavokka'],
    scripts=['bin/lakkavokka'],
    python_requires=">=3.8",
    install_requires=[
        'shapely',
        'opencv-python',
        'scipy',
        'pyproj',
        'numpy',
        'beautifulsoup4',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Plugins',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.8',
        'Topic :: Scientific/Engineering :: GIS'
    ],
)
