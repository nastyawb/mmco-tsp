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

    coord = {}  # dict -- {node index: (x, y)}
    existing_coord = []
    for i in range(n_nodes):
        flag = 0
        while flag == 0:
            (x, y) = (random.randint(0, max_x), random.randint(0, max_y))  # if generated (x, y) has not been
            if (x, y) not in existing_coord:  # previously generated, then record
                flag = 1
                coord[i] = (x, y)
                existing_coord.append((x, y))
    # plot_grid(coord)
    return coord


def get_distances_UNI(n_nodes, max_x, max_y):  # computing distances: d = (x1 - x2)^2 + (y1 - y2)^2
    coord = get_coordinates_UNI(n_nodes, max_x, max_y)
    n = len(coord)
    distances = np.empty((n, n))
    for i in range(n):
        for j in range(n):
            distances[i][j] = sqrt((coord[i][0] - coord[j][0]) ** 2 + (coord[i][1] - coord[j][1]) ** 2)
    np.fill_diagonal(distances, 0)  # filling diagonal with 0s
    # print(distances)
    return coord, distances


# REGULAR CASE
def get_area_size_line_size(k, n_sq):
    # random.seed(10)

    overall = k
    line_size = overall // line_fract  # size of the top line
    overall -= line_size
    k_rem = overall  # remaining nodes
    k_in_sq_vals = []  # list of numbers of nodes in rectangles
    k_added = 0  # initial overall number of nodes assigned to rectangles
    for i in range(n_sq - 1):
        k_in_sq_vals.append(random.randint(2, int(k_rem * 0.6)))
        k_added += k_in_sq_vals[-1]
        k_rem -= k_in_sq_vals[-1]
    k_in_sq_vals.append(overall - k_added)

    xy_sizes = []  # list of (width, length) pairs
    k_used = 0  # number of nodes assigned to rectangles taking into account width and length
    for k_in_sq in k_in_sq_vals:
        x_s, y_s = 2, 1  # starting (width, length) values
        for i in range(2, k_in_sq // 2 + 1):
            if i >= k_in_sq // i and i - k_in_sq // i <= i // 2:  # if potential length >= width
                x_s = k_in_sq // i  # and (length - width) <= length / 2,
                y_s = i  # then update (width, length) values
        xy_sizes.append((x_s, y_s))
        k_used += xy_sizes[-1][0] * xy_sizes[-1][1]
    line_size += overall - k_used
    # print(line_size, xy_sizes)
    return xy_sizes, line_size


def get_coordinates_REG(n_nodes, max_x, max_y):
    # random.seed(10)

    if n_nodes < 15:  # determining number of rectangles
        n_sq = 2
    elif n_nodes < 30:
        n_sq = random.randint(2, 3)
    else:
        n_sq = random.randint(2, 4)
    xy_sizes, nodes_in_line = get_area_size_line_size(n_nodes, n_sq)

    # distance between nodes in an area, Ox
    dist_x = max_x // (sum([xy_size[0] for xy_size in
                            xy_sizes]) * line_fract // 3.5)
    # distance between nodes in an area, Oy
    dist_y = max_y // (
            max([xy_size[1] for xy_size in xy_sizes]) * line_fract // 4)
    # distance between areas, Ox
    dist_sq = (max_x - (sum([xy_size[0] for xy_size in xy_sizes]) - 1) * dist_x) / (
            n_sq - 1)

    # distance between nodes in the top line
    if nodes_in_line > 1:
        delta_line_x = max_x / (nodes_in_line - 1)
    else:
        delta_line_x = max_x / 2

    sq_coord = {}  # dict -- {node index: (x, y)}
    nodes_rect = sum([x_size * y_size for (x_size, y_size) in xy_sizes])  # counter of nodes in the top line
    for i in range(nodes_in_line):  # computing coordinates for the line nodes
        if nodes_in_line > 1:
            sq_coord[nodes_rect + i] = (i * delta_line_x, max_y)
        else:
            sq_coord[nodes_rect + i] = (delta_line_x, max_y)

    nodes_added = 0  # counter of nodes in the rectangles
    x_occ = 0  # current 'occupied' point on x-coordinate
    for s in range(len(xy_sizes)):
        (x_size, y_size) = xy_sizes[s]
        nodes_in_sq = x_size * y_size

        if s != n_sq // 2:  # if not middle rectangle, then generating rectangle shift on y-axis
            loc_y = random.randint(max_y // 10, max_y - (y_size - 1) * dist_y - max_y // 10)
            for i in range(nodes_in_sq):
                sq_coord[nodes_added + i] = (x_occ + i % x_size * dist_x,
                                             i // x_size * dist_y + loc_y)
        else:  # fixing middle rectangle so that its lowest row sticks to y = 0
            for i in range(nodes_in_sq):
                sq_coord[nodes_added + i] = (x_occ + i % x_size * dist_x,
                                             i // x_size * dist_y)

        nodes_added += x_size * y_size
        x_occ += x_size * dist_x + dist_sq

    # plot_grid(sq_coord)
    return sq_coord


def get_distances_REG(n_nodes, max_x, max_y):  # computing distances: d = (x1 - x2)^2 + (y1 - y2)^2
    sq_coord = get_coordinates_REG(n_nodes, max_x, max_y)
    n = len(sq_coord)
    distances = np.empty((n, n))
    for i in range(n):
        for j in range(n):
            distances[i][j] = sqrt((sq_coord[i][0] - sq_coord[j][0]) ** 2 + (sq_coord[i][1] - sq_coord[j][1]) ** 2)
    np.fill_diagonal(distances, 0)  # filling diagonal with 0s
    # print(distances)
    return sq_coord, distances


def plot_grid(coord):  # visualisation
    x, y = [], []
    for key, value in coord.items():
        x.append(value[0])
        y.append(value[1])

    plt.figure(figsize=(5, 4))

    plt.rc('font', size=7)
    plt.scatter(x, y, c='indianred', zorder=2)
    plt.xlabel('x', fontsize=7)
    plt.ylabel('y', fontsize=7)
    plt.title(f'Grid with {len(x)} nodes')
    # plt.rc('font', size=7)
    plt.grid(color='silver', linestyle='--', linewidth=0.5, zorder=1)
    i = 0
    for x_, y_ in zip(x, y):
        plt.annotate(f'{int(list(coord.keys())[i])}',  # this is the text
                     (x_, y_),  # these are the coordinates to position the label
                     textcoords="offset points",  # how to position the text
                     xytext=(0, 5),  # distance from text to points (x,y)
                     ha='center')  # horizontal alignment can be left, right or center
        i += 1
    plt.show()
    # plt.savefig(f'reg_{n_nodes}nodes.png')


if __name__ == '__main__':
    # costs = get_distances_UNI(15, 50, 50)
    # print(costs)
    coord = get_coordinates_REG(100, 100, 100)
    # coord = get_coordinates_UNI(55, 100, 100)
    plot_grid(coord)
