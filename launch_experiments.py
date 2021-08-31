import sys
import json

NAME = "NAME"
PATH_TO_DOMAINS = "PATH_TO_DOMAINS"
PATH_TO_RESULTS = "PATH_TO_RESULTS"
PLANNERS_X_DOMAINS = "PLANNERS_X_DOMAINS"
COMPILER = "COMPILER"
DOMAINS = "DOMAINS"


def main(args):
    cfg = args[1]
    cfg_dict = json.load(open(cfg,))
    name = cfg_dict[NAME]
    path_to_domains = cfg_dict[PATH_TO_DOMAINS]
    path_to_results = cfg_dict[PATH_TO_RESULTS]
    planners_x_domains = cfg_dict[PLANNERS_X_DOMAINS]
    #For now i ignore the "COMPILER" field
    print(name)


if __name__ == '__main__':
    main(sys.argv)


import os.path as path

#This is the template for the configuration of an experiment
#The following fields are required!


#PATH_TO_DOMAINS = 'path to the folder with the domains' #TODO absolute?
#PATH_TO_RESULTS = 'path to the folder with the results' #TODO absolute?

#NAME = 'a meaningful name for the experiment'

# [(compiler, [list of planners], [list of domains]), ([], []), ...]
# Up to one appearance of every planner
#PLANNERS_X_DOMAINS = [('compiler1', ['planner1', 'planner2'], ['domain1', 'domain2', 'domain3']),
#                      (None, ['planner3'], ['domain3', 'domain4', 'domain5'])]

