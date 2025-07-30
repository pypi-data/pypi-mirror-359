from setuptools import setup, find_packages

setup(
    name="tglib",
    use_scm_version=True,
    packages=find_packages(),
    package_data={
        'tglib': ['*.so', '*.pyd'],
    },
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.10',
)
