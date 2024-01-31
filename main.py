from configs import (nodes_number,
                     case_flag,
                     init_path_flag,
                     ts_length,
                     max_iter_number)

from model_1 import solve_m1
from model_2 import solve_m2
from tabu_search import solve_ts
from calibration import calibrate
from performance import evaluate
from obj_f_comp import compare_obj_values

if __name__ == '__main__':
    # solve_m1(nodes_number, case_flag)
    # solve_m2(nodes_number, case_flag)
    # solve_ts(nodes_number, case_flag, init_path_flag, ts_length, max_iter_number)
    # calibrate(case_flag, init_path_flag)
    # evaluate(init_path_flag)
    compare_obj_values('greedy')
