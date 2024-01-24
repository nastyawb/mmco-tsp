import numpy as np
import random
from math import sqrt
import matplotlib.pyplot as plt
from configs import line_fract


def get_nodes_arcs_starting_node(N):
    nodes = tuple(_ for _ in range(N))  # set of nodes
    arcs = tuple((i, j) for i in nodes for j in nodes  # set of arcs
                 if (i != j))
    # random.seed(10)
    starting_node = random.choice(nodes)  # arbitrarily selected starting node
    nodes_wo_starting_node = tuple(_ for _ in nodes if _ != starting_node)  # set of nodes without starting_node

    return nodes, nodes_wo_starting_node, arcs, starting_node


# UNIFORM CASE
def get_coordinates_UNI(n_nodes, max_x, max_y):
    # random.seed(10)

    coord = {}
    existing_coord = []
    for i in range(n_nodes):
        flag = 0
        while flag == 0:
            (x, y) = (random.randint(0, max_x), random.randint(0, max_y))
            if (x, y) not in existing_coord:
                flag = 1
                coord[i] = (x, y)
                existing_coord.append((x, y))

    # x, y = [], []
    # for key, value in coord.items():
    #     x.append(value[0])
    #     y.append(value[1])
    #
    # plt.figure(figsize=(5, 4))
    # plt.scatter(x, y, c='indianred', zorder=2)
    # plt.xlabel('x')
    # plt.ylabel('y')
    # plt.rc('font', size=7)
    # plt.grid(color='silver', linestyle='--', linewidth=0.5, zorder=1)
    # plt.title(f'Uniform grid with {n_nodes} nodes')
    # i = 0
    # for x_, y_ in zip(x, y):
    #     plt.annotate(f'{int(list(coord.keys())[i])}',  # this is the text
    #                  (x_, y_),  # these are the coordinates to position the label
    #                  textcoords="offset points",  # how to position the text
    #                  xytext=(0, 5),  # distance from text to points (x,y)
    #                  ha='center')  # horizontal alignment can be left, right or center
    #     i += 1
    # plt.show()

    return coord


def get_distances_UNI(n_nodes, max_x, max_y):
    coord = get_coordinates_UNI(n_nodes, max_x, max_y)
    n = len(coord)
    distances = np.empty((n, n))
    for i in range(n):
        for j in range(n):
            distances[i][j] = sqrt((coord[i][0] - coord[j][0]) ** 2 + (coord[i][1] - coord[j][1]) ** 2)
    np.fill_diagonal(distances, 0)  # giving large values to costs of diagonal elements
    # print(distances)
    return coord, distances


# REGULAR CASE
def get_area_size_line_size(k, n_sq):
    # random.seed(10)

    overall = k
    line_size = overall // line_fract
    overall -= line_size
    k_rem = overall
    k_in_sq_vals = []
    k_added = 0
    for i in range(n_sq - 1):
        k_in_sq_vals.append(random.randint(2, int(k_rem * 0.6)))
        k_added += k_in_sq_vals[-1]
        k_rem -= k_in_sq_vals[-1]
    k_in_sq_vals.append(overall - k_added)

    xy_sizes = []
    k_used = 0
    for k_in_sq in k_in_sq_vals:
        x_s, y_s = 2, 1
        for i in range(2, k_in_sq // 2 + 1):
            if i >= k_in_sq // i and i - k_in_sq // i <= i // 2:
                x_s = k_in_sq // i
                y_s = i
        xy_sizes.append((x_s, y_s))
        k_used += xy_sizes[-1][0] * xy_sizes[-1][1]
    line_size += overall - k_used
    # print(line_size, xy_sizes)
    return xy_sizes, line_size


def get_coordinates_REG(n_nodes, max_x, max_y):
    # random.seed(10)

    if n_nodes < 15:
        n_sq = 2
    elif n_nodes < 35:
        n_sq = random.randint(2, 3)
    else:
        n_sq = random.randint(2, 4)
    xy_sizes, nodes_in_line = get_area_size_line_size(n_nodes, n_sq)

    dist_x = max_x // (sum([xy_size[0] for xy_size in xy_sizes]) * line_fract // 3.5)   # distance between nodes in an area, Ox = max_x // reg_areas_number
    dist_y = max_y // (max([xy_size[1] for xy_size in xy_sizes]) * line_fract // 4)  # distance between nodes in an area, Oy
    dist_sq = (max_x - (sum([xy_size[0] for xy_size in xy_sizes]) - 1) * dist_x) / (n_sq - 1)  # distance between areas, Ox

    sq_coord = {}
    nodes_added = 0
    x_occ = 0
    for s in range(len(xy_sizes)):
        (x_size, y_size) = xy_sizes[s]
        nodes_in_sq = x_size * y_size

        if s != n_sq // 2:
            loc_y = random.randint(max_y // 10, max_y - (y_size - 1) * dist_y - max_y // 10)
            for i in range(nodes_in_sq):
                sq_coord[nodes_added + i] = (x_occ + i % x_size * dist_x,
                                             i // x_size * dist_y + loc_y)
        else:
            for i in range(nodes_in_sq):
                sq_coord[nodes_added + i] = (x_occ + i % x_size * dist_x,
                                             i // x_size * dist_y)

        nodes_added += x_size * y_size
        x_occ += x_size * dist_x + dist_sq

    if nodes_in_line > 1:
        delta_line_x = max_x / (nodes_in_line - 1)
    else:
        delta_line_x = max_x / 2
    nodes_rect = sum([x_size * y_size for (x_size, y_size) in xy_sizes])
    for i in range(nodes_in_line):
        if nodes_in_line > 1:
            sq_coord[nodes_rect + i] = (i * delta_line_x, max_y)
        else:
            sq_coord[nodes_rect + i] = (delta_line_x, max_y)

    # x, y = [], []
    # for key, value in sq_coord.items():
    #     x.append(value[0])
    #     y.append(value[1])
    #
    # plt.figure(figsize=(5, 4))
    # plt.scatter(x, y, c='indianred', zorder=2)
    # plt.xlabel('x')
    # plt.ylabel('y')
    # plt.rc('font', size=7)
    # plt.grid(color='silver', linestyle='--', linewidth=0.5, zorder=1)
    # plt.title(f'Regular grid with {n_nodes} nodes and {n_sq + 1} separated areas')
    # i = 0
    # for x_, y_ in zip(x, y):
    #     plt.annotate(f'{int(list(sq_coord.keys())[i])}',  # this is the text
    #                  (x_, y_),  # these are the coordinates to position the label
    #                  textcoords="offset points",  # how to position the text
    #                  xytext=(0, 5),  # distance from text to points (x,y)
    #                  ha='center')  # horizontal alignment can be left, right or center
    #     i += 1
    # plt.show()
    # plt.savefig(f'reg_{n_nodes}nodes.png')
    return sq_coord


def get_distances_REG(n_nodes, max_x, max_y):
    sq_coord = get_coordinates_REG(n_nodes, max_x, max_y)
    inf_cost = 5 * sqrt(max_x ** 2 + max_y ** 2)
    n = len(sq_coord)
    distances = np.empty((n, n))
    for i in range(n):
        for j in range(n):
            distances[i][j] = sqrt((sq_coord[i][0] - sq_coord[j][0]) ** 2 + (sq_coord[i][1] - sq_coord[j][1]) ** 2)
    np.fill_diagonal(distances, inf_cost)  # giving large values to costs of diagonal elements
    # print(distances)
    return sq_coord, distances


if __name__ == '__main__':
    # costs = get_distances_UNI(15, 50, 50)
    # print(costs)
    get_coordinates_REG(60, 100, 100)
    # get_coordinates_UNI(55, 100, 100)
