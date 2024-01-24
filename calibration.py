import pandas as pd
from local_search import LocalSearch
from model_1 import CplexModel1
from configs import (max_x,
                     max_y,
                     nodes_number_values,
                     ts_list_length,
                     max_iter,
                     samples_number)
from params import (get_distances_UNI,
                    get_distances_REG)


class Calibration:

    def __init__(self, flag, N):
        self.flag = flag
        self.N = N

        self.samples_coords = []
        self.samples_costs = []

        self.coords_train, self.coords_val, self.coords_test = [], [], []
        self.costs_train, self.costs_val, self.costs_test = [], [], []

        self.cplex_m = CplexModel1(self.N, self.flag)

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

    def split_train_val_test(self):
        self.coords_train, rest = self.split_half(self.samples_coords)
        self.coords_val, self.coords_test = self.split_half(rest)

        self.costs_train, rest = self.split_half(self.samples_costs)
        self.costs_val, self.costs_test = self.split_half(rest)

    def get_exact_value(self, coords, costs):
        self.cplex_m.coords = coords
        self.cplex_m.costs = costs
        self.cplex_m.optimize_model()
        return self.cplex_m.obj_val

    def get_heur_value(self, ls_m, coords, costs):
        ls_m.coords = coords
        ls_m.costs = costs
        ls_m.optimize_model()
        return ls_m.obj_val

    def train(self):
        self.choose_case()
        self.split_train_val_test()
        # accepted_length_iters = []
        nodes_length_iter_train[self.N] = {}
        number_of_eq = {}
        for length in ts_list_length:
            for i in max_iter:
                nodes_length_iter_train[self.N][(length, i)] = 0
        # print(f'CHECK {self.N} -- {nodes_length_iter_train[self.N]}')
        for l in range(len(self.coords_train)):
            exact = self.get_exact_value(self.coords_train[l], self.costs_train[l])
            for length in ts_list_length:
                for i in max_iter:
                    ls_m = LocalSearch(self.N, self.flag, length, i)
                    heur = self.get_heur_value(ls_m, self.coords_train[l], self.costs_train[l])

                    if exact == heur:
                        nodes_length_iter_train[self.N][(length, i)] += 1
        # print(f'CHECK {self.N} -- {nodes_length_iter_train[self.N]}')

    def validate(self):
        nodes_length_iter_params[self.N] = {}
        nodes_length_iter_params[self.N]['length'] = max(nodes_length_iter_train[self.N], key=nodes_length_iter_train[self.N].get)[0]
        nodes_length_iter_params[self.N]['max iter'] = max(nodes_length_iter_train[self.N], key=nodes_length_iter_train[self.N].get)[1]

        nodes_length_iter_val[self.N] = {}
        length = nodes_length_iter_params[self.N]['length']
        i = nodes_length_iter_params[self.N]['max iter']
        nodes_length_iter_val[self.N][(length, i)] = 0

        for l in range(len(self.coords_val)):
            exact = self.get_exact_value(self.coords_val[l], self.costs_val[l])

            ls_m = LocalSearch(self.N, self.flag, length, i)
            heur = self.get_heur_value(ls_m, self.coords_val[l], self.costs_val[l])

            if exact == heur:
                nodes_length_iter_val[self.N][(length, i)] += 1


if __name__ == '__main__':
    nodes_length_iter_train = {}
    nodes_length_iter_params = {}
    nodes_length_iter_val = {}

    for nodes in nodes_number_values:
        calibr = Calibration('reg', nodes)
        calibr.train()
        calibr.validate()

    df_train = pd.DataFrame.from_dict(nodes_length_iter_train, orient='index')
    df_train.to_excel("train_info.xlsx")

    df_params = pd.DataFrame.from_dict(nodes_length_iter_params, orient='index')
    df_params.to_excel("params_info.xlsx")

    df_val = pd.DataFrame.from_dict(nodes_length_iter_val, orient='index')
    df_val.to_excel("val_info.xlsx")
