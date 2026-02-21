import heapq
from collections import deque

class Algorithms:
    def __init__(self, app):
        self.app = app
    
    def dijkstra(self, start_vertex, end_vertex):
        if self.__contains_negative_weight():
            return False #TODO: Vypíš správu keď graf obsahuje zápornú hranu

        distances = {v: float("inf") for v in self.app.vertices}
        previous = {}
        distances[start_vertex] = 0

        pq = [(0, start_vertex.id, start_vertex)]

        while pq:
            current_dist, _, current = heapq.heappop(pq)

            if current == end_vertex:
                break

            if current_dist > distances[current]:
                continue

            for edge in current.edges:
                v1, v2, = edge.vertices

                if edge.orientation == "yes":
                    if v1 != current:
                        continue
                    neighbour = v2
                else:
                    neighbour = v2 if v1 == current else v1

                new_dist = current_dist + edge.weight

                if new_dist < distances[neighbour]:
                    distances[neighbour] = new_dist
                    previous[neighbour] = current
                    heapq.heappush(pq, (new_dist, neighbour.id, neighbour))

        path = []
        current = end_vertex

        if current not in previous and current != start_vertex:
            return None
        
        while current:
            path.insert(0, current.id)
            current = previous.get(current)

        return path
    
    def prim(self, start_vertex):
        if self.__is_graph_oriented():
            return False #TODO: Vypíš správu keď je graf orientovaný

        visited = set()
        mst_edges = []
        pq = []

        visited.add(start_vertex)

        counter = 0

        for edge in start_vertex.edges:
            v1, v2 = edge.vertices
            neighbour = v2 if v1 == start_vertex else v1
            heapq.heappush(pq, (edge.weight, counter, start_vertex, neighbour))
            counter += 1

        while pq:
            weight, _, u, v = heapq.heappop(pq)

            if v in visited:
                continue

            visited.add(v)
            mst_edges.append(sorted([u.id, v.id]))

            for edge in v.edges:
                v1, v2 = edge.vertices
                neighbour = v2 if v1 == v else v1

                if neighbour not in visited:
                    heapq.heappush(pq, (edge.weight, counter, v, neighbour))
                    counter += 1

        return sorted(mst_edges)
    
    def kruskal(self):
        if self.__is_graph_oriented():
            return False #TODO: Vypíš správu keď je graf orientovaný
        
        size = len(self.app.vertices)

        edges = []
        for edge in self.app.edges:
            v1, v2 = edge.vertices
            edges.append((v1.id - 1, v2.id - 1, edge.weight))

        edges.sort(key=lambda x: x[2])

        parent = list(range(size))
        rank = [0] * size

        def find(i):
            if parent[i] != i:
                parent[i] = find(parent[i])
            return parent[i]
        
        def union(x, y):
            root_x = find(x)
            root_y = find(y)

            if root_x == root_y:
                return False
            
            if rank[root_x] < rank[root_y]:
                parent[root_x] = root_y
            elif rank[root_x] > rank[root_y]:
                parent[root_y] = root_x
            else:
                parent[root_y] = root_x
                rank[root_x] += 1

            return True
        
        mst = []
        for u,v,w in edges:
            if union(u,v):
                mst.append(sorted([u+1, v+1]))

        return sorted(mst)
    
    def bfs(self, start_vertex):
        visited = set()
        queue = deque()
        traversal_order = []
        tree_edges = []

        visited.add(start_vertex)
        queue.append(start_vertex)

        while queue:
            current = queue.popleft()
            traversal_order.append(current.id)

            for edge in current.edges:
                v1, v2 = edge.vertices

                if edge.orientation == "yes":
                    if v1 != current:
                        continue
                    neighbour = v2
                else:
                    neighbour = v2 if v1 == current else v1

                if neighbour not in visited:
                    visited.add(neighbour)
                    queue.append(neighbour)
                    tree_edges.append((current.id, neighbour.id))

        return traversal_order, tree_edges
    
    def dfs(self, start_vertex):
        visited = set()
        traversal_order = []
        tree_edges = []

        def dfs_visit(current):
            visited.add(current.id)
            traversal_order.append(current.id)

            neighbours = []
            for edge in current.edges:
                v1, v2 = edge.vertices

                if edge.orientation == "yes":
                    if v1 != current:
                        continue
                    neighbour = v2
                else:
                    neighbour = v2 if v1 == current else v1

                neighbours.append(neighbour)

            neighbours = sorted(neighbours, key=lambda v: v.id)

            for neighbour in neighbours:
                if neighbour.id not in visited:
                    tree_edges.append((current.id, neighbour.id))
                    dfs_visit(neighbour)
        
        dfs_visit(start_vertex)

        return traversal_order, tree_edges
    
    def __is_graph_oriented(self):
        for edge in self.app.edges:
            if edge.orientation == "yes":
                return True
        return False
    
    def __contains_negative_weight(self):
        for edge in self.app.edges:
            if edge.weight < 0:
                return True
        return False

