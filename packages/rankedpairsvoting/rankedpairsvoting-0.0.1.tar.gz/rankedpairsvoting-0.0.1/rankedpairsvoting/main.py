import random
from itertools import combinations, permutations
from .objects import TotalOrderGraph


def ranked_pairs_voting(candidates: list[str], votes: list[list[int]]) -> list[str]:
    """
    Effectuates the Ranked Pairs voting method.

    Args:
        candidates (list[str]): A list of candidate names in order.
        votes (list[list[int]]): A list of votes, ranking each candidate in the
            voter's preference order. There can be multiple candidates in the
            same position.

    Returns:
        winners (list[str]): The list of winning candidates in order.

    """
    if len(candidates) < 1:
        raise ValueError("There must be at least one candidate.")

    if len(votes) < 1:
        raise ValueError("There must be at least one vote.")

    if any(len(vote) != len(candidates) for vote in votes):
        raise ValueError("All votes must have the same number of candidates.")

    # Effectuate round-robin to determine pairwise preferences
    round_robin = {(i, j): 0 for i, j in permutations(range(len(candidates)), 2)}
    for vote in votes:
        for i, j in combinations(range(len(candidates)), 2):
            if vote[i] < vote[j]:
                round_robin[(i, j)] += 1
            elif vote[i] > vote[j]:
                round_robin[(j, i)] += 1

    ties = []
    # Calculate the pairwise margins only keeping winning pairs
    pairwise_margins = dict()
    for i, j in combinations(range(len(candidates)), 2):
        if round_robin[(i, j)] > round_robin[(j, i)]:
            pairwise_margins[(i, j)] = round_robin[(i, j)] - round_robin[(j, i)]
        elif round_robin[(i, j)] < round_robin[(j, i)]:
            pairwise_margins[(j, i)] = round_robin[(j, i)] - round_robin[(i, j)]
        else:
            # Ties are very coincidental may cause non-orderability if not
            # taken into account. Therefore, we determine them at random which
            # is fair for candidates and will have the lowest priority of pairs
            # in terms of ordering.
            if random.getrandbits(1) == 1:
                ties.append((i, j))
            else:
                ties.append((j, i))

    # Shuffle for fairness and sort by margin
    # Otherwise pairs may favor candidates placed first in the list
    pairwise_margins = [*pairwise_margins.items()]
    random.shuffle(pairwise_margins)
    sorted_pairs = sorted(pairwise_margins, key=lambda x: x[1], reverse=True)
    
    # Construct the graph with total ordering of candidates
    graph = TotalOrderGraph(len(candidates))
    for (big, small), _ in sorted_pairs:
        graph.add_edge(big, small)

    # Add ties to the graph in random order to secure fairness
    random.shuffle(ties)
    for big, small in ties:
        graph.add_edge(big, small)

    # Get the final order of candidates
    return [candidates[i] for i in graph.get_order()]


if __name__ == "__main__":
    # Example usage
    candidates = ["Alice", "Bob", "Charlie"]
    votes = [
        [1, 2, 3],  # Voter 1 prefers Alice > Bob > Charlie
        [2, 1, 3],  # Voter 2 prefers Bob > Alice > Charlie
        [3, 1, 2],  # Voter 3 prefers Bob > Charlie > Alice
        [1, 1, 2],  # Voter 4 prefers Alice = Bob > Charlie
        [1, 1, 1],  # Voter 5 prefers Alice = Bob = Charlie
        [2, 2, 1],  # Voter 6 prefers Charlie > Bob = Alice
        [2, 2, 1],  # Voter 7 prefers Charlie > Bob = Alice
    ]

    winners = ranked_pairs_voting(candidates, votes)
    print("Winners:", winners)