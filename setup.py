import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='lilliput',
    version='0.0.1',
    author='Niv Baehr (BLooperZ)',
    description='Declarative binary structure definitions for Python.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/blooperz/lilliput',
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3',
        'Environment :: Console',
        'OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
    ],
    python_requires='>=3.7',
    keywords='binary struct pack unpack typedef bytes header'
)
