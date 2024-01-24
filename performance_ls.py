from configs import (nodes_number_values,
                     tests_number)
from model_1 import CplexModel1
from model_2 import CplexModel2
from local_search import LocalSearch
from matplotlib import pyplot as plt
from rich.progress import Progress


def plot_res(dct_UNI_m1, dct_REG_m1, dct_UNI_m2, dct_REG_m2, dct_UNI_ls, dct_REG_ls):
    time_values_UNI_m1 = [_ for _ in dct_UNI_m1.values()]
    time_values_REG_m1 = [_ for _ in dct_REG_m1.values()]
    time_values_UNI_m2 = [_ for _ in dct_UNI_m2.values()]
    time_values_REG_m2 = [_ for _ in dct_REG_m2.values()]
    time_values_UNI_ls = [_ for _ in dct_UNI_ls.values()]
    time_values_REG_ls = [_ for _ in dct_REG_ls.values()]
    nodes_numbers = [_ for _ in dct_UNI_ls.keys()]
    plt.plot(nodes_numbers, time_values_UNI_m1, label='Uniform case, model 1', color='cornflowerblue')
    plt.plot(nodes_numbers, time_values_REG_m1, label='Regular case, model 1', color='sandybrown')
    plt.plot(nodes_numbers, time_values_UNI_m2, label='Uniform case, model 2', color='darkseagreen')
    plt.plot(nodes_numbers, time_values_REG_m2, label='Regular case, model 2', color='mediumvioletred')
    plt.plot(nodes_numbers, time_values_UNI_ls, label='Uniform case, local search', color='salmon')
    plt.plot(nodes_numbers, time_values_REG_ls, label='Regular case, local search', color='gold')
    plt.xlabel('Number of nodes')
    plt.ylabel('Computing time (in sec)')
    plt.title(f'Aver. time to find exact solution ({tests_number} tests per each number of nodes)')
    plt.grid(color='silver', linestyle='--', linewidth=0.5)
    plt.legend()
    plt.show()
    # plt.savefig(f'TSP_chart_{len(time_values)}nodes_{tests_number}tests_{int(avr_time_limit)}sec_time_limit.png')


class Evaluation:

    def __init__(self, n, flag):
        self.n = n
        self.m1 = CplexModel1(self.n, flag)
        self.m2 = CplexModel2(self.n, flag)
        self.ls = LocalSearch(self.n, flag)
        self.solution = None

    def optimize_model(self, m, nodes_number_time):
        m.optimize_model()
        nodes_number_time[self.n].append((m.solving_end - m.solving_start).total_seconds())

    def solve_ls(self, nodes_number_time):
        self.ls.optimize_model()
        nodes_number_time[self.n].append((self.ls.solving_end - self.ls.solving_start).total_seconds())

    def collect_obj_val(self, m, nodes_number_val):
        nodes_number_val[self.n].append(m.obj_val)


if __name__ == '__main__':
    nodes_number_time_UNI_m1 = {_: [] for _ in nodes_number_values}
    nodes_number_time_REG_m1 = {_: [] for _ in nodes_number_values}
    avr_time_UNI_m1, avr_time_REG_m1 = {}, {}

    nodes_number_time_UNI_m2 = {_: [] for _ in nodes_number_values}
    nodes_number_time_REG_m2 = {_: [] for _ in nodes_number_values}
    avr_time_UNI_m2, avr_time_REG_m2 = {}, {}

    nodes_number_time_UNI_ls = {_: [] for _ in nodes_number_values}
    nodes_number_time_REG_ls = {_: [] for _ in nodes_number_values}
    avr_time_UNI_ls, avr_time_REG_ls = {}, {}

    with Progress() as progress:
        nodes_pr = progress.add_task("[cyan]Number of nodes", total=len(nodes_number_values))
        tests_pr = progress.add_task(f"[magenta]{tests_number} tests for each number", total=tests_number)

        for i in nodes_number_values:

            for j in range(tests_number):
                evl_UNI = Evaluation(i, 'uni')
                evl_UNI.optimize_model(evl_UNI.m1, nodes_number_time_UNI_m1)
                evl_UNI.optimize_model(evl_UNI.m2, nodes_number_time_UNI_m2)
                evl_UNI.solve_ls(nodes_number_time_UNI_ls)

                evl_REG = Evaluation(i, 'reg')
                evl_REG.optimize_model(evl_REG.m1, nodes_number_time_REG_m1)
                evl_REG.optimize_model(evl_REG.m2, nodes_number_time_REG_m2)
                evl_REG.solve_ls(nodes_number_time_REG_ls)

                progress.update(tests_pr, completed=j + 1)

            curr_avr_time_UNI_m1 = sum(nodes_number_time_UNI_m1[i]) / tests_number
            curr_avr_time_UNI_m2 = sum(nodes_number_time_UNI_m2[i]) / tests_number
            curr_avr_time_UNI_ls = sum(nodes_number_time_UNI_ls[i]) / tests_number
            avr_time_UNI_m1[i] = curr_avr_time_UNI_m1
            avr_time_UNI_m2[i] = curr_avr_time_UNI_m2
            avr_time_UNI_ls[i] = curr_avr_time_UNI_ls

            curr_avr_time_REG_m1 = sum(nodes_number_time_REG_m1[i]) / tests_number
            curr_avr_time_REG_m2 = sum(nodes_number_time_REG_m2[i]) / tests_number
            curr_avr_time_REG_ls = sum(nodes_number_time_REG_ls[i]) / tests_number
            avr_time_REG_m1[i] = curr_avr_time_REG_m1
            avr_time_REG_m2[i] = curr_avr_time_REG_m2
            avr_time_REG_ls[i] = curr_avr_time_REG_ls

            progress.update(nodes_pr, completed=i - 3 + 1)

    # print(f'Number of nodes before stopping = {list(avr_time.keys())[-1]}')

    plot_res(avr_time_UNI_m1, avr_time_REG_m1,
             avr_time_UNI_m2, avr_time_REG_m2,
             avr_time_UNI_ls, avr_time_REG_ls)

