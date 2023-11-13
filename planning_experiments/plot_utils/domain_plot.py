from matplotlib import pyplot as plt
from planning_experiments.summary import *
from typing import Tuple, Any
import numpy as np
from pathlib import Path

_FOR_SORTING = "FOR_SORTING"


def get_sorted_df(df: pd.DataFrame, sorting_fun: Any, column: str):
    sorting_dict = {}
    for prob in set(df[column]):
        sorting_dict[prob] = sorting_fun(prob)
    df_tmp = df.copy()
    df_tmp[_FOR_SORTING] = df[column].map(sorting_dict)
    df_tmp = df_tmp.sort_values(by=_FOR_SORTING)
    return df_tmp


class DomainPlot:
    def __init__(self) -> None:
        pass

    def plot(
        self,
        df: pd.DataFrame,
        domain: str,
        sorting_function: Any = None,
        output_folder: Path = None,
    ) -> None:
        df_domain = df[df[DOM] == domain]
        legend = []

        if sorting_function is None:
            sorting_function = lambda x: x

        for sys in set(df_domain[SYS]):
            legend.append(sys)
            df_domain_sys = df_domain[df_domain[SYS] == sys]
            df_domain_sys_ordered = get_sorted_df(df_domain_sys, sorting_function, PROB)
            df_plot = df_domain_sys_ordered.copy()
            df_plot.loc[df_plot[SOL] == False, RT] = np.nan

            x = [i for i in range(len(df_domain_sys_ordered))]
            y = list(df_plot[RT])
            plt.plot(x, y, "-o")

        plt.legend(legend)
        plt.title(domain)
        plt.grid()
        plt.show() if output_folder is None else plt.savefig(
            output_folder / f"{domain}.png", bbox_inches='tight'
        )
        plt.close()
