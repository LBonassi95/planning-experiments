import os
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import ticker
from planning_experiments.data_processor.utils import *


def format_func(value, tick_number):
    if value == 0.01:
        return "{:.2f}".format(value)
    elif value == 0.1:
        return "{:.1f}".format(value)
    else:
        return "{:.0f}".format(value)


class PlotManager:

    def __init__(self):
        pass

    def survival_plot(self, df, max_coverage, title="", save_path=None, points=1000, verbose=False, fontsize=10, logscale=False, xlabel=None, ylabel=None,
                      system_colors=None, system_linestyles=None, systems_legend=None, check_coverage_percentage = None):
        systems = get_col_domain(df, SYS)
        fig = plt.figure(figsize=(6, 4), dpi=100, facecolor="w", edgecolor="k")
        x = np.linspace(0.2, 1800, num=points)
        ncols = 3
        if logscale:
            ncols = 1
            x = np.linspace(1, 1800, num=points)
            plt.xscale('log')
        legend = []
        df = df[df[SOL] == True]
        for system in systems:
            if systems_legend is not None:
                legend.append(systems_legend[system])
            else:
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
                for i in range(len(x[:int(len(x)/4)])):
                    print("{:.2f} - {:.2f}".format(x[i], y[i]))
                if check_coverage_percentage is not None:
                    print("Coverage at {}%: {} - {}s".format(check_coverage_percentage, y[int(check_coverage_percentage*len(x)/100)], int(check_coverage_percentage*len(x)/100)))
            if system_colors is None or system_linestyles is None:
                plt.plot(x, y, linewidth=3.8,
                         antialiased=True)
            else:
                plt.plot(x, y, linestyle=system_linestyles[system],
                         color=system_colors[system], linewidth=3.8,
                         antialiased=True)
        plt.grid()
        plt.title("Coverage over time")
        ax = plt.gca()
        plt.title(title)
        if not logscale:
            ax.set_xticks([0, 250, 500, 750, 1000, 1250, 1500, 1750])
        ax.set_yticks([i for i in range(0, max_coverage + 1, 20)])
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_func))
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_func))
        plt.legend(legend, bbox_to_anchor=(
            0.69, 0.44), loc='best', fontsize=14)
        ax.tick_params(axis='both', labelsize=fontsize)
        if xlabel is None:
            plt.xlabel(r"Planning time", fontsize=fontsize)
        else:
            plt.xlabel(xlabel, fontsize=fontsize)
        if ylabel is None:
            plt.ylabel(r"Coverage", fontsize=fontsize)
        else:
            plt.ylabel(ylabel, fontsize=fontsize)
        plt.legend(legend, loc='best', borderaxespad=0.5, handletextpad=0.5, framealpha=0.6,
                   ncol=ncols, fontsize=fontsize+2, handlelength=2.5, columnspacing=0.3)
        if save_path is not None:
            plt.savefig(save_path, bbox_inches='tight',pad_inches = 0.01, dpi=300)
            plt.close()
        else:
            plt.show()
            plt.close()

    def runtime_comparison_plot(self, df: pd.DataFrame, system1: str, system2: str, timeout=1800, save_path=None, fontsize=12, axis_labels=False,
                                domain_markers = None, domain_colors = None, domain_legend = None, system_legend = None, hide_legend = False, facecolors='none', s=120):
        plt.figure(figsize=(6, 4), dpi=100, facecolor="w", edgecolor="k")

        # Everything that is not a solution, is considered a timeout
        df.loc[df[SOL] == False, RT] = 1800

        df = df.drop(columns=[SOL])

        runtime1 = f'{RT}_{system1}'
        runtime2 = f'{RT}_{system2}'

        df_system1 = df[df[SYS] == system1].rename(columns={RT: runtime1})
        df_system2 = df[df[SYS] == system2].rename(columns={RT: runtime2})

        merged_df = pd.merge(df_system1, df_system2, on=[D, I])
        legend = []
        systems = get_col_domain(df, D)
        plt.yscale('log')
        plt.xscale('log')
        x = np.geomspace(1e0, 1800, num=100)
        points_above = 0
        for domain in systems:
            if domain_legend is not None:
                legend.append(domain_legend[domain])
            else:
                legend.append(domain)
            df_domain = merged_df[merged_df[D] == domain]
            runtimes_system1 = list(
                df_domain[runtime1].replace(np.Inf, timeout))
            runtimes_system2 = list(
                df_domain[runtime2].replace(np.Inf, timeout))
            if domain_markers is not None and domain_colors is not None:
                if facecolors != 'none':
                    plt.scatter(runtimes_system1, runtimes_system2,
                                marker=domain_markers[domain], color=domain_colors[domain], linewidths=1.5, s=s)
                else:
                    plt.scatter(runtimes_system1, runtimes_system2,
                                marker=domain_markers[domain], color=domain_colors[domain], linewidths=1.5, s=s, facecolors=facecolors)
            else:
                plt.scatter(runtimes_system1, runtimes_system2,
                            linewidths=1.5, s=s)
            points_above += len([k for k in np.subtract(runtimes_system2,
                                runtimes_system1) if k > 0])
        print(points_above)
        plt.plot(x, x, "k--", label='_nolegend_')
        plt.grid()
        plt.xticks(fontsize=fontsize)
        plt.yticks(fontsize=fontsize)
        if not hide_legend:
            plt.legend(legend, loc='best', borderaxespad=0.5, handletextpad=0.5,
                    framealpha=0.6, ncol=1, fontsize=fontsize, handlelength=2.5, columnspacing=0.3)
        if axis_labels:
            if system_legend is not None:
                plt.xlabel(system_legend[system1], fontsize=fontsize)
                plt.ylabel(system_legend[system2], fontsize=fontsize)
            else:
                plt.xlabel(system1, fontsize=fontsize)
                plt.ylabel(system2, fontsize=fontsize)
        if save_path is not None:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
            plt.close()
        else:
            plt.show()
            plt.close()


    def expanded_comparison_plot(self, df: pd.DataFrame, system1: str, system2: str, horizon: int, save_path=None, fontsize=12, axis_labels=False,
                                 domain_markers = None, domain_colors = None, domain_legend = None, system_legend = None):
        plt.figure(figsize=(6, 4), dpi=100, facecolor="w", edgecolor="k")
        exp1 = f'{EN}_{system1}'
        exp2 = f'{EN}_{system2}'
        df_system1 = df[df[SYS] == system1].rename(columns={EN: exp1})
        df_system2 = df[df[SYS] == system2].rename(columns={EN: exp2})

        merged_df = pd.merge(df_system1, df_system2, on=[D, I])
        legend = []
        systems = get_col_domain(df, D)
        plt.yscale('log')
        plt.xscale('log')
        x = np.geomspace(1e0, horizon, num=1000)
        for domain in systems:
            if domain_legend is not None:
                legend.append(domain_legend[domain])
            else:
                legend.append(domain)
            df_domain = merged_df[merged_df[D] == domain]
            runtimes_system1 = list(df_domain[exp1].replace(np.NaN, horizon))
            runtimes_system2 = list(df_domain[exp2].replace(np.NaN, horizon))
            if domain_markers is not None and domain_colors is not None:
                plt.scatter(runtimes_system1, runtimes_system2, marker=domain_markers[domain], color=domain_colors[domain], facecolors="none", linewidths=1.5, s=120)

            else:
                plt.scatter(runtimes_system1, runtimes_system2, linewidths=1.5, s=120)

        plt.plot(x, x, "k--", label='_nolegend_')
        plt.grid()
        plt.xticks(fontsize=fontsize)
        plt.yticks(fontsize=fontsize)
        plt.legend(legend, loc='best', borderaxespad=0.5, handletextpad=0.5, framealpha=0.6, ncol=1, fontsize=fontsize, handlelength=2.5, columnspacing=0.3)
        if axis_labels:
            if system_legend is not None:
                plt.xlabel(system_legend[system1], fontsize=fontsize)
                plt.ylabel(system_legend[system2], fontsize=fontsize)
            else:
                plt.xlabel(system1, fontsize=fontsize)
                plt.ylabel(system2, fontsize=fontsize)
        if save_path is not None:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
            plt.close()
        else:
            plt.show()
            plt.close()