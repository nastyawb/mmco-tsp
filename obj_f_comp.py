import numpy as np

from configs import (max_x,
                     max_y,
                     nodes_number_values)
from params import (get_nodes_arcs_starting_node,
                    get_distances_UNI,
                    get_distances_REG)
from model_1 import CplexModel1
from model_2 import CplexModel2
from local_search import LocalSearch
from calibration import calibrate

from matplotlib import pyplot as plt
from rich.progress import Progress


def plot_res(dct_UNI, dct_REG):
    gap_values = {'uni': [round(val, 1) for val in dct_UNI.values()],
                  'reg': [round(val, 1) for val in dct_REG.values()]}
    nodes_numbers = [_ for _ in dct_UNI.keys()]

    x = np.arange(len(nodes_numbers))  # the label locations
    width = 0.33  # the width of the bars
    multiplier = 0.5

    fig, ax = plt.subplots(layout='constrained')
    colors = {'uni': 'lightcoral', 'reg': 'mediumturquoise'}

    for attribute, measurement in gap_values.items():
        offset = width * multiplier
        rects = ax.bar(x + offset, measurement, width, label=attribute, color=colors[attribute], zorder=2)
        ax.bar_label(rects, padding=3)
        multiplier += 1

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Gap (in %)')
    ax.set_xlabel('Number of nodes')
    ax.set_title('Gap between exact and heuristic solutions per each number of nodes')
    ax.set_xticks(x + width, nodes_numbers)
    ax.legend(loc='upper left', ncols=2)
    ax.set_ylim(0, 50)
    plt.grid(axis='y', color='silver', linestyle='--', linewidth=0.5, zorder=1)
    plt.show()


class ObjFunction:
    def __init__(self, n, flag, length, max_iter):
        self.flag = flag

        self.n = n
        self.nodes, self.nodes_wo_starting_node, self.arcs, self.starting_node = get_nodes_arcs_starting_node(self.n)
        self.coords, self.costs = self.choose_case()

        self.m1 = CplexModel1(self.n, self.flag)
        self.m2 = CplexModel2(self.n, self.flag)
        self.ls = LocalSearch(self.n, self.flag, length, max_iter)

        self.ms = [self.m1, self.m2, self.ls]
        self.m_val = {}

    def choose_case(self):
        if self.flag == 'uni':
            self.coords, self.costs = get_distances_UNI(self.n, max_x, max_y)
        elif self.flag == 'reg':
            self.coords, self.costs = get_distances_REG(self.n, max_x, max_y)
        return self.coords, self.costs

    def set_model_params(self, m):
        m.nodes, m.nodes_wo_starting_node, m.arcs, m.starting_node = self.nodes, \
            self.nodes_wo_starting_node, self.arcs, self.starting_node
        m.coords = self.coords
        m.costs = self.costs

    def get_obj_val(self, m):
        self.set_model_params(m)
        m.optimize_model()
        self.m_val[m] = m.obj_val

    def get_stats(self):
        for m in self.ms:
            self.get_obj_val(m)


if __name__ == '__main__':
    f_vals_UNI, f_vals_REG = {}, {}
    tl_params_UNI = calibrate('uni')
    tl_params_REG = calibrate('reg')

    with Progress() as progress:
        nodes_pr = progress.add_task("[cyan]Evaluating obj. value gap for each number of nodes",
                                     total=len(nodes_number_values))
        for i in nodes_number_values:

            obj_f_vals = ObjFunction(i, 'uni', tl_params_UNI[i]['length'], tl_params_UNI[i]['max iter'])
            obj_f_vals.get_stats()

            if round(list(obj_f_vals.m_val.values())[0], 2) != round(list(obj_f_vals.m_val.values())[1], 2):
                print(
                    f'Cplex models error: {round(list(obj_f_vals.m_val.values())[0], 2)} != {round(list(obj_f_vals.m_val.values())[1], 2)}')
            else:
                f_vals_UNI[i] = (list(obj_f_vals.m_val.values())[-1] - list(obj_f_vals.m_val.values())[0]) / \
                                list(obj_f_vals.m_val.values())[0] * 100

            obj_f_vals = ObjFunction(i, 'reg', tl_params_REG[i]['length'], tl_params_REG[i]['max iter'])
            obj_f_vals.get_stats()

            if round(list(obj_f_vals.m_val.values())[0], 2) != round(list(obj_f_vals.m_val.values())[1], 2):
                print(
                    f'Cplex models error: {round(list(obj_f_vals.m_val.values())[0], 2)} != {round(list(obj_f_vals.m_val.values())[1], 2)}')
            else:
                f_vals_REG[i] = (list(obj_f_vals.m_val.values())[-1] - list(obj_f_vals.m_val.values())[0]) / \
                                list(obj_f_vals.m_val.values())[0] * 100

            progress.update(nodes_pr, completed=i - 3 + 1)

    plot_res(f_vals_UNI, f_vals_REG)
