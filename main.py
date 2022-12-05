import main_comp_vs_comp as cvsc
import main_human_vs_comp as hvsc
import main_human_vs_human as hvsh
import main_eval as eval

runner_map = {
  0: hvsc.run,  # human vs computer
  1: cvsc.run,  # computer vs computer
  2: hvsh.run,  # human vs human
  3: eval.run,  # evaluation selected Scorers
}

runner_map[0]()
