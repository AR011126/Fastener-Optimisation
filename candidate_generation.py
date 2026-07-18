import random
from scipy.stats import qmc

# Before using LHS a random sampling is used to generate a design vector for testing as it is easier to debug
def generate_random_design_vector(baseline_model):
    variable_map = baseline_model['design_variable_map']
    group_bounds_df = baseline_model['group_bounds_df']
    vector_length = int(variable_map['gap_end_index'].max()) + 1
    design_vector = [0.0] * vector_length
    for _,row in variable_map.iterrows():
        group_id = row['Group_id']
        n_max = int(row['n_max'])
        bound_row = group_bounds_df[group_bounds_df['Group_id'] == group_id].iloc[0]
        diameter = float(bound_row['diameter'])
        start_edge_s = float(bound_row['start_edge_s'])
        end_edge_s = float(bound_row['end_edge_s'])
        max_span = end_edge_s - start_edge_s
        max_gap = 10 * diameter
        n_min_required = int(max_span // max_gap) + 1
        n_min_required = max(2, min(n_min_required, n_max))
        n_active = random.randint(n_min_required, n_max)
        left_offset = random.uniform(0.0, 2.5 * diameter)
        right_offset = random.uniform(0.0, 2.5 * diameter)
        design_vector[int(row['n_active_index'])] = n_active
        design_vector[int(row['left_offset_index'])] = left_offset
        design_vector[int(row['right_offset_index'])] = right_offset

        gap_start = int(row['gap_start_index'])
        gap_end = int(row['gap_end_index'])

        for idx in range(gap_start, gap_end + 1):
            design_vector[idx] = random.random()

    return design_vector

#Using LHS sampling to generate design vectors for 
def generate_lhs_samples(n_samples, baseline_model):
    variable_map = baseline_model['design_variable_map']
    group_bounds_df = baseline_model['group_bounds_df']
    vector_length = int(variable_map['gap_end_index'].max()) + 1
    lhs_dimension = vector_length
    sampler = qmc.LatinHypercube(d=lhs_dimension)
    lhs_matrix = sampler.random(n=n_samples)
    design_vectors = []
    for sample in lhs_matrix:
        design_vector = [0.0] * vector_length
        for _, row in variable_map.iterrows():
            group_id = row['Group_id']
            n_max = int(row['n_max'])
            bound_row = group_bounds_df[group_bounds_df['Group_id'] == group_id].iloc[0]
            diameter = float(bound_row['diameter'])

            n_active_index = int(row['n_active_index'])
            left_offset_index = int(row['left_offset_index'])
            right_offset_index = int(row['right_offset_index'])
            gap_start_index = int(row['gap_start_index'])
            gap_end_index = int(row['gap_end_index'])

            u_count = sample[n_active_index]
            u_left = sample[left_offset_index]
            u_right = sample[right_offset_index]
            
            max_span = float(bound_row['end_edge_s']) - float(bound_row['start_edge_s'])
            max_gap = 10 * diameter
            n_min_required = int(max_span // max_gap) + 1

            n_active = n_min_required + int(u_count * (n_max - n_min_required + 1))
            n_active = min(n_active, n_max)
            if n_active > n_max:
                n_active = n_max
            
            left_offset = u_left * 2.5 * diameter
            right_offset = u_right * 2.5 * diameter

            design_vector[n_active_index] = n_active
            design_vector[left_offset_index] = left_offset
            design_vector[right_offset_index] = right_offset

            for idx in range(gap_start_index, gap_end_index + 1):
                design_vector[idx] = sample[idx]

        design_vectors.append(design_vector)

    return design_vectors

