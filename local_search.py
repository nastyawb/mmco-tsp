import random
from configs import (max_x,
                     max_y)
from params import (get_nodes_arcs_starting_node,
                    get_distances_UNI,
                    get_distances_REG)
from datetime import datetime
import matplotlib.pyplot as plt


class LocalSearch:

    def __init__(self, N, flag, tl_len, n_iter):
        self.N = N
        self.flag = flag
        self.nodes, self.nodes_wo_starting_node, self.arcs, self.starting_node = get_nodes_arcs_starting_node(self.N)

        self.coords, self.costs = self.choose_case()

        self.solving_start = None
        self.solving_end = None

        self.obj_val = None
        self.best_path = None

        self.path = []
        self.tl_len = tl_len
        self.n_iter = n_iter

    def choose_case(self):
        if self.flag == 'uni':
            self.coords, self.costs = get_distances_UNI(self.N, max_x, max_y)
        elif self.flag == 'reg':
            self.coords, self.costs = get_distances_REG(self.N, max_x, max_y)
        return self.coords, self.costs

    def get_initial_path_1(self):
        # print(f'Starting node: {self.starting_node}')
        # random.seed(11)
        perturbed_nodes = random.sample(self.nodes, k=len(self.nodes))
        # print(f'Before aligning: {perturbed_nodes}')
        init_path = perturbed_nodes[perturbed_nodes.index(self.starting_node):] + \
                    perturbed_nodes[:perturbed_nodes.index(self.starting_node)]
        # print(perturbed_nodes[perturbed_nodes.index(self.starting_node):],
        #      perturbed_nodes[:perturbed_nodes.index(self.starting_node)])
        # print(f'Perturbed path: {init_path}')
        return init_path

    def get_initial_path(self):
        init_path = [self.starting_node]
        for node in range(len(self.nodes_wo_starting_node)):
            pot_sotred_by_cost = sorted(range(len(self.costs[init_path[-1]])),
                                        key=lambda k: self.costs[init_path[-1]][k])
            flag_added = 0
            for i in range(len(pot_sotred_by_cost)):
                if self.costs[init_path[-1]][pot_sotred_by_cost[i]] != 0 and flag_added == 0 and pot_sotred_by_cost[
                    i] not in init_path:
                    init_path.append(pot_sotred_by_cost[i])
                    flag_added = 1
        # print(f'Init path: {init_path}')
        return init_path

    def compute_path_cost(self, path):
        # print('Costs:')
        # print(self.costs)
        cost_value = 0
        for i in range(len(path) - 1):
            cost_value += self.costs[path[i]][path[i + 1]]
        # print(f'Path: {path}, Cost: {cost_value}')
        return cost_value

    def optimize_model(self):
        path = self.get_initial_path()
        best_cost = self.compute_path_cost(path)

        tabu_list = []
        k = 0
        improved = True

        iters = 0

        self.solving_start = datetime.now()

        while k < self.n_iter and improved:
            improved = False
            # print(f'k = {k}')
            for i in range(1, len(path) - 2):
                for j in range(i + 2, len(path)):

                    old_archs = ((path[i - 1], path[i]), (path[j - 1], path[j]))
                    new_archs = ((path[i - 1], path[j - 1]), (path[i], path[j]))
                    new_cost = best_cost - \
                               self.costs[old_archs[0][0]][old_archs[0][1]] - \
                               self.costs[old_archs[1][0]][old_archs[1][1]] + \
                               self.costs[new_archs[0][0]][new_archs[0][1]] + \
                               self.costs[new_archs[1][0]][new_archs[1][1]]
                    if new_archs not in tabu_list[-self.tl_len:] and new_cost < best_cost:
                        # curr_cost = best_cost - self.costs[path[i - 1]][path[i]] - self.costs[path[j - 1]][
                        #     path[j]] + \
                        #             self.costs[path[i - 1]][path[j - 1]] + self.costs[path[i]][path[j]]
                        new_path = path[:]
                        new_path[i:j] = path[j - 1:i - 1:-1]
                        tabu_list.append(new_archs)
                        # print(f'TL {tabu_list}')

                        best_cost = new_cost
                        path = new_path
                        # print(f'Path: {path}, Cost: {best_cost}, Subtour: {i} - {j - 1}')
                        improved = True
                        k += 1
                        # print('k =', k)
                        # print(tabu_list)

        self.solving_end = datetime.now()
        self.obj_val = best_cost + self.costs[path[-1]][self.starting_node]
        self.best_path = path
        # print(f'Improved path: {path}')
        # print(f'Improved cost = {best_cost}')
        return path

    def plot_path(self, path):
        self.path = path

        x_coord = [self.coords[node][0] for node in self.path]
        y_coord = [self.coords[node][1] for node in self.path]

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
    ls = LocalSearch(22, 'reg', 6, 5)
    ls.optimize_model()
    print(ls.plot_path(ls.get_initial_path()))
    print(ls.plot_path(ls.best_path))
    print(ls.obj_val)
