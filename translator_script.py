"""
Script to Translate the HTML files present
"""

import glob
import math
import sys
import os
import time

from bs4 import BeautifulSoup
from englisttohindi.englisttohindi import EngtoHindi


def list_all_html_files(dir_name: str) -> list:
    """
    List all the HTML files
    :return:
    """
    _html_files = []
    os.chdir(dir_name)
    for file in glob.glob("*.html"):
        _html_files.append(file)
    return _html_files


def _group_html_for_multiprocess(_html_files: list, group_size: int = 512) -> list[list]:
    """
    Group the HTML files in a group of 512(MAX_PROCESSES
    :return:
    """
    _grouped_html_files = []
    for i in range(0, len(html_files), group_size):
        _grouped_html_files.append(html_files[i:i + group_size])
    return _grouped_html_files


def translate_and_write_html(_file_name: str) -> None:
    """
    Translate & write the given HTML file
    :return:
    """
    with open(_file_name, "r") as f:
        v = f.read()
    f.close()
    b = BeautifulSoup(v, "lxml")

    _i = 0
    tot = len(b.find_all())
    print(f"Len: {len(b.find_all())}")
    for b1 in b.find_all():
        _i += 1
        if b1.string and b1.name != "style" and b1.name != "script":
            sys.stdout.write('\r')
            percent_completed = math.ceil(100*_i/tot)
            sys.stdout.write("[%-100s] %d%%  -- (%d/%d)" %
                             ('=' * percent_completed, percent_completed, _i, tot))
            sys.stdout.flush()
            try:
                b1.string = EngtoHindi(b1.string).convert
            except Exception as _:
                _i = _i

    with open(_file_name, "w") as f:
        f.write(str(b.prettify()))
    f.close()


if __name__ == '__main__':

    # List the HTML Files
    html_files = list_all_html_files("www.classcentral.com/update-item")
    no_html_files = int(os.getenv("FILES_END_BATCH", len(html_files)))
    start_point = int(os.getenv("FILES_END_BATCH"))

    # Translating HTML one by one
    start_time = int(time.time())
    retry_cnt = 0
    for i in range(start_point, no_html_files):
        print(f"{i}/{no_html_files}: {html_files[i]}")
        try:
            translate_and_write_html(html_files[i])
            retry_cnt = 0
        except Exception as e:
            print(f"Retry count: {retry_cnt+1} for {html_files[i]} after waiting for 30 seconds...")
            if retry_cnt == 1:
                i -= 1
            if retry_cnt > 5:
                raise Exception(e)

    print(f"Done Translating with all files in {int(time.time()) - start_time} seconds.")
