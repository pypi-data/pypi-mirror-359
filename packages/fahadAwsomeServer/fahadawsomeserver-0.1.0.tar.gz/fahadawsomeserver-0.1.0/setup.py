from setuptools import setup, find_packages
setup(
   name='fahadAwsomeServer', # This is the package name pip installs (must be unique on PyPI)
   version='0.1.0',
   packages=find_packages(),
   install_requires=["mcp","mcp[cli]"],
   entry_points={
       # This creates an executable script in the user's Python environment
       # that directly runs your FastMCP server.
       'console_scripts': [
           'fahadtestserver=fahadservermodule.server:main',
       ],
   },
   author='Fahad Khan',
   author_email='k.fahad1@tcs.com',
   description='A custom Model Context Protocol server developed in Python.',
   long_description=open('README.md').read(),
   long_description_content_type='text/markdown',
   # Link to your repo
   classifiers=[
       'Programming Language :: Python :: 3',
       'License :: OSI Approved :: MIT License',
       'Operating System :: OS Independent',
   ],
   python_requires='>=3.10',
)