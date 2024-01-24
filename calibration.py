import pandas as pd
from rich.progress import Progress
from local_search import LocalSearch
from model_1 import CplexModel1
from configs import (max_x,
                     max_y,
                     nodes_number_values,
                     ts_list_length,
                     max_iter,
                     samples_number)
from params import (get_nodes_arcs_starting_node,
                    get_distances_UNI,
                    get_distances_REG)


def calibrate(flag):
    nodes_length_iter_train = {}
    nodes_length_iter_params = {}
    nodes_length_iter_test = {}

    with Progress() as progress:
        nodes_pr = progress.add_task(f"[cyan]Calibrating TS parameters for each number of nodes ({flag})",
                                     total=len(nodes_number_values))

        for nodes in nodes_number_values:
            calibr = Calibration(flag, nodes)
            calibr.train(nodes_length_iter_train)
            calibr.test(nodes_length_iter_train, nodes_length_iter_params, nodes_length_iter_test)

            progress.update(nodes_pr, completed=nodes - 3 + 1)

    df_train = pd.DataFrame.from_dict(nodes_length_iter_train, orient='index')
    df_train.to_excel(f"train_info_{flag}.xlsx")

    df_params = pd.DataFrame.from_dict(nodes_length_iter_params, orient='index')
    df_params.to_excel(f"params_info_{flag}.xlsx")

    df_test = pd.DataFrame.from_dict(nodes_length_iter_test, orient='index')
    df_test.to_excel(f"test_info_{flag}.xlsx")
    return nodes_length_iter_params


class Calibration:

    def __init__(self, flag, N):
        self.flag = flag
        self.N = N
        self.nodes, self.nodes_wo_starting_node, self.arcs, self.starting_node = get_nodes_arcs_starting_node(self.N)

        self.samples_coords = []
        self.samples_costs = []

        self.coords_train, self.coords_test = [], []
        self.costs_train, self.costs_test = [], []

    def choose_case(self):
        if self.flag == 'uni':
            self.create_samples_UNI()
        elif self.flag == 'reg':
            self.create_samples_REG()

    def create_samples_UNI(self):
        while len(self.samples_coords) < samples_number:
            coords, costs = get_distances_UNI(self.N, max_x, max_y)
            if coords not in self.samples_coords:
                self.samples_coords.append(coords)
                self.samples_costs.append(costs)

    def create_samples_REG(self):
        while len(self.samples_coords) < samples_number:
            coords, costs = get_distances_REG(self.N, max_x, max_y)
            if coords not in self.samples_coords:
                self.samples_coords.append(coords)
                self.samples_costs.append(costs)

    def split_half(self, lst):
        return lst[:len(lst) // 2], lst[len(lst) // 2:]

    def split_train_test(self):
        self.coords_train, self.coords_test = self.split_half(self.samples_coords)
        self.costs_train, self.costs_test = self.split_half(self.samples_costs)

    def get_exact_value(self, cplex_m, coords, costs):
        cplex_m.nodes, cplex_m.nodes_wo_starting_node, cplex_m.arcs, cplex_m.starting_node = self.nodes, \
            self.nodes_wo_starting_node, self.arcs, self.starting_node
        cplex_m.coords = coords
        cplex_m.costs = costs
        cplex_m.optimize_model()
        return cplex_m.obj_val

    def get_heur_value(self, ls_m, coords, costs):
        ls_m.nodes, ls_m.nodes_wo_starting_node, ls_m.arcs, ls_m.starting_node = self.nodes, \
            self.nodes_wo_starting_node, self.arcs, self.starting_node
        ls_m.coords = coords
        ls_m.costs = costs
        ls_m.optimize_model()
        return ls_m.obj_val

    def train(self, nodes_length_iter_train):
        self.choose_case()
        self.split_train_test()
        # accepted_length_iters = []
        nodes_length_iter_train[self.N] = {}
        number_of_eq = {}
        for length in ts_list_length:
            for i in max_iter:
                nodes_length_iter_train[self.N][(length, i)] = 0
        # print(f'CHECK {self.N} -- {nodes_length_iter_train[self.N]}')
        for l in range(len(self.coords_train)):
            cplex_m = CplexModel1(self.N, self.flag)
            exact = self.get_exact_value(cplex_m, self.coords_train[l], self.costs_train[l])
            for length in ts_list_length:
                for i in max_iter:
                    ls_m = LocalSearch(self.N, self.flag, length, i)
                    heur = self.get_heur_value(ls_m, self.coords_train[l], self.costs_train[l])

                    if exact == heur:
                        nodes_length_iter_train[self.N][(length, i)] += 1
            cplex_m.m.clear()
        # print(f'CHECK {self.N} -- {nodes_length_iter_train[self.N]}')

    def test(self,nodes_length_iter_train, nodes_length_iter_params, nodes_length_iter_test):
        nodes_length_iter_params[self.N] = {}
        nodes_length_iter_params[self.N]['length'] = max(nodes_length_iter_train[self.N], key=nodes_length_iter_train[self.N].get)[0]
        nodes_length_iter_params[self.N]['max iter'] = max(nodes_length_iter_train[self.N], key=nodes_length_iter_train[self.N].get)[1]

        nodes_length_iter_test[self.N] = {}
        length = nodes_length_iter_params[self.N]['length']
        i = nodes_length_iter_params[self.N]['max iter']
        nodes_length_iter_test[self.N][(length, i)] = 0

        for l in range(len(self.coords_test)):
            cplex_m = CplexModel1(self.N, self.flag)
            exact = self.get_exact_value(cplex_m, self.coords_test[l], self.costs_test[l])

            ls_m = LocalSearch(self.N, self.flag, length, i)
            heur = self.get_heur_value(ls_m, self.coords_test[l], self.costs_test[l])

            if exact == heur:
                nodes_length_iter_test[self.N][(length, i)] += 1
            cplex_m.m.clear()


# if __name__ == '__main__':
#     nodes_length_iter_train = {}
#     nodes_length_iter_params = {}
#     nodes_length_iter_test = {}
#
#     with Progress() as progress:
#         nodes_pr = progress.add_task("[cyan]CALIBRATING. Number of nodes", total=len(nodes_number_values))
#
#         for nodes in nodes_number_values:
#             calibr = Calibration('reg', nodes)
#             calibr.train()
#             calibr.test()
#
#             progress.update(nodes_pr, completed=nodes - 3 + 1)
#
#     df_train = pd.DataFrame.from_dict(nodes_length_iter_train, orient='index')
#     df_train.to_excel("train_info.xlsx")
#
#     df_params = pd.DataFrame.from_dict(nodes_length_iter_params, orient='index')
#     df_params.to_excel("params_info.xlsx")
#
#     df_test = pd.DataFrame.from_dict(nodes_length_iter_test, orient='index')
#     df_test.to_excel("test_info.xlsx")
