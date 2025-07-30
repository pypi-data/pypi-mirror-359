from setuptools import setup, find_packages

setup(
    name='heybot',
    version='0.1.0',
    description='A simple command-line WhatsApp bot using pywhatkit',
    author='Haruki',
    author_email='haruki9159826376@gmail.com',
    packages=find_packages(),
    install_requires=[
        'pywhatkit'
    ],
    entry_points={
        'console_scripts': [
            'hey-bot = heybot.bot:run_bot'
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
