import heapq
from collections import deque

class Algorithms:
    def __init__(self, app):
        self.app = app

    def build_adj_matrix(self):
        size = len(self.app.vertices)
        matrix = [[0] * size for _ in range(size)]

        for edge in self.app.edges:
            v1, v2 = edge.vertices
            matrix[v1.id-1][v2.id-1] = edge.weight
            matrix[v2.id-1][v1.id-1] = edge.weight # V prípade neorientovaného grafu

        return matrix
    
    def dijkstra(self, start_vertex, end_vertex):
        size = len(self.app.vertices)
        adj_matrix = self.build_adj_matrix()

        distances = [float('inf')] * size
        previous = [None] * size
        distances[start_vertex.id - 1] = 0
        visited = [False] * size

        for _ in range(size):
            min_distance = float('inf')
            u = None

            for i in range(size):
                if not visited[i] and distances[i] < min_distance:
                    min_distance = distances[i]
                    u = i
            
            if u is None:
                break

            visited[u] = True

            for v in range(size):
                if adj_matrix[u][v] != 0 and not visited[v]:
                    alt = distances[u] + adj_matrix[u][v]
                    if alt < distances[v]:
                        distances[v] = alt
                        previous[v] = u

        return self.__get_dijkstra_path(end_vertex, previous)
    
    def __get_dijkstra_path(self, end_vertex, previous):
        path = []
        current = end_vertex.id - 1
        while current is not None:
            path.insert(0, self.app.vertices[current])
            current = previous[current]
        return [v.id for v in path]
    
    def prim(self, start_vertex):
        size = len(self.app.vertices)
        adj_matrix = self.build_adj_matrix()
        pq = []
        src = start_vertex.id - 1

        key = [float('inf')] * size
        parent = [-1] * size
        in_mst = [False] * size

        heapq.heappush(pq, (0, src))
        key[src] = 0

        while pq:
            u = heapq.heappop(pq)[1]

            if in_mst[u]:
                continue

            in_mst[u] = True

            for v in range(size):
                weight = adj_matrix[u][v]
                if weight != 0 and not in_mst[v] and key[v] > weight:
                    key[v] = weight
                    heapq.heappush(pq, (key[v], v))
                    parent[v] = u

        mst_edges = []
        for i in range(size):
            if parent[i] != -1:
                edge = sorted([self.app.vertices[parent[i]].id, self.app.vertices[i].id])
                mst_edges.append(edge)

        mst_edges = sorted(mst_edges, key=lambda x: (x[0], x[1]))

        return mst_edges
    
    def kruskal(self):
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

            for neigbour in sorted(current.neighbours, key=lambda v: v.id):
                if neigbour not in visited:
                    visited.add(neigbour)
                    queue.append(neigbour)
                    tree_edges.append(sorted([current.id, neigbour.id]))

        return traversal_order, tree_edges
    
    def dfs(self, start_vertex):
        visited = set()
        traversal_order = []
        tree_edges = []

        def dfs_visit(vertex):
            visited.add(vertex)
            traversal_order.append(vertex.id)

            for neighbour in sorted(vertex.neighbours, key=lambda v: v.id):
                if neighbour not in visited:
                    tree_edges.append(sorted([vertex.id, neighbour.id]))
                    dfs_visit(neighbour)
        
        dfs_visit(start_vertex)

        return traversal_order, tree_edges

