class TotalOrderGraph:
    """Graph that interprets total order relations between nodes."""

    def __init__(self, nodes: int):
        if nodes < 1:
            raise ValueError("Number of nodes must be at least 1.")

        self.nodes = set(range(nodes))
        self.children_of: list[set] = [set() for _ in range(nodes)]
        self.parents_of: list[set] = [set() for _ in range(nodes)]

    def add_edge(self, big: int, small: int):
        if not (big in self.nodes and small in self.nodes):
            raise ValueError("Both nodes must be in the graph.")

        if big in self.children_of[small]:
            return  # Discard loops

        # Update parent's children
        all_children = self.children_of[small]
        all_children.add(small)
        self.children_of[big].update(all_children)
        for parent in self.parents_of[big]:
            # Remove already added children
            all_children.difference_update(self.children_of[parent])
            if not all_children:
                break # All children already added
            self.children_of[parent].update(all_children)

        # Update children's parents
        all_parents = self.parents_of[big]
        all_parents.add(big)
        self.parents_of[small].update(all_parents)
        for child in self.children_of[small]:
            # Remove already added parents
            all_parents.difference_update(self.parents_of[child])
            if not all_parents:
                break # All parents already added
            self.parents_of[child].update(all_parents)

    def get_order(self) -> list[int]:
        order = [(len(self.parents_of[node]), node) for node in self.nodes]
        order.sort(key=lambda x: x[0])
        return [node for _, node in order]
