import os
import sys
from constants import PLANNERS_FOLDER, ALREADY_REGISTERED, PLANNER_SOURCE_FOLDER, PLANNER_NOT_FOUND, PLANNER_REGISTERED, COLLECT_DATA_FOLDER


def main(args):
    planners_to_register = args[1:]
    if len(planners_to_register) > 0:
        for planner_path_raw in planners_to_register:
            planner_path = planner_path_raw
            planner_name = os.path.basename(planner_path)
            if not os.path.isdir(planner_path):
                print(PLANNER_NOT_FOUND.format(planner_name=planner_name))
            else:
                planner_home = os.path.join(PLANNERS_FOLDER, planner_name)
                if os.path.isdir(planner_home):
                    print(ALREADY_REGISTERED.format(planner_name=planner_name))
                else:
                    planner_dst = os.path.join(PLANNERS_FOLDER, planner_name, PLANNER_SOURCE_FOLDER)
                    os.mkdir(planner_home)
                    os.system('cp -r {} {}'.format(planner_path, planner_dst))
                    os.system('touch {}'.format(os.path.join(planner_home, 'cfg_map.json')))
                    os.system('touch {}'.format(os.path.join(COLLECT_DATA_FOLDER, 'collect_{}.py'.format(planner_name))))
                    print(PLANNER_REGISTERED.format(planner_name=planner_name))
    else:
        print('No planner to register!')


if __name__ == '__main__':
    main(sys.argv)
