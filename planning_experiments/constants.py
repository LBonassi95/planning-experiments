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
COLLECT_DATA_FOLDER = 'collect_data'