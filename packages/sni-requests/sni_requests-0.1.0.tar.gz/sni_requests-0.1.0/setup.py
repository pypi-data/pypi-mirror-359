from setuptools import setup

setup(
    name='sni_requests',
    version='0.1.0',
    description='A requests wrapper that allows setting a custom SNI hostname for HTTPS connections',
    long_description='A requests wrapper that allows setting a custom SNI hostname for HTTPS connections',
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