from planning_experiments.data_processor import LogsParser
import pytest

def test_log_parser():
    path1 = '/home/studenti/lbonassi/coding/PPLTL_FOND/EXPERIMENTS/results/BIG_DOMAINS/RUN_rovers_big_formula_a2022-11-11_16:01:01.968140_2508402730755557113'
    df = LogsParser(path=path1).logs2df()


if __name__ == '__main__':
    pytest.main()