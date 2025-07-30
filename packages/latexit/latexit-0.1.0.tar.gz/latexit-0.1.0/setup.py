from setuptools import setup, find_packages


setup(
    name='latexit',
    version='0.1.0',
    description='Render LaTeX code to PNG images with transparent background (no math mode required)',
    author='Furkan Tandogan',
    packages=find_packages(),
    install_requires=[
        'matplotlib',
        'Pillow',
    ],
    entry_points={
        'console_scripts': [
            'latexit=src.cli:main',
        ],
    },
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Operating System :: OS Independent',
    ],
    include_package_data=True,
    zip_safe=False,
) 