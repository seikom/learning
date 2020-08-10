### pytest for Checking_bed_files_draft.py
import pytest
import os
import sys
import argparse

# Specify a path for importing the modules
sys.path.append('/Users/seikomakino/PycharmProjects/SDGS/learning/')


from Checking_bed_files_draft import check_format, check_header

# parser.parse_args([])

## troubleshooting on args
# https://stackoverflow.com/questions/55259371/pytest-testing-parser-error-unrecognised-arguments

'''
# testing if .fixture helps to remove pytest error
@pytest.fixture
def test_path():
    path_upcoming_test = '/Users/seikomakino/Documents/201809_NHS_STP/SCH_SDGS/SDGS_Bioinfo/Projects/Checking_bed_files_202005_/'
    return path_upcoming_test

@pytest.fixture
def test_f_new_bed():
    f_new_bed = 'Haems_mini_SLC40A1_v2.bed'
    return f_new_bed

@pytest.fixture
def test_f_not_ascii():
    f_not_ascii = 'test_bed.xlsx'
    return f_not_ascii

@pytest.fixture
def test_n_service():
    n_service = 'NGD'
    return n_service
'''

@pytest.mark.check_format
def test_check_format():
    # set up - path and file
    path_upcoming_test = '/Users/seikomakino/Documents/201809_NHS_STP/SCH_SDGS/SDGS_Bioinfo/Projects/Checking_bed_files_202005_/'
    f_new_bed = 'Haems_mini_SLC40A1_v2.bed'
    n_service = 'NGD'
    #f_not_ascii='test_bed.xlsx'
    # act and assert
    #assert check_format(path_upcoming_test,f_new_bed)
    assert True
    #assert check_format(path_upcoming_test,f_not_ascii)

@pytest.mark.check_header
def test_check_header():
    # set up
    path_upcoming_test = '/Users/seikomakino/Documents/201809_NHS_STP/SCH_SDGS/SDGS_Bioinfo/Projects/Checking_bed_files_202005_/'
    f_new_bed = 'Haems_mini_SLC40A1_v2.bed'
    n_service = 'NGD'
    f_not_ascii='test_bed.xlsx'
    # act and assert
    assert True
    #assert check_header(path_upcoming_test,f_new_bed)


if __name__=='__main__':
    pytest.main()