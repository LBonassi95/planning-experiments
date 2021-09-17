import os
from os import path
import sys
from constants import PLANNERS_FOLDER, ALREADY_REGISTERED, SOURCE_FOLDER, PLANNER_REGISTERED


def main(args):
    planners_to_register = args[1:]
    if len(planners_to_register) > 0:
        for planner in planners_to_register:
            planner_home = os.path.join(PLANNERS_FOLDER, planner)
            if os.path.isdir(planner_home):
                print(ALREADY_REGISTERED.format(planner_name=planner))
            else:
                os.makedirs(path.join(planner_home, SOURCE_FOLDER))
                os.system('touch {}'.format(os.path.join(planner_home, 'cfg_map.json')))
                print(PLANNER_REGISTERED.format(planner_name=planner))
    else:
        print('No planner to register!')


if __name__ == '__main__':
    main(sys.argv)
