from setuptools import setup, find_packages

setup(
    name="roblox-dev-sync",
    version="1.0.0",
    description="Sync server between Roblox Studio and an external IDE",
    long_description="""A server that enables two-way file synchronization between Roblox Studio and an external IDE.
Allows you to edit Roblox files directly in your preferred IDE while maintaining a connection to Roblox Studio.""",
    author="Joaquín Stürtz",
    author_email="NetechAI@proton.me",
    url="https://github.com/janxhg/roblox-dev-sync",
    packages=find_packages(),
    python_requires='>=3.7',
    install_requires=[
        'Flask>=2.0.0',
        'Flask-Cors>=4.0.0',
        'watchdog>=2.1.0'
    ],
    entry_points={
        'console_scripts': [
            'roblox-sync=robloxidesync.sync:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
