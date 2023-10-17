from matplotlib import pyplot as plt
from planning_experiments.summary import *
import numpy as np


class SurvivalPlot:

    def __init__(self, timeout: int = 1800,
                 fontsize: int = 12,
                 num_points: int = 1000,
                 logscale: bool = False,
                 legends_kwargs: dict = {},
                 plot_kwargs: dict = {}) -> None:

        self.timeout = timeout
        self.num_points = num_points
        self.logscale = logscale
        self.fontsize = fontsize
        self.legends_kwargs = legends_kwargs
        self.plot_kwargs = plot_kwargs

    def plot(self, df) -> None:
        df = df[df[SOL] == True]
        plt.figure(figsize=(6, 4), dpi=100, facecolor="w", edgecolor="k")

        if self.logscale:
            x = np.linspace(1, self.timeout, num=self.num_points)
            plt.xscale('log')
        else:
            x = np.linspace(1, self.timeout, num=self.num_points)

        legend = []
        systems = set(df[SYS])
        df = df[df[SOL] == True]

        for system in systems:
            legend.append(system)
            df_system = df[df[SYS] == system]
            y = np.zeros(len(x))
            runtimes = list(df_system[RT])
            for i in range(len(x)):
                current_time = x[i]
                y[i] = len([r for r in runtimes if r <= current_time])
            plt.plot(x, y, antialiased=True, label=system, **self.plot_kwargs)

        plt.grid()
        plt.legend(legend, fontsize=self.fontsize, **self.legends_kwargs)
        plt.xlabel(r"Planning time", fontsize=self.fontsize)
        plt.ylabel(r"Coverage", fontsize=self.fontsize)
        plt.show()
        plt.close()