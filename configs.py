nodes_number = 5  # number of nodes
max_x = 100  # max x-coordinate value
max_y = 100  # max y-coordinate value
case_flag = 'uni'  # case indicator, 'uni' or 'reg'
init_path_flag = 'greedy'  # initial path indicator, 'greedy' or 'random'
ts_length = 7  # TL length
max_iter_number = 5  # max number of TS iterations


# REGULAR CASE
line_fract = 6  # fraction of nodes for the top line

# PERFORMANCE EVALUATION
max_N = 7  # number of nodes for model performance evaluation
nodes_number_values = tuple(range(4, max_N + 1))  # tuple of node number values: (4, ... , max_N)
tests_number = 10  # numer of tests for each number of nodes

# CALIBRATION
ts_list_length = tuple(range(1, max_N + 1))  # tuple of TL length values
max_iter = tuple(range(1, 4 * max_N + 1))  # tuple of max number of TS iterations values
samples_number = 30  # dataset size
