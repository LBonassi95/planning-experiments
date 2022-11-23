from planning_experiments.data_processor import LogsParser
import pytest

def test_log_parser():
    path1 = '/home/studenti/lbonassi/coding/PPLTL_CLASSICAL/RESULTS/results/EXPERIMENTS/RUN_FF_OT2022-11-21_10:38:48'
    df = LogsParser(path=path1).logs2df()


if __name__ == '__main__':
    pytest.main()