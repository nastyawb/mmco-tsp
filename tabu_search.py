import random
from configs import (max_x,
                     max_y)
from params import (get_nodes_arcs_starting_node,
                    get_distances_UNI,
                    get_distances_REG,
                    plot_grid)
from datetime import datetime
import matplotlib.pyplot as plt


def solve_ts(nodes_number, case_flag, init_path_flag, length, max_iter):
    ts = TabuSearch(nodes_number, case_flag, length, max_iter, init_path_flag)
    ts.optimize_model()
    # print(ts.costs)
    print(f'Starting node: {ts.starting_node}')
    plot_grid(ts.coords)

    if init_path_flag == 'greedy':
        print(ts.plot_path(ts.init_path[:-1]))
        print(f'Initial greedy path: {ts.init_path[:-1]}')
    else:
        print(ts.plot_path(ts.init_path[:-1]))
        print(f'Initial random path: {ts.init_path[:-1]}')
    print(ts.plot_path(ts.best_path))
    print(f'TS path: {ts.best_path}')
    print(ts.obj_val)


class TabuSearch:

    def __init__(self, N, case_flag, tl_len, n_iter, init_path_flag):
        self.N = N
        self.case_flag = case_flag
        self.init_path_flag = init_path_flag
        self.nodes, self.nodes_wo_starting_node, self.arcs, self.starting_node = get_nodes_arcs_starting_node(self.N)

        self.coords, self.costs = self.choose_case()

        self.solving_start = None
        self.solving_end = None

        self.init_path = None
        self.obj_val = None
        self.best_path = None

        self.path = []
        self.tl_len = tl_len
        self.n_iter = n_iter

    def choose_case(self):
        if self.case_flag == 'uni':
            self.coords, self.costs = get_distances_UNI(self.N, max_x, max_y)
        elif self.case_flag == 'reg':
            self.coords, self.costs = get_distances_REG(self.N, max_x, max_y)
        return self.coords, self.costs

    def get_initial_path_random(self):  # computing initial random path
        # random.seed(11)
        shuffled_nodes = random.sample(self.nodes, k=len(self.nodes))
        init_path = shuffled_nodes[shuffled_nodes.index(self.starting_node):] + \
                    shuffled_nodes[:shuffled_nodes.index(self.starting_node)]
        # print(f'Init path: {init_path}')
        init_path.append(self.starting_node)
        return init_path

    def get_initial_path_greedy(self):  # computing initial greedy path
        init_path = [self.starting_node]
        for node in range(len(self.nodes_wo_starting_node)):
            pot_sotred_by_cost = sorted(range(len(self.costs[init_path[-1]])),
                                        key=lambda k: self.costs[init_path[-1]][k])
            flag_added = 0
            for i in range(len(pot_sotred_by_cost)):
                if self.costs[init_path[-1]][pot_sotred_by_cost[i]] != 0 \
                        and flag_added == 0 and pot_sotred_by_cost[i] not in init_path:
                    init_path.append(pot_sotred_by_cost[i])
                    flag_added = 1
        # print(f'Init path: {init_path}')
        init_path.append(self.starting_node)
        return init_path

    def compute_path_cost(self, path):  # cost of the whole path
        cost_value = 0
        for i in range(len(path) - 1):
            cost_value += self.costs[path[i]][path[i + 1]]
        return cost_value

    def optimize_model(self):
        if self.init_path_flag == 'random':
            path = self.get_initial_path_random()
        else:
            path = self.get_initial_path_greedy()
        self.init_path = path
        best_cost = self.compute_path_cost(path)
        # print(f'Init cost: {best_cost}')

        tabu_list = []  # TL
        k = 0   # iterations counter
        improved = True

        self.solving_start = datetime.now()  # for evaluation

        while k < self.n_iter and improved:
            improved = False
            for i in range(1, len(path) - 2):
                for j in range(i + 2, len(path)):

                    old_archs = ((path[i - 1], path[i]), (path[j - 1], path[j]))  # current arcs
                    new_archs = ((path[i - 1], path[j - 1]), (path[i], path[j]))  # potential arcs after swapping
                    new_cost = best_cost - \
                               self.costs[old_archs[0][0]][old_archs[0][1]] - \
                               self.costs[old_archs[1][0]][old_archs[1][1]] + \
                               self.costs[new_archs[0][0]][new_archs[0][1]] + \
                               self.costs[new_archs[1][0]][new_archs[1][1]]         # cost after swapping
                    if new_archs not in tabu_list[-self.tl_len:] and new_cost < best_cost:
                        new_path = path[:]                      # swapping
                        new_path[i:j] = path[j - 1:i - 1:-1]
                        tabu_list.append(new_archs)             # updating TL
                        # print(f'TL {tabu_list}')

                        best_cost = new_cost                    # updating cost
                        path = new_path                         # updating path
                        # print('k =', k)
                        # print(f'Path: {path}, Cost: {best_cost}, Subtour: {i} - {j - 1}')
                        improved = True
                        k += 1

                        # print(tabu_list)

        self.solving_end = datetime.now()   # for evaluation
        self.obj_val = best_cost
        self.best_path = path[:-1]
        # print(f'Improved path: {path}')
        # print(f'Improved cost = {best_cost}')
        return path

    def plot_path(self, path):
        self.path = path

        x_coord = [self.coords[node][0] for node in self.path]
        y_coord = [self.coords[node][1] for node in self.path]

        plt.figure(figsize=(5, 4))
        plt.plot(x_coord, y_coord, '-o', c='indianred', zorder=2)
        plt.xlabel('x')
        plt.ylabel('y')
        plt.grid(color='silver', linestyle='--', linewidth=0.5, zorder=1)
        plt.title(f'Computed path where starting node = {self.starting_node}')
        i = 0
        for x, y in zip(x_coord, y_coord):
            plt.annotate(f'{int(self.path[i])}',  # this is the text
                         (x, y),  # these are the coordinates to position the label
                         textcoords="offset points",  # how to position the text
                         xytext=(0, 5),  # distance from text to points (x,y)
                         ha='center')  # horizontal alignment can be left, right or center

            i += 1
        plt.show()


if __name__ == '__main__':
    solve_ts(9, 'uni', 'greedy', 9, 4)
