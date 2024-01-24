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

from matplotlib import pyplot as plt
from rich.progress import Progress


def plot_res(dct_UNI, dct_REG):
    gap_values_UNI = [_ for _ in dct_UNI.values()]
    gap_values_REG = [_ for _ in dct_REG.values()]
    nodes_numbers = [_ for _ in dct_UNI.keys()]
    # plt.plot(nodes_numbers, gap_values_UNI, label='Uniform case')
    # plt.plot(nodes_numbers, gap_values_REG, label='Regular case')

    plt.bar(np.arange(len(nodes_numbers)) - 0.2, gap_values_UNI, 0.4, label='Uniform case', color='lightcoral')
    plt.bar(np.arange(len(nodes_numbers)) + 0.2, gap_values_REG, 0.4, label='Regular case', color='mediumturquoise')

    plt.xticks(nodes_numbers, nodes_numbers)
    plt.xlabel('Number of nodes')
    plt.ylabel('Gap (in %)')
    plt.title(f'Gap between exact and heuristic solutions per each number of nodes')
    plt.grid(axis = 'y', color='silver', linestyle='--', linewidth=0.5)
    plt.legend()
    plt.show()


class ObjFunction:
    def __init__(self, n, flag):
        self.flag = flag

        self.n = n
        self.nodes, self.nodes_wo_starting_node, self.arcs, self.starting_node = get_nodes_arcs_starting_node(self.n)
        self.costs = self.choose_case()

        self.m1 = CplexModel1(self.n, flag)
        self.m2 = CplexModel2(self.n, flag)
        self.ls = LocalSearch(self.n, flag, 4, 15)

        self.ms = [self.m1, self.m2, self.ls]
        self.m_val = {}

    def choose_case(self):
        if self.flag == 'uni':
            self.costs = get_distances_UNI(self.n, max_x, max_y)
        elif self.flag == 'reg':
            self.costs = get_distances_REG(self.n, max_x, max_y)
        return self.costs

    def get_obj_val(self, m):
        m.optimize_model()
        self.m_val[m] = m.obj_val

    def get_stats(self):
        for m in self.ms:
            self.get_obj_val(m)


if __name__ == '__main__':
    f_vals_UNI, f_vals_REG = {}, {}

    with Progress() as progress:
        nodes_pr = progress.add_task("[cyan]Number of nodes", total=len(nodes_number_values))
        for i in nodes_number_values:

            obj_f_vals = ObjFunction(i, 'uni')
            obj_f_vals.get_stats()

            if round(list(obj_f_vals.m_val.values())[0], 2) != round(list(obj_f_vals.m_val.values())[1], 2):
                print(f'Cplex models error: {round(list(obj_f_vals.m_val.values())[0], 2)} != {round(list(obj_f_vals.m_val.values())[1], 2)}')
            else:
                f_vals_UNI[i] = (list(obj_f_vals.m_val.values())[-1] - list(obj_f_vals.m_val.values())[0]) / \
                                list(obj_f_vals.m_val.values())[0] * 100

            obj_f_vals = ObjFunction(i, 'reg')
            obj_f_vals.get_stats()

            if round(list(obj_f_vals.m_val.values())[0], 2) != round(list(obj_f_vals.m_val.values())[1], 2):
                print(f'Cplex models error: {round(list(obj_f_vals.m_val.values())[0], 2)} != {round(list(obj_f_vals.m_val.values())[1], 2)}')
            else:
                f_vals_REG[i] = (list(obj_f_vals.m_val.values())[-1] - list(obj_f_vals.m_val.values())[0]) / \
                                list(obj_f_vals.m_val.values())[0] * 100

            progress.update(nodes_pr, completed=i - 3 + 1)

    plot_res(f_vals_UNI, f_vals_REG)
