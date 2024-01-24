from configs import (nodes_number_values,
                     tests_number,
                     avr_time_limit,
                     curr_avr_time,
                     comp_time_intervals,
                     labeling_colors,
                     color_legend)
from model_1 import CplexModel1
from model_2 import CplexModel2
from matplotlib import pyplot as plt
from tqdm.notebook import tqdm_notebook
from rich.progress import Progress, track


def plot_res(dct_UNI_m1, dct_REG_m1, dct_UNI_m2, dct_REG_m2):
    time_values_UNI_m1 = [_ for _ in dct_UNI_m1.values()]
    time_values_REG_m1 = [_ for _ in dct_REG_m1.values()]
    time_values_UNI_m2 = [_ for _ in dct_UNI_m2.values()]
    time_values_REG_m2 = [_ for _ in dct_REG_m2.values()]
    nodes_numbers = [_ for _ in dct_UNI_m1.keys()]
    # plt.plot(nodes_number_values[:i], time_values[:i])
    plt.plot(nodes_numbers, time_values_UNI_m1, label='Uniform case, model 1')
    plt.plot(nodes_numbers, time_values_REG_m1, label='Regular case, model 1')
    plt.plot(nodes_numbers, time_values_UNI_m2, label='Uniform case, model 2')
    plt.plot(nodes_numbers, time_values_REG_m2, label='Regular case, model 2')
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
        self.solution = None

    def optimize_model(self, m, nodes_number_time):
        m.optimize_model()
        nodes_number_time[self.n].append((m.solving_end - m.solving_start).total_seconds())


if __name__ == '__main__':
    nodes_number_time_UNI_m1 = {_: [] for _ in nodes_number_values}
    nodes_number_time_REG_m1 = {_: [] for _ in nodes_number_values}
    avr_time_UNI_m1, avr_time_REG_m1 = {}, {}

    nodes_number_time_UNI_m2 = {_: [] for _ in nodes_number_values}
    nodes_number_time_REG_m2 = {_: [] for _ in nodes_number_values}
    avr_time_UNI_m2, avr_time_REG_m2 = {}, {}

    with Progress() as progress:
        nodes_pr = progress.add_task("[cyan]Computing for different number of nodes", total=len(nodes_number_values))
        tests_pr = progress.add_task(f"[magenta]Running {tests_number} tests for each number", total=tests_number)

        for i in nodes_number_values:
            # if curr_avr_time < avr_time_limit:
            # print(f'Node #{i}')

            for j in range(tests_number):
                evl_UNI = Evaluation(i, 'uni')
                evl_UNI.optimize_model(evl_UNI.m1, nodes_number_time_UNI_m1)
                evl_UNI.optimize_model(evl_UNI.m2, nodes_number_time_UNI_m2)

                evl_REG = Evaluation(i, 'reg')
                evl_REG.optimize_model(evl_REG.m1, nodes_number_time_REG_m1)
                evl_REG.optimize_model(evl_REG.m2, nodes_number_time_REG_m2)

                progress.update(tests_pr, completed=j + 1)

            curr_avr_time_UNI_m1 = sum(nodes_number_time_UNI_m1[i]) / tests_number
            curr_avr_time_UNI_m2 = sum(nodes_number_time_UNI_m2[i]) / tests_number
            avr_time_UNI_m1[i] = curr_avr_time_UNI_m1
            avr_time_UNI_m2[i] = curr_avr_time_UNI_m2

            curr_avr_time_REG_m1 = sum(nodes_number_time_REG_m1[i]) / tests_number
            curr_avr_time_REG_m2 = sum(nodes_number_time_REG_m2[i]) / tests_number
            avr_time_REG_m1[i] = curr_avr_time_REG_m1
            avr_time_REG_m2[i] = curr_avr_time_REG_m2

            progress.update(nodes_pr, completed=i - 3 + 1)

    # print(f'Number of nodes before stopping = {list(avr_time.keys())[-1]}')
    # plot_bar(curr_avr_time_UNI)
    plot_res(avr_time_UNI_m1, avr_time_REG_m1, avr_time_UNI_m2, avr_time_REG_m2)
