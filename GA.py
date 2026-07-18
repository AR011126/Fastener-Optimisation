from evauate_population import evaluate_population

def constraint_dominates(candidate_a, candidate_b):
    if candidate_a['is_feasible'] and not candidate_b['is_feasible']:
        return True
    if candidate_b['is_feasible'] and not candidate_a['is_feasible']:
        return False
    
    # Both infeasible
    if not candidate_a['is_feasible'] and not candidate_b['is_feasible']:
        return candidate_a['total_constraint_violation'] < candidate_b['total_constraint_violation']

    #Both feasible
    a_objectives = candidate_a['objectives']
    b_objectives = candidate_b['objectives']

    no_worse_in_all = True
    better_in_at_least_one = False

    for objective_name in a_objectives:
        a_value = a_objectives[objective_name]
        b_value = b_objectives[objective_name]

        if a_value < b_value:
            better_in_at_least_one = True
        if a_value > b_value:
            no_worse_in_all = False
            break
    
    return better_in_at_least_one and no_worse_in_all

def non_dominated_sort(population):
    fronts = [[]]
    for candidate in population:
        candidate['dominated_candidates'] = []
        candidate['domination_count'] = 0

    for i, candidate_a in enumerate(population):
        for j, candidate_b in enumerate(population):
            if i == j:
                continue
            if constraint_dominates(candidate_a, candidate_b):
                candidate_a['dominated_candidates'].append(candidate_b)
            elif constraint_dominates(candidate_b, candidate_a):
                candidate_a['domination_count'] += 1
        
    for candidate in population:
        if candidate['domination_count'] == 0:
            candidate['rank'] = 0
            fronts[0].append(candidate)
    
    front_index = 0
    while len(fronts[front_index]) > 0:
        next_front = []
        for candidate in fronts[front_index]:
            for dominated_candidate in candidate['dominated_candidates']:
                dominated_candidate['domination_count'] -= 1

                if dominated_candidate['domination_count'] == 0:
                    dominated_candidate['rank'] = front_index + 1
                    next_front.append(dominated_candidate)
        front_index += 1
        fronts.append(next_front)

    fronts.pop()
    return fronts


def assign_crowd_distance(front):
    """
    Assign NSGA-II crowding distance to each candidate in the front.

    Parameters
    ----------
    front: list[dict]
        List of candidates in the front, each candidate is a dictionary containing its attributes including objectives
    
    """

    if not front:
        return
    
    # Rest crowding distance
    for candidate in front:
        candidate['crowding_distance'] = 0.0

    #One or two member fronts are boundary only fronts

    if len(front) <= 2:
        for candidate in front:
            candidate['crowding_distance'] = float('inf')
        return
    

    objective_names = list(front[0]['objectives'].keys())

    for objective_name in objective_names:
        front.sort(key=lambda candidate: candidate['objectives'][objective_name])

        front[0]['crowding_distance'] = float('inf')
        front[-1]['crowding_distance'] = float('inf')

        objective_min = front[0]['objectives'][objective_name]
        objective_max = front[-1]['objectives'][objective_name]


        if objective_max == objective_min:
            continue
        

        for index in range(1, len(front) - 1):
            prev_candidate = front[index - 1]['objectives'][objective_name]
            next_candidate = front[index + 1]['objectives'][objective_name]

            normalised_distance = (next_candidate - prev_candidate) / (objective_max - objective_min)

            front[index]['crowding_distance'] += normalised_distance



def assign_rank_and_crowd_distance(population):
    """
    Performs non-dominated sorting on the population and assigns rank and crowding distance 
    """

    fronts = non_dominated_sort(population)

    for rank, front in enumerate(fronts):
        for candidate in front:
            candidate['rank'] = rank
        
        assign_crowd_distance(front)

    return fronts

