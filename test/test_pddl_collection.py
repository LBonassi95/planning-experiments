from planning_experiments.data_structures import *
from planning_experiments.launch_experiments import Executor
from pathlib import Path
import pkg_resources

PDDL_PATH = Path(__file__).parent /  "pddl"

def test_pddl_collection():

    blocksworld = Domain('blocksworld', PDDL_PATH / 'blocksworld')
    rovers = Domain('rovers', PDDL_PATH / 'rovers')
    rovers_alt = Domain('rovers_alt', PDDL_PATH / 'rovers_alt')
    print(PDDL_PATH / 'rovers')
    assert len(blocksworld.instances)  == 2
    assert len(rovers.instances)  == 3
    assert len(rovers_alt.instances)  == 3


if __name__ == "__main__":
    test_pddl_collection()
