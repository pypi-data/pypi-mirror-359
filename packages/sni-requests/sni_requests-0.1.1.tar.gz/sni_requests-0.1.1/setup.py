from setuptools import setup

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

setup(
    name='sni_requests',
    version='0.1.1',
    description='A requests wrapper that allows setting a custom SNI hostname for HTTPS connections',
    long_description=readme,
    long_description_content_type="text/markdown",
    author='hacked_by_zen',
    url='https://github.com/42zen/sni_requests',
    packages=['sni_requests'],
    package_dir={'sni_requests': '.'},
    py_modules=['sni_requests'],
    install_requires=[
        'requests',
        'urllib3',
    ]
)