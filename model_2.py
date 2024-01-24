from configs import (max_x,
                     max_y)
from params import (get_nodes_arcs_starting_node,
                    get_distances_UNI,
                    get_distances_REG)
from docplex.mp.model import (Model)
import operator
from datetime import datetime
import matplotlib.pyplot as plt


def solve_m2(nodes_number, case_flag):
    mdl = CplexModel2(nodes_number, case_flag)
    mdl.optimize_model()
    # print(mdl.costs)

    print(f'Starting node: {mdl.starting_node}')
    sol = mdl.get_solution()
    print(f'Path: {sol}')
    print(f'Obj value = {mdl.solved_m.get_objective_value()}')

    mdl.plot_path()


class CplexModel2:

    def __init__(self, N, case_flag):
        self.case_flag = case_flag
        self.N = N
        self.nodes, self.nodes_wo_starting_node, self.arcs, self.starting_node = get_nodes_arcs_starting_node(self.N)

        self.coords, self.costs = self.choose_case()

        self.m = Model(name='TSP 2')
        self.solved_m = None

        self.x = None
        self.y = None

        self.solution, self.solution_sorted = None, None
        self.path = []
        self.obj_val = None

        self.solving_start = None
        self.solving_end = None

    def choose_case(self):
        if self.case_flag == 'uni':
            self.coords, self.costs = get_distances_UNI(self.N, max_x, max_y)
        elif self.case_flag == 'reg':
            self.coords, self.costs = get_distances_REG(self.N, max_x, max_y)
        return self.coords, self.costs

    def add_vars(self):
        # print('Creating variables...')

        self.y = self.m.integer_var_dict(keys=self.nodes,
                                         lb={_: 0 for _ in self.nodes},
                                         ub={_: self.N for _ in self.nodes},
                                         name='order_')
        self.x = self.m.binary_var_dict(keys=self.arcs,
                                        name='if__flow_')

    def add_constraints(self):
        # print('Adding constraints...')

        # enter each node once
        self.m.add_constraints((self.m.sum(self.x[(i, j)] for j in self.nodes if (i, j) in self.arcs) == 1
                                for i in self.nodes),
                               names=[f'shipping to 1 arc, node {i}' for i in self.nodes])

        # leave each node once
        self.m.add_constraints((self.m.sum(self.x[(i, j)] for i in self.nodes if (i, j) in self.arcs) == 1
                                for j in self.nodes),
                               names=[f'shipping from 1 arc, node {j}' for j in self.nodes])

        # Subtour breaking:
        # if no arc 'i<-->j', then any order 'i<-->j'
        # otherwise, 'first i is visited, then j'
        self.m.add_constraints((self.y[i] - self.y[j] + 1 <= (self.N - 1) * (1 - self.x[(i, j)])
                                for i in self.nodes_wo_starting_node
                                for j in self.nodes_wo_starting_node
                                if i != j),
                               names=[f'flow__units, arc{(i, j)}' for (i, j) in self.arcs
                                      if j != self.starting_node])

        self.m.add_constraints((1 <= self.y[i])
                               for i in self.nodes_wo_starting_node)

        self.m.add_constraints((self.y[i] <= self.N - 1)
                               for i in self.nodes_wo_starting_node)

    def set_objective_function(self):
        # print('Setting objective function...')

        self.m.minimize(self.m.sum(self.costs[(i, j)] * self.x[(i, j)] for (i, j) in self.arcs))

    def optimize_model(self):
        self.add_vars()
        self.set_objective_function()
        self.add_constraints()
        # self.m.export_as_lp('tsp2.lp')

        # print('Solving the model...')
        self.solving_start = datetime.now()
        self.solved_m = self.m.solve(log_output=False)
        self.solving_end = datetime.now()
        self.obj_val = self.solved_m.get_objective_value()
        # self.solved_m.display()

    def get_solution(self):
        self.solution = {k: self.y[k].solution_value for k in self.nodes}
        self.solution_sorted = [_ for _ in dict(sorted(self.solution.items(), key=operator.itemgetter(1), reverse=False)).keys()]
        self.path = self.solution_sorted

        return self.path

    def plot_path(self):
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
    solve_m2(9, 'reg')
