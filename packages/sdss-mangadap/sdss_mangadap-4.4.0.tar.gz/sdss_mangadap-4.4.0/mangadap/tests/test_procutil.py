import os
from IPython import embed

from mangadap.proc import util
from mangadap.config import defaults


def test_database_key():
    assert util.get_database_key('junk') == 'JUNK'
    assert util.get_database_key('test.par') == 'TEST'
    assert util.get_database_key('/path/to/test.par') == 'TEST' 


def test_select_database():
    d = defaults.dap_data_root() / 'emission_lines'
    assert os.path.split(util.select_database('ELPMPL11', d))[1] == 'elpmpl11.par'

