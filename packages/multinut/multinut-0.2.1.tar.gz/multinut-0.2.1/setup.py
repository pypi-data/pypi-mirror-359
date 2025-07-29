from setuptools import setup, find_packages

setup(
    name='multinut',
    version='0.2.1',
    packages=find_packages(),
    install_requires=["dotenv"],
    author='Chipperfluff',
    author_email='i96774080@gmail.com',
    description='A completely unnecessary multitool module.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ChipperFluff/multinut',
    classifiers=[
        'Programming Language :: Python :: 3'
    ],
    python_requires='>=3.6',
)
