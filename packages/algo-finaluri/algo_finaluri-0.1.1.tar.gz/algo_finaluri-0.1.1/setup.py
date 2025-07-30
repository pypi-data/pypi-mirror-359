from setuptools import setup, find_packages

setup(
    name='algo_finaluri',
    version='0.1.1',  # <--- MUST bump version every upload
    packages=find_packages(),
    include_package_data=True,
    package_data={'': ['*']},  # Wildcard for everything (text, md, etc.)
    description='Ghmerti ar gagvwiravs',
    author='Bakuri Tchelidze',
    author_email='bakuritchelidze@btu.com',
    python_requires='>=3.6',
)
