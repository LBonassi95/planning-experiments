import os
from os import path
import sys
from constants import PLANNERS_FOLDER, ALREADY_REGISTERED, SOURCE_FOLDER, PLANNER_REGISTERED, COMPILER_MANAGER, COMPILER_MANAGER_TEMPLATE


def main(args):
    compilers_to_register = args[1:]
    if len(compilers_to_register) > 0:
        for compiler in compilers_to_register:
            compiler_home = os.path.join(PLANNERS_FOLDER, compiler)
            if os.path.isdir(compiler_home):
                print(ALREADY_REGISTERED.format(planner_name=compiler))
            else:
                os.makedirs(path.join(compiler_home, SOURCE_FOLDER))
                os.system('touch {}'.format(os.path.join(compiler_home, 'cfg_map.json')))
                with open(path.join(compiler_home, COMPILER_MANAGER), 'w') as cm:
                    cm.write(COMPILER_MANAGER_TEMPLATE)                    
                print(PLANNER_REGISTERED.format(planner_name=compiler))
    else:
        print('No compiler to register!')


if __name__ == '__main__':
    main(sys.argv)
