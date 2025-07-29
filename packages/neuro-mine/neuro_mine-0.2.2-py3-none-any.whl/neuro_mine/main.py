"""
Module for easy running of MINE on user data
"""

import utilities
from mine import Mine
import subprocess


def main():
    subprocess.run(["python", "/Users/danicamatovic/PycharmProjects/neuro_mine/neuro_mine/process_csv.py"])
