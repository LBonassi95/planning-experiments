from planning_experiments.constants import PDDL_EXTENSION, DOMAIN_STR_CONST, DOMAIN_INSTANCES_ERROR
from pathlib import Path


def get_pddl_files(directory):
    path = Path(directory)
    pddl_files = list(path.rglob(f'*{PDDL_EXTENSION}'))  # Recursively find all .pddl files
    return pddl_files

def _is_domain(file: str):
    return PDDL_EXTENSION in file and DOMAIN_STR_CONST in file

def _is_instance(file: str):
    return PDDL_EXTENSION in file and DOMAIN_STR_CONST not in file

class InstancesCollector:
    def __init__(self, is_domain=_is_domain, is_instance=_is_instance) -> None:
        self.is_domain = is_domain
        self.is_instance = is_instance

    def collect_instances(self, instances_path):

        pddl_domains = []
        pddl_instances = []
        for file in get_pddl_files(instances_path):
            if self.is_domain(file.name):
                pddl_domains.append(file)
            elif self.is_instance(file.name):
                pddl_instances.append(file)

        if len(pddl_domains) != 1 and len(pddl_domains) != len(pddl_instances):
            raise Exception(DOMAIN_INSTANCES_ERROR)
        
        pddl_instances.sort(key=lambda x: x.name)
        pddl_domains.sort(key=lambda x: x.name)
        pairs = []
        for i in range(len(pddl_instances)):
            if len(pddl_domains) == 1:
                pairs.append((pddl_domains[0], pddl_instances[i]))
            else:
                # assert '-' in pddl_domains[i] or '_' in pddl_domains[i]
                # if '-' in pddl_domains[i]:
                #     sep = '-'
                # elif '_' in pddl_domains[i]:
                #     sep = '_'
                # else:
                #     assert False, 'ABORTING!'
                # test_soundness = pddl_domains[i].split(sep)[1]
                # #assert test_soundness == pddl_instances[i]
                pairs.append((pddl_domains[i], pddl_instances[i]))
        return pairs

class Domain:
    def __init__(self, name: str, path2pddl: str, instances_collector: InstancesCollector = None) -> None:
        self.name = name
        self.path = path2pddl
        if instances_collector is None:
            instances_collector = InstancesCollector()
        self.instances = instances_collector.collect_instances(self.path)
    
    def __repr__(self) -> str:
        return self.name