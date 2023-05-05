import os

import pytest

from ..powerQueriesPull_generic import *


def test_remove_old_tmp_files():
    remove_old_tmp_files()
    assert not os.path.exists("*.txt.tmp")
    assert not os.path.exists("*.txt.json")


@pytest.mark.skip
def test_get_opts_and_args():
    params = ["-f", "folder", "-s", "students", "-l", "debug"]
    options, args = get_opts_and_args(params)
    assert options.folder == "folder"
    assert options.single == "students"
    assert options.log_level == "debug"
    assert options.exclude == "NULL"
