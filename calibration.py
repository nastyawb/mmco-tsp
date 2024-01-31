import pandas as pd
from rich.progress import Progress
from tabu_search import TabuSearch
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


def calibrate(case_flag, init_path_flag):
    nodes_length_iter_train = {}
    nodes_length_iter_params = {}
    nodes_length_iter_test = {}

    with Progress() as progress:
        nodes_pr = progress.add_task(f"[cyan]Calibrating TS parameters for each number of nodes ({case_flag})",
                                     total=len(nodes_number_values))

        for nodes in nodes_number_values:
            calibr = Calibration(case_flag, nodes, init_path_flag)
            calibr.train(nodes_length_iter_train)
            calibr.test(nodes_length_iter_train, nodes_length_iter_params, nodes_length_iter_test)

            progress.update(nodes_pr, completed=nodes - 3 + 1)

    df_train = pd.DataFrame.from_dict(nodes_length_iter_train, orient='index')
    df_train.to_excel(f"train_info_{case_flag}_{init_path_flag}.xlsx")

    df_params = pd.DataFrame.from_dict(nodes_length_iter_params, orient='index')
    df_params.to_excel(f"params_info_{case_flag}_{init_path_flag}.xlsx")

    df_test = pd.DataFrame.from_dict(nodes_length_iter_test, orient='index')
    df_test.to_excel(f"test_info_{case_flag}_{init_path_flag}.xlsx")
    return nodes_length_iter_params


class Calibration:

    def __init__(self, case_flag, N, init_path_flag):
        self.case_flag = case_flag
        self.N = N
        self.init_path_flag = init_path_flag
        self.nodes, self.nodes_wo_starting_node, self.arcs, self.starting_node = get_nodes_arcs_starting_node(self.N)

        self.samples_coords = []
        self.samples_costs = []

        self.coords_train, self.coords_test = [], []
        self.costs_train, self.costs_test = [], []

    def choose_case(self):
        if self.case_flag == 'uni':
            self.create_samples_UNI()
        elif self.case_flag == 'reg':
            self.create_samples_REG()

    def create_samples_UNI(self):  # creating samples_number different UNI samples
        while len(self.samples_coords) < samples_number:
            coords, costs = get_distances_UNI(self.N, max_x, max_y)
            if coords not in self.samples_coords:
                self.samples_coords.append(coords)
                self.samples_costs.append(costs)

    def create_samples_REG(self):  # creating samples_number different REG samples
        while len(self.samples_coords) < samples_number:
            coords, costs = get_distances_REG(self.N, max_x, max_y)
            if coords not in self.samples_coords:
                self.samples_coords.append(coords)
                self.samples_costs.append(costs)

    def split_half(self, lst):  # splitting list in half
        return lst[:len(lst) // 2], lst[len(lst) // 2:]

    def split_train_test(self):  # splitting dataset in training and test sets
        self.coords_train, self.coords_test = self.split_half(self.samples_coords)
        self.costs_train, self.costs_test = self.split_half(self.samples_costs)

    def get_obj_value(self, m, coords, costs):
        m.nodes, m.nodes_wo_starting_node, m.arcs, m.starting_node = self.nodes, \
            self.nodes_wo_starting_node, self.arcs, self.starting_node  # fixing model parameters
        m.coords = coords
        m.costs = costs
        m.optimize_model()  # solving problem
        return m.obj_val

    def train(self, nodes_length_iter_train):
        self.choose_case()
        self.split_train_test()
        nodes_length_iter_train[self.N] = {}  # dictionary for training stage information

        for length in ts_list_length:
            for i in max_iter:
                nodes_length_iter_train[self.N][(length, i)] = 0  # setting counters
        for l in range(len(self.coords_train)):
            cplex_m = CplexModel1(self.N, self.case_flag)
            exact = self.get_obj_value(cplex_m, self.coords_train[l], self.costs_train[l])  # solving Cplex
            for length in ts_list_length:
                for i in max_iter:
                    ts_m = TabuSearch(self.N, self.case_flag, length, i, self.init_path_flag)
                    heur = self.get_obj_value(ts_m, self.coords_train[l], self.costs_train[l])  # solving TS

                    if exact == heur:
                        nodes_length_iter_train[self.N][(length, i)] += 1  # if equal, updating counters
            cplex_m.m.clear()

    def test(self, nodes_length_iter_train, nodes_length_iter_params, nodes_length_iter_test):
        # sorting dictionary for training stage information:
        # value (ascending),
        # second value of key (descending)
        train_info_sorted = {key: value for key, value in sorted(nodes_length_iter_train[self.N].items(),
                                                                 key=lambda item: (item[1], -item[0][1]))}

        nodes_length_iter_test[self.N] = {}  # dictionary for testing stage information
        nodes_length_iter_params[self.N] = {}  # dict for resulting parameters

        calibrated = False
        best_ind = -1  # starting from the best according to training stage
        while not calibrated:
            # if already more than one third of pairs are considered, stopping on the best according to training stage
            if -best_ind >= len(train_info_sorted) // 3:
                nodes_length_iter_params[self.N]['length'] = list(train_info_sorted.keys())[-1][0]
                nodes_length_iter_params[self.N]['max iter'] = list(train_info_sorted.keys())[-1][1]

                calibrated = True
            else:
                length = list(train_info_sorted.keys())[best_ind][0]
                i = list(train_info_sorted.keys())[best_ind][1]
                nodes_length_iter_test[self.N][(length, i)] = 0

                for l in range(len(self.coords_test)):
                    cplex_m = CplexModel1(self.N, self.case_flag)
                    exact = self.get_obj_value(cplex_m, self.coords_test[l], self.costs_test[l])  # solving Cplex

                    ts_m = TabuSearch(self.N, self.case_flag, length, i, self.init_path_flag)
                    heur = self.get_obj_value(ts_m, self.coords_test[l], self.costs_test[l])  # solving TS

                    if exact == heur:
                        nodes_length_iter_test[self.N][(length, i)] += 1  # if equal, updating counters
                    cplex_m.m.clear()

                # avoiding over/underfitting
                if nodes_length_iter_test[self.N][(length, i)] < 0.8 * nodes_length_iter_train[self.N][(length, i)]:
                    best_ind -= 1
                else:
                    nodes_length_iter_params[self.N]['length'] = length
                    nodes_length_iter_params[self.N]['max iter'] = i

                    calibrated = True


if __name__ == '__main__':
    calibrate('reg', 'greedy')
