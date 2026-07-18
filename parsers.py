import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from io_utils import validate_input_file
from data_preprocessing import preprocess_fem_data


def node_data(model_record):
    #This will take the model data and extract the geometry as numerical data that can be used for the rest of the program, built in a dataframe
    node_df = pd.DataFrame(columns=["Node_id", "x", "y", "z"])

    for line in model_record:
        if line.startswith("GRID"):
            parts = line.split()
            x = float(parts[2])
            y = float(parts[3])
            z = float(parts[4])
            Node_id = int(parts[1])
            Type = parts[0]
            node_df.loc[len(node_df)] = [Node_id, x, y, z]
    node_df = node_df.astype({"Node_id": int})
    node_df.set_index("Node_id", inplace=True)
    return node_df

def CQUAD4_element_data(model_record):
    #This will take the model data and extract the element data as numerical data tha can be used for the rest of the progrma, built in a dataframe
    CQUAD4_element_df = pd.DataFrame(columns=["Element_id", "Property_id", "Node1", "Node2", "Node3", "Node4"])
    for line in model_record:
        if line.startswith("CQUAD4"):
            parts = line.split()
            Element_id = int(parts[1])
            Property_id = int(parts[2])
            Node1 = int(parts[3])
            Node2 = int(parts[4])
            Node3 = int(parts[5])
            Node4 = int(parts[6])
            CQUAD4_element_df.loc[len(CQUAD4_element_df)] = [Element_id, Property_id, Node1, Node2, Node3, Node4]
    CQUAD4_element_df = CQUAD4_element_df.astype({
        "Element_id": int,
        "Property_id": int,
        "Node1" : int,
        "Node2" : int,
        "Node3" : int,
        "Node4":int,
        })
    CQUAD4_element_df.set_index("Element_id", inplace=True)
    return CQUAD4_element_df

def shell_node_data(CQUAD4_element_df, node_df):
    #This will build a dataset of the nodes and their coordinates that are part of the shell elements
    shell_node_df = pd.DataFrame(columns=["x", "y", "z"])
    for row in CQUAD4_element_df.iterrows():
        #For each row in the cquad4 element dataframe, extract the 4 node ids
        node1 = row[1]["Node1"] # E.g 1 -> Meaning its referencing the node with id 1 in the node dataframe
        node2 = row[1]["Node2"]
        node3 = row[1]["Node3"]
        node4 = row[1]["Node4"]
        # For each of the 4 nodes, now check in the node dataframe to extract their coordinates
        for node in [node1, node2, node3, node4]:
            if node not in shell_node_df.index:
                node_data = node_df.loc[node]
                node_x = node_data["x"]
                node_y = node_data["y"]
                node_z = node_data["z"]
                shell_node_df.loc[node] = [node_x, node_y, node_z]
    return shell_node_df

def SPC_node_data(model_record):
    #This will take the model data and extract the SPC nodes, built as a dataframe
    SPCs_df = pd.DataFrame(columns=["SPC_collector","SPC_id", "DOF", "Node_id"])
    for line in model_record:
        if line.startswith("SPC"):
            parts = line.split()
            SPC_id = int(parts[1])
            DOF = int(parts[2])
            SPC_collector = (parts[0])
            for i in range(3, len(parts)):
                Node_id = int(parts[i])
                SPCs_df.loc[len(SPCs_df)] = [SPC_collector, SPC_id, DOF, Node_id]
    SPCs_df.set_index("SPC_id", inplace=True)
    return SPCs_df  


def cbar_element_data(model_record):
    cbar_df = pd.DataFrame(columns=["Element_id", "PID", "Node1", "Node2"])
    for line in model_record:
        if line.startswith("CBAR"):
            parts = line.split()
            Element_id = int(parts[1])
            Property_id = int(parts[2])
            Node1 = int(parts[3])
            Node2 = int(parts[4])
            cbar_df.loc[len(cbar_df)] = [Element_id, Property_id, Node1, Node2]
    cbar_df = cbar_df.astype({
        "Element_id": int,
        "PID": int,
        "Node1" : int,
        "Node2":int,
        })
    
    cbar_df.set_index("Element_id", inplace=True)


    return cbar_df


def fastener_database(cbar_df, shell_node_df, SPCs_df, node_df):
    #This will take the model data and extract the fastener data, building upon the CBAR data
    shell_nodes_ids = set(shell_node_df.index)
    SPC_nodes_ids = set(SPCs_df['Node_id'])
    fastener_df = pd.DataFrame(columns=["Element_id", "Property_id", "Shell_Node", "Support_Node", "Shell_x", "Shell_y", "Shell_z", "Support_x", "Support_y", "Support_z"])
    for index,row in cbar_df.iterrows():
        Element_id = index
        property_id = row["PID"]
        node_1 = row["Node1"]
        node_2 = row["Node2"]
        if node_1 in shell_nodes_ids and node_2 in SPC_nodes_ids:
                shell_node = node_1
                support_node = node_2
        elif node_2 in shell_nodes_ids and node_1 in SPC_nodes_ids:
                shell_node = node_2
                support_node = node_1
        else:
                print(f"Neither node is attached to the shell mesh or an SPC")
                sys.exit(1)


        #Once we have ascertained which node is part of the shell mesh and which is the SPC node, we can collect their respecitve coordinates
        shell_coordinate_x = node_df.loc[shell_node]["x"]
        shell_coordinate_y = node_df.loc[shell_node]["y"]
        shell_coordinate_z = node_df.loc[shell_node]["z"]
        support_coordinate_x = node_df.loc[support_node]["x"]
        support_coordinate_y = node_df.loc[support_node]["y"]
        support_coordinate_z = node_df.loc[support_node]["z"]
        fastener_df.loc[len(fastener_df)] = [Element_id, property_id, shell_node, support_node, shell_coordinate_x, shell_coordinate_y, shell_coordinate_z, support_coordinate_x, support_coordinate_y, support_coordinate_z]
    fastener_df = fastener_df.astype({
         "Element_id" : int,
         "Property_id" : int,
         "Shell_Node": int,
         "Support_Node" : int
    })
    fastener_df.set_index("Element_id", inplace=True)
    return fastener_df, shell_nodes_ids, SPC_nodes_ids

def pbar_property_data(model_record):
    rows = []
    for line in model_record:
        if line.startswith("PBAR"):
            parts = line.split()
            PID = int(parts[1])
            MID = int(parts[2])
            A = float(parts[3])

            rows.append({
                "PID" : PID,
                "MID" : MID,
                "A" : A
            })
    
    pbar_df =pd.DataFrame(rows)




    return pbar_df

