from setuptools import setup, find_packages

setup(
    name='testah995q',
    version='0.1.0',
    description='Capture terminal output and send to Telegram',
    author='YourName',
    author_email='you@example.com',
    packages=find_packages(),
    install_requires=[
        'requests'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License'
    ],
    python_requires='>=3.6',
)