DOMAINS = "DOMAINS"
MEMORY = "MEMORY"
TIME = "TIME"
PRIORITY = "PRIORITY"
PPN = "PPN"
NO_VALIDATION_PERFORMED = 'N/A'

PDDL_EXTENSION = ".pddl"
DOMAIN_STR_CONST = "domain"

# Errors #####
DOMAIN_INSTANCES_ERROR = "ERROR! domain files and problem files don't match in number"
##############

PLANNER_COPIES_FOLDER = "PLANNERS_COPY"

RM_CMD = 'rm -r -f {}'

PPN_QSUB = '#PPN#'
PRIORITY_QSUB = '#PRIORITY#'
SCRIPT_QSUB = '#SCRIPT#'
LOG_QSUB = "#LOG#"
ERR_QSUB = "#ERR#"

QSUB_TEMPLATE  = "qsub -o #LOG# -e #ERR# -p #PRIORITY# -q longbatch -l "
QSUB_TEMPLATE += "nodes=minsky.ing.unibs.it:ppn=#PPN# "
QSUB_TEMPLATE += "#SCRIPT#"

EXPERIMENT_RUN_FOLDER = "RUN_{}"

PLANNERS_FOLDER = 'systems'
LOG_FOLDER = 'logs'
BIN_FOLDER = 'bin'


# Info dict keys
PLANNER_EXE = 'planner_exe'
DOMAIN_PATH = 'domain_path'
INSTANCE_PATH = 'instance_path'
SOLUTION_PATH = 'solution_path'
STDE = 'stde'
STDO = 'stdo'
VAL_DOMAIN_PATH = 'val_domain_path'
VAL_INSTANCE_PATH = 'val_instance_path'
VALIDATION = 'validation'

# DATA COLLECTION
RT = 'RT'
PL = 'PL'
EN = 'EN'
D = 'D'
SYS = 'SYS'
I = 'I'
SOL = 'SOL'
POL = 'POL'
UNSAT = 'UNSAT'
CT = 'CT'
DEFAULT_SOLUTION_FOUND_STRINGS = ['Strong cyclic plan found.', 'Policy successfully found.' , 'Solution found.', 'Plan found.', 'ff: found legal plan', 
                                  'Problem Solved', 'Solution Found']
UNSOLVABLE_STRINGS = ['Search stopped without finding a solution.', 'Completely explored state space -- no solution!', 'INITIAL IS UNPROVEN!', 'No solution']
SOLUTION_FOUND_STRINGS = 'solution_found_strings'