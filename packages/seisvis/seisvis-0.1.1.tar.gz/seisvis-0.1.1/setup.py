from setuptools import setup, find_packages

setup(
    name='seisvis',
    version='0.1.1',
    description='Seismic data visualization and plotting utilities',
    author='Qi Pang',
    author_email='pangjiutian@gmail.com',
    packages=find_packages(),  
    install_requires=[
        'numpy',
        'matplotlib',
        'scipy',
    ],
    python_requires='>=3.6',
    include_package_data=True,
    package_data={
        'seisvis.opendtect_colormaps': ['ColTabs/*'],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)