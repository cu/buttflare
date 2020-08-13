from setuptools import setup

setup(
    name='buttflare',
    version='0.1',
    packages=['buttflare'],
    python_requires='>=3.6',
    install_requires=[
        'requests'
    ],
    entry_points='''
        [console_scripts]
        buttflare=buttflare.buttflare:main
    '''
)
