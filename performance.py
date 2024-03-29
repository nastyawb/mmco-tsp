from matplotlib import pyplot as plt
from rich.progress import Progress
import pandas as pd
from configs import (nodes_number_values,
                     tests_number,
                     max_x, max_y)
from params import (get_nodes_arcs_starting_node,
                    get_distances_UNI,
                    get_distances_REG,
                    plot_grid)
from model_1 import CplexModel1
from model_2 import CplexModel2
from tabu_search import TabuSearch
from calibration import calibrate


def solve_exact_and_heur(N, case_flag, init_path_flag):
    dummy_dct = {_: [] for _ in nodes_number_values}
    # tl_params = calibrate(case_flag, init_path_flag)

    # eval = Evaluation(N, case_flag, init_path_flag, tl_params[N]['length'], tl_params[N]['max iter'])
    eval = Evaluation(N, case_flag, init_path_flag, 0, 0)
    eval.optimize_model(eval.m1, dummy_dct)
    eval.optimize_model(eval.m2, dummy_dct)
    eval.optimize_model(eval.ts, dummy_dct)

    sol_m1 = eval.m1.get_solution()
    sol_m2 = eval.m2.get_solution()
    if sol_m1 != sol_m2:

        # plot grid
        plot_grid(eval.coords)

        # plot exact solution 1
        print(f'Starting node: {eval.m1.starting_node}')

        print(f'Path: {sol_m1}')
        eval.m1.plot_path()
        print(eval.m1.obj_val)

        # plot exact solution 2
        print(f'Starting node: {eval.m2.starting_node}')

        print(f'Path: {sol_m2}')
        eval.m2.plot_path()
        print(eval.m2.obj_val)
    else:
        print('Same')


def evaluate(init_path_flag):
    # nodes_number_time_UNI_m1 = {_: [] for _ in nodes_number_values}
    # nodes_number_time_REG_m1 = {_: [] for _ in nodes_number_values}
    # avr_time_UNI_m1, avr_time_REG_m1 = {}, {}

    # nodes_number_time_UNI_m2 = {_: [] for _ in nodes_number_values}
    # nodes_number_time_REG_m2 = {_: [] for _ in nodes_number_values}
    # avr_time_UNI_m2, avr_time_REG_m2 = {}, {}

    # tl_params_UNI = calibrate('uni', init_path_flag)
    nodes_number_time_UNI_ls = {_: [] for _ in nodes_number_values}
    # tl_params_REG = calibrate('reg', init_path_flag)
    nodes_number_time_REG_ls = {_: [] for _ in nodes_number_values}
    avr_time_UNI_ls, avr_time_REG_ls = {}, {}

    with Progress() as progress:
        nodes_pr = progress.add_task("[red]Evaluating time for each number of nodes",
                                     total=len(nodes_number_values))
        tests_pr = progress.add_task(f"[magenta]Running {tests_number} tests for each number of nodes",
                                     total=tests_number)

        for i in nodes_number_values:

            for j in range(tests_number):
                # evl_UNI = Evaluation(i, 'uni', init_path_flag,
                #                      tl_params_UNI[i]['length'], tl_params_UNI[i]['max iter'])
                evl_UNI = Evaluation(i, 'uni', init_path_flag,
                                     i, i)
                # evl_UNI.optimize_model(evl_UNI.m1, nodes_number_time_UNI_m1)
                # evl_UNI.optimize_model(evl_UNI.m2, nodes_number_time_UNI_m2)
                evl_UNI.solve_ts(nodes_number_time_UNI_ls)

                # evl_REG = Evaluation(i, 'reg', init_path_flag,
                #                      tl_params_REG[i]['length'], tl_params_REG[i]['max iter'])
                evl_REG = Evaluation(i, 'reg', init_path_flag,
                                     i, i)
                # evl_REG.optimize_model(evl_REG.m1, nodes_number_time_REG_m1)
                # evl_REG.optimize_model(evl_REG.m2, nodes_number_time_REG_m2)
                evl_REG.solve_ts(nodes_number_time_REG_ls)

                progress.update(tests_pr, completed=j + 1)

            # curr_avr_time_UNI_m1 = sum(nodes_number_time_UNI_m1[i]) / tests_number  # computing average time
            # curr_avr_time_UNI_m2 = sum(nodes_number_time_UNI_m2[i]) / tests_number
            curr_avr_time_UNI_ls = sum(nodes_number_time_UNI_ls[i]) / tests_number
            # avr_time_UNI_m1[i] = curr_avr_time_UNI_m1
            # avr_time_UNI_m2[i] = curr_avr_time_UNI_m2
            avr_time_UNI_ls[i] = curr_avr_time_UNI_ls

            # curr_avr_time_REG_m1 = sum(nodes_number_time_REG_m1[i]) / tests_number
            # curr_avr_time_REG_m2 = sum(nodes_number_time_REG_m2[i]) / tests_number
            curr_avr_time_REG_ls = sum(nodes_number_time_REG_ls[i]) / tests_number
            # avr_time_REG_m1[i] = curr_avr_time_REG_m1
            # avr_time_REG_m2[i] = curr_avr_time_REG_m2
            avr_time_REG_ls[i] = curr_avr_time_REG_ls

            progress.update(nodes_pr, completed=i - 3 + 1)

    # plot_res(avr_time_UNI_m1, avr_time_REG_m1,
    #          avr_time_UNI_m2, avr_time_REG_m2,
    #          avr_time_UNI_ls, avr_time_REG_ls)
    # plot_res(avr_time_UNI_m1, avr_time_REG_m1,
    #          avr_time_UNI_m2, avr_time_REG_m2)
    plot_res(avr_time_UNI_ls, avr_time_REG_ls)


# def plot_res(dct_UNI_m1, dct_REG_m1, dct_UNI_m2, dct_REG_m2, dct_UNI_ls, dct_REG_ls):
# def plot_res(dct_UNI_m1, dct_REG_m1, dct_UNI_m2, dct_REG_m2):
def plot_res(dct_UNI_ts, dct_REG_ts):
    stats = {'uni ts': dct_UNI_ts,
             'reg ts': dct_REG_ts}
    df = pd.DataFrame.from_dict(stats, orient='index')
    df.to_excel(f"ts_comp.xlsx")

    # time_values_UNI_m1 = [_ for _ in dct_UNI_m1.values()]
    # time_values_REG_m1 = [_ for _ in dct_REG_m1.values()]
    # time_values_UNI_m2 = [_ for _ in dct_UNI_m2.values()]
    # time_values_REG_m2 = [_ for _ in dct_REG_m2.values()]
    time_values_UNI_ls = [_ for _ in dct_UNI_ts.values()]
    time_values_REG_ls = [_ for _ in dct_REG_ts.values()]
    nodes_numbers = [_ for _ in dct_UNI_ts.keys()]
    # plt.plot(nodes_numbers, time_values_UNI_m1, label='Uniform case, model 1', color='cornflowerblue')
    # plt.plot(nodes_numbers, time_values_REG_m1, label='Regular case, model 1', color='sandybrown')
    # plt.plot(nodes_numbers, time_values_UNI_m2, label='Uniform case, model 2', color='darkseagreen')
    # plt.plot(nodes_numbers, time_values_REG_m2, label='Regular case, model 2', color='mediumvioletred')
    plt.plot(nodes_numbers, time_values_UNI_ls, label='Uniform case, tabu search', color='salmon')
    plt.plot(nodes_numbers, time_values_REG_ls, label='Regular case, tabu search', color='gold')
    plt.xlabel('Number of nodes')
    plt.ylabel('Computing time (in sec)')
    plt.title(f'Aver. time to find solution ({tests_number} tests per each number of nodes)')
    plt.grid(color='silver', linestyle='--', linewidth=0.5)
    plt.legend()
    plt.show()
    # plt.savefig(f'TSP_chart_{len(time_values)}nodes_{tests_number}tests_{int(avr_time_limit)}sec_time_limit.png')


class Evaluation:

    def __init__(self, n, case_flag, init_path_flag, length, max_iter):
        self.n = n
        self.case_flag = case_flag
        self.init_path_flag = init_path_flag
        self.nodes, self.nodes_wo_starting_node, self.arcs, self.starting_node = get_nodes_arcs_starting_node(self.n)
        self.coords, self.costs = self.choose_case()

        self.m1 = CplexModel1(self.n, self.case_flag)
        self.m2 = CplexModel2(self.n, self.case_flag)

        self.ts = TabuSearch(self.n, self.case_flag, length, max_iter, self.init_path_flag)
        self.solution = None

    def choose_case(self):
        if self.case_flag == 'uni':
            self.coords, self.costs = get_distances_UNI(self.n, max_x, max_y)
        elif self.case_flag == 'reg':
            self.coords, self.costs = get_distances_REG(self.n, max_x, max_y)
        return self.coords, self.costs

    def set_model_params(self, m):  # fixing parameters so the are the same for every model
        m.nodes, m.nodes_wo_starting_node, m.arcs, m.starting_node = self.nodes, \
            self.nodes_wo_starting_node, self.arcs, self.starting_node
        m.coords = self.coords
        m.costs = self.costs

    def optimize_model(self, m, nodes_number_time): # solving Cplex
        self.set_model_params(m)
        m.optimize_model()
        nodes_number_time[self.n].append((m.solving_end - m.solving_start).total_seconds())

    def solve_ts(self, nodes_number_time):  # solving TS
        self.ts.optimize_model()
        nodes_number_time[self.n].append((self.ts.solving_end - self.ts.solving_start).total_seconds())

    def collect_obj_val(self, m, nodes_number_val):
        nodes_number_val[self.n].append(m.obj_val)


if __name__ == '__main__':
    # solve_exact_and_heur(9, 'uni', 'greedy')
    evaluate('greedy')
