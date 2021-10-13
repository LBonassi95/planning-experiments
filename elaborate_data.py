import json
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import matplotlib
from matplotlib import rc

PLAN_STEPS = 'PLAN_STEPS'

SYSTEM = 'SYSTEM'

TOTALRUNTIME = 'TOTALRUNTIME'

DOMAIN = 'DOMAIN'

from os import path


def format_func(value, tick_number):
    if value == 0.01:
        return "{:.2f}".format(value)
    elif value == 0.1:
        return "{:.1f}".format(value)
    else:
        return "{:.0f}".format(value)


def get_tot_keys(json_lst):
    tot_keys = set()
    for j in json_lst:
        for key in j:
            tot_keys.add(key)
    return tot_keys


def json2dataframe(json_lst):
    dict = {}
    tot_keys = get_tot_keys(json_lst)
    for key in tot_keys:
        dict[key] = []

    for j in json_lst:
        for key in tot_keys:
            if key in j:
                dict[key].append(j[key])
            else:
                dict[key].append(None)
    return pd.DataFrame.from_dict(dict)


def get_col_domain(df, col):
    domain = []
    for index, row in df.iterrows():
        if df.loc[index, col] not in domain:
            domain.append(df.loc[index, col])
    return domain


def survival_plot(df, system_column=SYSTEM, runtime_column=TOTALRUNTIME, outfolder='./', name=""):
    plt.figure(num=None, dpi=600, facecolor='w', edgecolor='k', figsize=(8, 5))
    x = np.geomspace(0.01, 1800, num=100)
    legend = []
    planners = get_col_domain(df, system_column)
    upper = 0
    for planner in planners:
        legend.append(planner)
        df_planner = df[df[system_column] == planner]
        upper = len(df_planner)
        y = np.zeros(len(x))
        for i in range(len(x)):
            coverage = 0
            t = x[i]
            for index, row in df_planner.iterrows():
                time = row[runtime_column]
                if time <= t:
                    coverage += 1
            y[i] = float(coverage)
        plt.plot(x, y, linewidth=3.5,
                 antialiased=True)

    plt.grid()
    # plt.title("Coverage over time")
    ax = plt.gca()
    ax.set_xticks([0, 250, 500, 750, 1000, 1250, 1500, 1750])
    ax.set_yticks([i for i in range(0, upper + 1, 10)])
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(format_func))
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(format_func))
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    # plt.legend(legend, bbox_to_anchor=(0.69, 0.44), loc='best', fontsize=14)
    plt.legend(legend, bbox_to_anchor=(1.01, 1), loc='best', fontsize=15, borderaxespad=0, handletextpad=0.5,
               framealpha=1)
    plt.savefig(path.join(outfolder, "./survival_plot_{}.png".format(name)), bbox_inches='tight')
    plt.close()


def survival_plot_over_domains(df, domain_column=DOMAIN, runtime_column=TOTALRUNTIME, outfolder='./', name=""):
    plt.figure(num=None, dpi=600, facecolor='w', edgecolor='k', figsize=(8, 5))
    x = np.geomspace(0.01, 1800, num=100)
    legend = []
    upper = 0
    for dom in get_col_domain(df, domain_column):
        legend.append(dom)
        df_planner = df[df[domain_column] == dom]
        upper = len(df_planner)
        y = np.zeros(len(x))
        for i in range(len(x)):
            coverage = 0
            t = x[i]
            for index, row in df_planner.iterrows():
                time = row[runtime_column]
                if time <= t:
                    coverage += 1
            y[i] = float(coverage)
        plt.plot(x, y, linewidth=3.5,
                 antialiased=True)

    plt.grid()
    # plt.title("Coverage over time")
    ax = plt.gca()
    ax.set_xticks([0, 250, 500, 750, 1000, 1250, 1500, 1750])
    ax.set_yticks([i for i in range(0, upper + 1, 10)])
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(format_func))
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(format_func))
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    # plt.legend(legend, bbox_to_anchor=(0.69, 0.44), loc='best', fontsize=14)
    plt.legend(legend, loc='best', fontsize=15, borderaxespad=0, handletextpad=0.5, framealpha=1)
    plt.savefig(path.join(outfolder, "./survival_plot_{}.png".format(name)), bbox_inches='tight')
    plt.close()


def makespan_plot(df, system_column=SYSTEM, steps_column=PLAN_STEPS, outfolder='./', name=""):
    if PLAN_STEPS not in df.columns:
        return
    plt.figure(num=None, dpi=600, facecolor='w', edgecolor='k', figsize=(8, 5))
    legend = []
    planners = get_col_domain(df, system_column)
    for planner in planners:
        legend.append(planner)
        df_planner = df[df[system_column] == planner]
        df_planner = df_planner.sort_values('INSTANCE')
        y = list(df_planner[steps_column])
        x = [i for i in range(len(y))]
        plt.scatter(x, y, facecolors='none')
    plt.grid()
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.legend(legend, bbox_to_anchor=(1.01, 1), loc='best', fontsize=15, borderaxespad=0, handletextpad=0.5,
               framealpha=1)
    plt.savefig(path.join(outfolder, "./quality_plot_{}.png".format(name)), bbox_inches='tight')
    plt.close()


def get_coverage(df, domain_column=DOMAIN, runtime_column=TOTALRUNTIME):
    df_ok = df.dropna(subset=[TOTALRUNTIME], inplace=False)
    domains = get_col_domain(df, DOMAIN)
    planners = get_col_domain(df, SYSTEM)
    dictionary = {SYSTEM: []}
    for dom in domains:
        dictionary[dom] = []
    for p in planners:
        dictionary[SYSTEM].append(p)
        for dom in domains:
            df_planner = df_ok[df_ok[SYSTEM] == p]
            df_planner_dom = df_planner[df_planner[DOMAIN] == dom]
            num = len(df_planner_dom)
            dictionary[dom].append(num)
    coverage = pd.DataFrame(dictionary)
    coverage = coverage.set_index(SYSTEM)
    coverage = coverage.T
    ax = coverage.plot.bar(legend=False, figsize=(10, 4))
    ax.legend().set_title("")
    ax.set_axisbelow(True)
    ax.legend(fontsize=15)
    plt.grid()
    plt.savefig("./coverage.png", bbox_inches='tight', dpi=600)
    plt.close()
    coverage.to_csv('./coverage.csv', index=True)


def preprocess(df):
    for index, row in df.iterrows():
        df.loc[index, DOMAIN] = df.loc[index, DOMAIN].replace('_', '-')
        df.loc[index, SYSTEM] = df.loc[index, SYSTEM].replace('_', '-')


if __name__ == '__main__':
    with open('results.txt', 'r') as inp:
        res = inp.read()
    res = res.strip()
    res = res.split('\n')
    res_dict = {}
    json_list = [json.loads(r.strip()) for r in res]
    df = json2dataframe(json_list)
    preprocess(df)
    get_coverage(df)
    survival_plot(df, outfolder='./', name='experiment')
    makespan_plot(df, outfolder='./', name='experiment')
