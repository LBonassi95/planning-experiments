import os
from planning_experiments.constants import PDDL_EXTENSION, DOMAIN_STR_CONST, DOMAIN_INSTANCES_ERROR
from typing import List, Tuple

def _is_domain(file: str) -> bool:
    """
    Determines if a given file is a domain file based on its extension and content.

    Args:
        file (str): The file name to check.

    Returns:
        bool: True if the file is a domain, False otherwise.
    """
    return PDDL_EXTENSION in file and DOMAIN_STR_CONST in file

def _is_instance(file: str) -> bool:
    """
    Determines if a given file is an instance file based on its extension and content.

    Args:
        file (str): The file name to check.

    Returns:
        bool: True if the file is an instance, False if it's a domain.
    """
    return PDDL_EXTENSION in file and DOMAIN_STR_CONST not in file

class InstancesCollector:
    """
    A class used to collect PDDL domain and instance files.

    This class separates domain files from instance files in a given directory and
    pairs them according to specific rules.

    Attributes
    ----------
    is_domain : function
        A function to determine if a file is a domain file.
    is_instance : function
        A function to determine if a file is an instance file.

    Methods
    -------
    collect_instances(instances_path: str) -> list
        Collects and pairs domain and instance files from the specified directory.
    """

    def __init__(self, is_domain=_is_domain, is_instance=_is_instance) -> None:
        """
        Constructs the necessary attributes for the InstancesCollector object.

        Args:
            is_domain (function, optional): A function to identify domain files. Defaults to _is_domain.
            is_instance (function, optional): A function to identify instance files. Defaults to _is_instance.
        """
        self.is_domain = is_domain
        self.is_instance = is_instance

    def collect_instances(self, instances_path: str) -> List[Tuple[str, str]]:
        """
        Collects and pairs PDDL domain and instance files from the given path.

        The function scans the specified directory for domain and instance files,
        pairs them according to predefined rules, and returns a list of tuples
        containing domain-instance pairs. It raises an exception if the number of 
        domains and instances is not consistent.

        Args:
            instances_path (str): The path to the directory containing PDDL files.

        Returns:
            list: A list of tuples where each tuple contains a domain and an instance file.

        Raises:
            Exception: If the number of domains is not exactly 1 or does not match the
                number of instances.
        """
        pddl_domains = []
        pddl_instances = []
        for file in os.listdir(instances_path):
            if self.is_domain(file):
                pddl_domains.append(file)
            elif self.is_instance(file):
                pddl_instances.append(file)
        if len(pddl_domains) != 1 and len(pddl_domains) != len(pddl_instances):
            raise Exception(DOMAIN_INSTANCES_ERROR)
        pddl_instances.sort()
        pddl_domains.sort()
        pairs = []
        for i in range(len(pddl_instances)):
            if len(pddl_domains) == 1:
                pairs.append((pddl_domains[0], pddl_instances[i]))
            else:
                pairs.append((pddl_domains[i], pddl_instances[i]))
        return pairs

class Domain:
    """
    A class used to represent a planning domain and its associated instances.

    Attributes
    ----------
    name : str
        The name of the domain.
    path : str
        The path to the directory containing the domain and instance files.
    instances : list
        A list of tuples, where each tuple contains a domain file and an instance file.

    Methods
    -------
    __repr__() -> str
        Returns a string representation of the domain.
    """

    def __init__(self, name: str, path2pddl: str, instances_collector: InstancesCollector = None) -> None:
        """
        Constructs all the necessary attributes for the Domain object.

        Args:
            name (str): The name of the domain.
            path2pddl (str): The path to the directory containing the domain and instance files.
            instances_collector (InstancesCollector, optional): An object used to collect instances.
                Defaults to None, in which case a new InstancesCollector is created.
        """
        self.name = name
        self.path = path2pddl
        if instances_collector is None:
            instances_collector = InstancesCollector()
        self.instances = instances_collector.collect_instances(self.path)
    
    def __repr__(self) -> str:
        """
        Returns a string representation of the domain.

        Returns:
            str: The name of the domain.
        """
        return self.name
