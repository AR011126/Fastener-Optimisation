# This is the top level controller/entry point for the application.
# It is responsible for setting up the application and starting the main loop.
# The role is roughly:
# 1. Load project configuration
# 2. Identify the input FEM
# 3. Call preprocessing
# 4. Build baseline fastener dataset
# 5. Generate candidate congifurations
# 6. Run analysis
# 7. Evaluate results
# 8. rank/export outputs


'''
Assumptions:
- The input fem file is in a specific format (each line is a data point, i.e. no continuation lines)
- The geometry data is identified by lines starting with "GRID" and the format of these lines is consistent (e.g. "GRID Node_id x y z"), no support for nodes in another system
- No material coordinate system data is included in the fem file, or if it is, it is not relevant to the geometry extraction
- units in mm
'''


import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from io_utils import validate_input_file
from build_baseline import build_baseline_model
from data_preprocessing import preprocess_fem_data
from parsers import node_data, CQUAD4_element_data, shell_node_data, SPC_node_data, cbar_element_data, fastener_database, pbar_property_data
from visualisation import mesh_visualisation, boundary_visualisation
from fastener_analysis import reduce_fastener_dataset, fastener_directionality, fastener_grouping, group_mapping, adjacent_spacing, terminal_boundary_spacing,compute_edge_distance
from mesh_analysis import mesh_boundary_generation
from design_space import build_group_design_variable_map, decode_design_vector,check_terminal_edge_constraints,check_spacing_constraint, evaluate_design_vector, build_initial_design_vector
from vector_eval import evaluate_design_vector
from candidate_generation import generate_random_design_vector, generate_lhs_samples
from evauate_population import evaluate_population
from initialise_population import initialise_population
from GA import non_dominated_sort, assign_rank_and_crowd_distance
from structural_eval import decoded_df_to_fastener_coordinates
from hypermesh_automation import launch_hypermesh
from test_population import build_test_population


def main():
    if len(sys.argv) < 2:
        raise ValueError("Please provide a Fem file path")
    
    fem_path = sys.argv[1]

    baseline_model = build_baseline_model(fem_path)
    #design_vector = generate_random_design_vector(baseline_model)

    #result = evaluate_design_vector(design_vector, baseline_model)
    #print(result)
    #mesh_visualisation(baseline_model)

    population = build_test_population()



#=======================TEMP NSGA TEST==================================
    fronts = assign_rank_and_crowd_distance(population)

    for front_index, front in enumerate(fronts):
        print(f"\nFront {front_index}")

        for candidate in front:
            print(
                "ID:", candidate['candidate_id'],
                "objectives:", candidate['objectives'],
                "violation:", candidate['total_constraint_violation'],
                "rank:", candidate['rank'],
                "crowding_distance:", candidate['crowding_distance']
            )






#======================================================================


#================TEMP STRUCTURAL EVALUATION TEST========================
    #evaluated_candidates = [candidate for candidate in population if not candidate['strength_results'].get('solver_skipped', False)]
    #print(f"{len(evaluated_candidates)} candidates reached structural evaluation\n")
    
    #for candidate in evaluated_candidates:
    #    print("Candidate:", candidate['candidate_id'])
    #    print(candidate['strength_results'])
    #   print()

#=========================================================================

#=================TEMP HYPERMESH AUTOMATION TEST==========================
#HM_EXE = r"C:\Program Files\Altair\2023\hwsolvers\bin\win64\hypermesh.exe"  #Update this path to the actual location of the Hypermesh executable on your system


#process = launch_hypermesh(HM_EXE)







#=========================================================================

    #print(feasible_count, "/", len(population_results))
    #print(population_results[0].keys())
    #fronts = non_dominated_sort(population_results)

    #for i, front in enumerate(fronts):
    #    print(f"Front {i}, size = {len(front)}")
#
#        for candidate in front:
#            print(
#                candidate["candidate_id"],
#                candidate["objectives"],
#                candidate["total_constraint_violation"],
#                candidate["is_feasible"]
#            )



    #print(baseline_model['fastener_candidates_df'].head())
    #print(baseline_model['terminal_fastener_df'])
    #print(baseline_model['cbar_df'].head())
    #print(baseline_model['group_bounds_df'])
if __name__ == "__main__":
    main()

  

    


    

   