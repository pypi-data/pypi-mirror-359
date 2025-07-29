from setuptools import setup, find_packages

setup(
    name='cheesymamas',
    version='0.2.61',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'PyQt6>=6.0.0',
    ],
    entry_points={
        'console_scripts': [
            'cheesymamas=cheesymamas.main:main',
        ],
    },
    package_data={
        'cheesymamas': ['assets/CheesyMamas.png']
    },
    author='Luke Miller',
    description='A local-first code editor with cheesy Git goodness',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Environment :: X11 Applications :: Qt',
        'Intended Audience :: Developers',
    ],
)