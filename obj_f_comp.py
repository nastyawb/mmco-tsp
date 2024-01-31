import numpy as np

from configs import (max_x,
                     max_y,
                     nodes_number_values)
from params import (get_nodes_arcs_starting_node,
                    get_distances_UNI,
                    get_distances_REG)
from model_1 import CplexModel1
from model_2 import CplexModel2
from tabu_search import TabuSearch
from calibration import calibrate

from matplotlib import pyplot as plt
from rich.progress import Progress


def compare_obj_values(init_path_flag):
    f_vals_UNI, f_vals_REG = {}, {}
    # tl_params_UNI = calibrate('uni', init_path_flag)
    # tl_params_REG = calibrate('reg', init_path_flag)

    with Progress() as progress:
        nodes_pr = progress.add_task("[cyan]Evaluating obj. value gap for each number of nodes",
                                     total=len(nodes_number_values))
        for i in nodes_number_values:
            # UNIFORM
            # obj_f_vals = ObjFunction(i, 'uni', init_path_flag,
            #                          tl_params_UNI[i]['length'], tl_params_UNI[i]['max iter'])
            obj_f_vals = ObjFunction(i, 'uni', init_path_flag, i, i // 3 + 1)
            obj_f_vals.get_stats()

            # checking Cplex solutions equality
            if round(list(obj_f_vals.m_val.values())[0], 2) != round(list(obj_f_vals.m_val.values())[1], 2):
                print(
                    f'Cplex models error: {round(list(obj_f_vals.m_val.values())[0], 2)} != {round(list(obj_f_vals.m_val.values())[1], 2)}')
            else:
                # if equal, computing gap
                f_vals_UNI[i] = (list(obj_f_vals.m_val.values())[-1] - list(obj_f_vals.m_val.values())[0]) / \
                                list(obj_f_vals.m_val.values())[0] * 100

            # REGULAR
            # obj_f_vals = ObjFunction(i, 'reg', init_path_flag,
            #                          tl_params_REG[i]['length'], tl_params_REG[i]['max iter'])
            obj_f_vals = ObjFunction(i, 'reg', init_path_flag, i, i // 3)
            obj_f_vals.get_stats()

            # checking Cplex solutions equality
            if round(list(obj_f_vals.m_val.values())[0], 2) != round(list(obj_f_vals.m_val.values())[1], 2):
                print(
                    f'Cplex models error: {round(list(obj_f_vals.m_val.values())[0], 2)} != {round(list(obj_f_vals.m_val.values())[1], 2)}')
            else:
                # if equal, computing gap
                f_vals_REG[i] = (list(obj_f_vals.m_val.values())[-1] - list(obj_f_vals.m_val.values())[0]) / \
                                list(obj_f_vals.m_val.values())[0] * 100

            progress.update(nodes_pr, completed=i - 3 + 1)

    plot_res(f_vals_UNI, f_vals_REG)


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
    # ax.set_ylim(0, 50)
    plt.grid(axis='y', color='silver', linestyle='--', linewidth=0.5, zorder=1)
    plt.show()


class ObjFunction:
    def __init__(self, n, case_flag, init_path_flag, length, max_iter):
        self.case_flag = case_flag
        self.init_path_flag = init_path_flag

        self.n = n
        self.nodes, self.nodes_wo_starting_node, self.arcs, self.starting_node = get_nodes_arcs_starting_node(self.n)
        self.coords, self.costs = self.choose_case()

        self.m1 = CplexModel1(self.n, self.case_flag)
        self.m2 = CplexModel2(self.n, self.case_flag)
        self.ls = TabuSearch(self.n, self.case_flag, length, max_iter, self.init_path_flag)

        self.ms = [self.m1, self.m2, self.ls]
        self.m_val = {}

    def choose_case(self):
        if self.case_flag == 'uni':
            self.coords, self.costs = get_distances_UNI(self.n, max_x, max_y)
        elif self.case_flag == 'reg':
            self.coords, self.costs = get_distances_REG(self.n, max_x, max_y)
        return self.coords, self.costs

    def set_model_params(self, m):  # fixing parameters
        m.nodes, m.nodes_wo_starting_node, m.arcs, m.starting_node = self.nodes, \
            self.nodes_wo_starting_node, self.arcs, self.starting_node
        m.coords = self.coords
        m.costs = self.costs

    def get_obj_val(self, m):  # computing solution
        self.set_model_params(m)
        m.optimize_model()
        self.m_val[m] = m.obj_val

    def get_stats(self):  # collecting statistics
        for m in self.ms:
            self.get_obj_val(m)


if __name__ == '__main__':
    compare_obj_values('greedy')
