from setuptools import setup, find_packages

setup(
    name='nestorix',  # Replace with your final chosen name
    version='1.0.1',
    description='Nestorix: A proprietary Python toolkit for deeply nested data manipulation and analysis.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Ayush Agrawal',
    author_email='youremail@example.com',  # Replace with your email
    url='https://github.com/yourusername/nestorix',  # Replace with your repo
    license='Proprietary',
    packages=find_packages(),
    py_modules=['ayushlist', 'glaze'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Topic :: Software Development :: Libraries',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'License :: Other/Proprietary License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    keywords=[
        'nested-data', 'tree-structure', 'linked-list', 'data-structure',
        'educational-data', 'data-manipulation', 'python-tools', 'dstruct',
        'data-analysis', 'curriculum-parser', 'matrix-conversion', 'glaze',
        'ayushlist', 'nestorix'
    ],
    python_requires='>=3.7',
    include_package_data=True,
    install_requires=[
        'numpy',
        'pandas'
    ],
)
