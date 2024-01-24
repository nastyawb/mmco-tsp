N = 5  # number of nodes
max_x = 100
max_y = 100

# UNIFORM CASE


# REGULAR CASE
line_fract = 6  # number of distinct regions (rectangles)
dist_x = 3  # distance between nodes in an area, Ox = max_x // reg_areas_number //
dist_y = 6  # distance between nodes in an area, Oy
dist_sq = 20  # distance between areas, Ox
dist_line = 20  # distance between all areas and a line, Oy

# EVALUATION
max_N = 30  # number of nodes for model performance evaluation
nodes_number_values = tuple(range(4, max_N))  # tuple of different values: (4, ... , max_N - 1)
tests_number = 10  # numer of tests we run for each number of nodes
curr_avr_time = -1  # starting value of average computing time for performance evaluation

# CALIBRATION
ts_list_length = tuple(range(max_N))
max_iter = tuple(range(10))
samples_number = 30

# comp_time_intervals = [[0, 0.1], [0.1 + 1e-5, 0.5], [0.5 + 1e-5, 1], [1 + 1e-5, 5], [5 + 1e-5, 10]]
comp_time_intervals = [[0, 0.1],
                       [0.1 + 1e-5, 0.5],
                       [0.5 + 1e-5, 1],
                       [1 + 1e-5, 5],
                       [5 + 1e-5, 10]]  # time intervals under consideration
avr_time_limit = comp_time_intervals[-1][-1] + 1e-5  # limit for average computing time

# for visualization
labeling_colors = ['darkseagreen', 'skyblue', 'mediumpurple', 'palevioletred', 'darksalmon', 'tomato']
color_legend = {}
for i in range(len(comp_time_intervals)):
    color_legend[f'up to {comp_time_intervals[i][-1]} sec'] = labeling_colors[i]
color_legend[f'more than {comp_time_intervals[-1][-1]} sec'] = labeling_colors[-1]
