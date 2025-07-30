from setuptools import setup, find_packages

setup(
    name='wgen',
    version='4.7.9',
    author='lucasliu71',
    author_email='Lucasliu71@126.com',
    description='Wordlist generator for password brute force cracking using CPUs',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://gitee.com/lucasliu71/wgen',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'psutil>=7.0.0',
        'rich>=14.0.0',
        'setuptools>=79.0.1'
    ],
    entry_points={
        'console_scripts': [
            'wgen=wgen.wgen:main',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Topic :: Security',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Systems Administration',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
    ],
    keywords='wordlist generator password brute force security penetration testing',
    python_requires='>=3.7',
    zip_safe=False
)
