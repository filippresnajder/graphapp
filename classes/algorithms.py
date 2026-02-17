import heapq

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
