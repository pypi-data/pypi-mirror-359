from setuptools import setup, find_packages

setup(
    name='yrwatertemperatures',
    version='0.9.7-beta',
    author='Jørn Pettersen',
    author_email='joern.pettersen@gmail.com',
    description='A Python client to fetch water temperatures in Norway from YR.no.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/jornpe/yr-norwegian-water-temperatures', # Replace with your repo URL
    packages=find_packages(),
    package_data={"yrwatertemperatures": ["py.typed"]},
    install_requires=[
        'requests>=2.20.0',
    ],
    extras_require={
        'test': [
            'pytest>=7.0.0',
            'pytest-asyncio>=0.21.0',
            'aioresponses>=0.7.4',
            'aiohttp>=3.8.0',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3 :: Only",
        "Typing :: Typed",
    ],
    python_requires='>=3.12',
    project_urls={
        'Bug Tracker': 'https://github.com/jornpe/yr-norwegian-water-temperatures/issues',
    },
)