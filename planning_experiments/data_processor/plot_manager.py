import os
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from planning_experiments.data_processor.utils import *

class PlotManager:

    def __init__(self):
        pass

    def survival_plot(self, df, max_coverage, title = "", save_path = None, points=1000, verbose=False, fontsize=10, logscale=False, xlabel=None, ylabel=None):
        systems = get_col_domain(df, SYS)
        fig = plt.figure(figsize=(6, 4), dpi=100, facecolor="w", edgecolor="k")
        x = np.linspace(0, 1800, num=points)
        ncols = 3
        if logscale:
            ncols = 1
            x = np.linspace(0.3, 1800, num=points)
            plt.xscale('log')
        legend = []
        df = df[df[SOL] == True]
        for system in systems:
            legend.append(system)
            df_system = df[df[SYS] == system]
            y = np.zeros(len(x))
            runtimes = list(df_system[RT])
            for i in range(len(x)):
                current_time = x[i]
                y[i] = len([r for r in runtimes if r <= current_time])
                # for index, row in df_system.iterrows():
                #     time = row[RUNTIME]
                #     if time <= t:
                #         coverage += 1
                # y[i] = float(coverage)
            if verbose:
                print(runtimes)
                print(system)
                if system == 'ltlexp' or system == 'plan4past' or system == 'ltlpoly-4':
                    for i in range(len(x[:int(len(x)/4)])):
                        print("{:.2f} - {:.2f}".format(x[i], y[i]))
            plt.plot(x, y, linewidth=3.8, antialiased=True)
        plt.grid()
        # plt.title("Coverage over time")
        #ax = plt.gca()
        # plt.title(title)
        # if not logscale:
        #     ax.set_xticks([0, 250, 500, 750, 1000, 1250, 1500, 1750])
        # ax.set_yticks([i for i in range(0, max_coverage + 1, 20)])
        # ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_func))
        # ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_func))
        # plt.legend(legend, bbox_to_anchor=(0.69, 0.44), loc='best', fontsize=14)
        #ax.tick_params(axis='both', labelsize=fontsize)
        if xlabel is None:
            plt.xlabel(r"Planning time", fontsize=fontsize)
        else:
            plt.xlabel(xlabel, fontsize=fontsize)
        if ylabel is None:
            plt.ylabel(r"Coverage", fontsize=fontsize)
        else:
            plt.ylabel(ylabel, fontsize=fontsize)
        plt.legend(legend, loc='best', borderaxespad=0.5, handletextpad=0.5, framealpha=0.6, ncol=ncols, fontsize=fontsize, handlelength=2.5, columnspacing=0.3)
        if save_path is not None:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
            plt.close()
        else:
            plt.show()
            plt.close()
