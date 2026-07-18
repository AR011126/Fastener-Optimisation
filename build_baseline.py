import sys
from pathlib import Path
from parsers import preprocess_fem_data, node_data, CQUAD4_element_data, shell_node_data, SPC_node_data,cbar_element_data,fastener_database,pbar_property_data
from fastener_analysis import reduce_fastener_dataset, fastener_directionality, fastener_grouping, group_mapping, adjacent_spacing, terminal_boundary_spacing, compute_edge_distance, build_pbar_diameter_lookup
from mesh_analysis import mesh_boundary_generation
from design_space import build_group_design_variable_map, build_group_position_bounds, build_group_design_df, build_initial_design_vector, decode_design_vector
from tests import test_projection_reconstruction

import pandas as pd


pd.set_option('display.max_columns', None)
pd.set_option('display.width', 2000)
pd.set_option('display.expand_frame_repr', False)

def load_fem_file(fem_path):
    input_path = Path(fem_path)

    if not input_path.exists():
        print(f"File doesn't exist: {input_path}")
        sys.exit(1)
    
    if not input_path.is_file():
        print(f"File is not valid: {input_path}")
        sys.exit(1)
    
    if input_path.suffix.lower() != '.fem':
        print(f"File is not a .fem file: {input_path}")
        sys.exit(1)


    with open(input_path, 'r') as f:
        fem_raw_data = f.readlines()

    return fem_raw_data

def build_baseline_model(fem_path):

    fem_raw_data = load_fem_file(fem_path)
    model_record = preprocess_fem_data(fem_raw_data)
    node_df = node_data(model_record)
    cquad4_df = CQUAD4_element_data(model_record)
    shell_node_df = shell_node_data(cquad4_df, node_df)
    shell_node_ids = set()
    spc_df = SPC_node_data(model_record)
    pbar_df = pbar_property_data(model_record)
    diameter_lookup = build_pbar_diameter_lookup(pbar_df)
    cbar_df = cbar_element_data(model_record)
    cbar_df["diameter"] = cbar_df["PID"].map(diameter_lookup)
    fastener_df, shell_nodes_ids, SPC_nodes_ids = fastener_database(cbar_df, shell_node_df, spc_df, node_df)
    fastener_candidates_df = reduce_fastener_dataset(fastener_df)
    fastener_candidates_df = fastener_directionality(fastener_candidates_df, fastener_df)
    fastener_candidates_df = fastener_grouping(fastener_candidates_df)
    fastener_candidates_df = fastener_candidates_df.rename(columns={"Group id" : "group_id"})
    fastener_candidates_df = group_mapping(fastener_candidates_df)
    fastener_candidates_df = adjacent_spacing(fastener_candidates_df)
    fastener_candidates_df['diameter'] = fastener_candidates_df.index.map(cbar_df['diameter'])
    error_df = test_projection_reconstruction(fastener_candidates_df, tolerance = 1e-6)
    mesh_edges = mesh_boundary_generation(cquad4_df, node_df)
    terminal_fastener_df = terminal_boundary_spacing(mesh_edges, fastener_candidates_df)
    terminal_fastener_df = compute_edge_distance(terminal_fastener_df, mesh_edges)
    group_design_df = build_group_design_df(fastener_candidates_df)
    design_variable_map = build_group_design_variable_map(group_design_df)
    group_bounds_df = build_group_position_bounds(terminal_fastener_df)
    initial_design_vector = build_initial_design_vector(fastener_candidates_df, design_variable_map, group_bounds_df)    




    baseline_model = {
        #file info
        "fem_path" : fem_path,
        "fem_raw_data" : fem_raw_data,
        #parsed data
        "model_record" : model_record,
        "node_df" : node_df,
        "cquad4_df" : cquad4_df,
        "shell_node_df" : shell_node_df,
        "spc_df" : spc_df,
        "cbar_df" : cbar_df,
        #dervied geometry
        "mesh_edges": mesh_edges,
        #fastener data
        "fastener_df": fastener_df,
        "fastener_candidates_df" : fastener_candidates_df,
        "terminal_fastener_df" : terminal_fastener_df,
        "design_variable_map" : design_variable_map,
        "pbar_df": pbar_df,
        "group_bounds_df" : group_bounds_df,
        "baseline_fem_path" : "path/to/baseline.fem",
        "run_directory" : "runs"

    }

    return baseline_model


