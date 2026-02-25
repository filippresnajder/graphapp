import heapq
from collections import deque

class Algorithms:
    def __init__(self, app):
        self.app = app
    
    def dijkstra(self, start_vertex, end_vertex):
        self.app.infobox.clear()

        if self.__contains_negative_weight():
            self.app.infobox.log("Chyba: Dijkstrov algoritmus nie je možné spusiť v grafe so zápornými hranami")
            return False
        
        logs = ""
        logs += "Spúštam Dijkstrov algoritmus\n"
        logs += f"Začínam na vrchole {start_vertex.tag}\n"

        distances = {v: float("inf") for v in self.app.vertices}
        logs += "Inicializujem vzdialenosti pre vrcholy na nekonečno\n"
        previous = {}
        edges_visited = []
        distances[start_vertex] = 0
        logs += f"Pre počiatočný vrchol {start_vertex.tag} nastavujem vzdialenosť 0\n"

        pq = [(0, start_vertex.id, start_vertex)]

        while pq:
            current_dist, _, current = heapq.heappop(pq)

            if current_dist > distances[current]:
                continue

            logs += f"Vyberám vrchol {current.tag} s aktuálnou vzdialenosťou {current_dist}\n"
            if current == end_vertex:
                logs += f"Navštívil som konečný vrchol {end_vertex.tag}, začínam rekonštrukciu cesty\n"
                break

            for edge in current.edges:
                v1, v2, = edge.vertices

                if edge.orientation == "yes":
                    if v1 != current:
                        continue
                    neighbour = v2
                else:
                    neighbour = v2 if v1 == current else v1

                if edge not in edges_visited:
                    logs += f"Skúmam hranu {current.tag} -> {neighbour.tag} (váha {edge.weight})\n"

                new_dist = current_dist + edge.weight

                if new_dist < distances[neighbour]:
                    distances[neighbour] = new_dist
                    previous[neighbour] = (current, edge)
                    heapq.heappush(pq, (new_dist, neighbour.id, neighbour))
                    logs += f"Našla sa kratšia vzdialenosť - aktualizujem vzdialenosť do vrcholu {neighbour.tag} na hodnotu {new_dist}\n"
                else:
                    if edge not in edges_visited:
                        logs += f"Neaktualizujem vrchol {neighbour.tag} - aktuálna vzdialenosť je kratšia.\n"
                
                edges_visited.append(edge)


        if end_vertex not in previous and end_vertex != start_vertex:
            return None
        
        path = []
        path_tag = []
        edge_ids = []
        current = end_vertex

        while current != start_vertex:
            path.insert(0, current.id)
            path_tag.insert(0, current.tag)
            prev_vertex, prev_edge = previous[current]
            edge_ids.insert(0, prev_edge.id)
            current = prev_vertex

        path.insert(0, start_vertex.id)
        path_tag.insert(0, start_vertex.tag)

        return (path, edge_ids, path_tag, logs)
    
    def prim(self, start_vertex):
        self.app.infobox.clear()

        if self.__is_graph_oriented():
            self.app.infobox.log("Chyba: Primov algoritmus nefunguje na orientované grafy")
            return False

        visited = set()
        mst_edges = []
        pq = []
        visited_edges = []
        logs = ""
        logs += f"Spúštam Primov algoritmus od vrcholu {start_vertex.tag}\n"
        logs += f"Vrchol {start_vertex.tag} pridávam do minimálnej kostry\n"
        visited.add(start_vertex)

        counter = 0

        for edge in start_vertex.edges:
            v1, v2 = edge.vertices
            neighbour = v2 if v1 == start_vertex else v1
            heapq.heappush(pq, (edge.weight, counter, start_vertex, neighbour, edge))
            counter += 1

        while pq:
            weight, _, u, v, edge = heapq.heappop(pq)

            logs += f"Kontrolujem hranu ({u.tag} - {v.tag}) s váhou {weight}\n"

            if v in visited:
                logs += "Vrchol už patrí do minimálnej kostry, preskakujem\n"
                continue

            visited.add(v)
            mst_edges.append(edge.id)
            logs += "Vrchol a hranu pridávam do minimálnej kostry\n"
            visited_edges.append(edge)

            for edge in v.edges:
                v1, v2 = edge.vertices
                neighbour = v2 if v1 == v else v1

                if neighbour not in visited:
                    heapq.heappush(pq, (edge.weight, counter, v, neighbour, edge))
                    counter += 1

        return (mst_edges, logs)
    
    def kruskal(self):
        self.app.infobox.clear()

        if self.__is_graph_oriented():
            self.app.infobox.log("Chyba: Kruskalov algoritmus nefunguje na orientované grafy")
            return False
        
        size = len(self.app.vertices)
        logs = []

        edges = []
        for edge in self.app.edges:
            v1, v2 = edge.vertices
            edges.append((edge.weight, edge.id, v1.id - 1, v2.id - 1, v1.tag, v2.tag))

        edges.sort()

        # Kvôli lokálnej premnej v union funkcií používame zoznam
        logs.append("Spúštam Kruskalov algoritmus a zoraďujem si hrany od najmenšej po najväčšiu")

        parent = list(range(size))
        rank = [0] * size

        def find(i):
            if parent[i] != i:
                parent[i] = find(parent[i])
            return parent[i]
        
        def union(x, y, x_tag, y_tag, weight, logs):
            root_x = find(x)
            root_y = find(y)
            logs.append(f"Kontrola hrany medzi vrcholmi {x_tag} - {y_tag} s váhou {weight}")

            if root_x == root_y:
                logs.append("Vznikol cyklus, preskakujem")
                return False
            
            if rank[root_x] < rank[root_y]:
                parent[root_x] = root_y
            elif rank[root_x] > rank[root_y]:
                parent[root_y] = root_x
            else:
                parent[root_y] = root_x
                rank[root_x] += 1

            logs.append("Cyklus nevznikol, pridávam ju do minimálnej kostry grafu")
            return True
        
        mst_edges = []
        for weight, edge_id, u, v, u_tag, v_tag in edges:
            if union(u,v, u_tag, v_tag, weight, logs):
                mst_edges.append(edge_id)

        return (mst_edges, logs)
    
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

