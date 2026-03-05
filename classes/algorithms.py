import heapq
from collections import deque

class Algorithms:
    def __init__(self, app):
        self.app = app
    
    def dijkstra(self, start_vertex, end_vertex):
        self.app.infobox.clear()
        self.app.infobox.log("Spúšťam vizualizáciu Dijkstrovho algoritmu")

        if self.__contains_negative_weight():
            self.app.infobox.log("Chyba: Dijkstrov algoritmus nie je možné spusiť v grafe so zápornými hranami")
            return False
        
        logs = []
        edges_logs = []
        vertices_logs = []

        distances = {v: float("inf") for v in self.app.vertices}
        previous = {}
        vertices_checked = set()
        edges_visited = set()
        distances[start_vertex] = 0

        pq = [(0, start_vertex.id, start_vertex)]

        while pq:
            step_log = []
            edges = {}
            current_dist, _, current = heapq.heappop(pq)

            if current_dist > distances[current]:
                continue

            step_log.append(f"Vyberám ešte neprehľadaný vrchol, s aktuálne najmenšou vzdialenosťou (Vrchol {current.tag}, aktuálna vzdialenosť {current_dist})")
            if current == end_vertex:
                step_log.append(f"Navštívený vrchol {end_vertex.tag} je konečný vrchol")
                step_log.append("Môžem začať rekonštrukciu cesty")
                logs.append(step_log)
                edges_logs.append({})
                vertices_logs.append({current: True})
                break

            step_log.append(f"Skúmam nenavštívené hrany zoradené podľa váhy pre aktuálny vrchol {current.tag}")
            for edge in sorted(current.edges, key=lambda e: e.weight):
                v1, v2, = edge.vertices

                if edge.orientation == "yes":
                    if v1 != current:
                        continue
                    neighbour = v2
                else:
                    neighbour = v2 if v1 == current else v1

                if edge not in edges_visited:
                    step_log.append(f"Skúmam hranu {current.tag} -> {neighbour.tag} (váha {edge.weight})")

                new_dist = current_dist + edge.weight

                if new_dist < distances[neighbour]:
                    distances[neighbour] = new_dist
                    previous[neighbour] = (current, edge)
                    heapq.heappush(pq, (new_dist, neighbour.id, neighbour))
                    step_log.append(f"Našla sa kratšia vzdialenosť - aktualizujem vzdialenosť do vrcholu {neighbour.tag} na hodnotu {new_dist}")
                    edges[edge] = True
                else:
                    if edge not in edges_visited:
                        step_log.append(f"Neaktualizujem vrchol {neighbour.tag} - jeho aktuálna vzdialenosť {distances[neighbour]} je menšia ako vypočítaná {new_dist}.")
                        edges[edge] = False
                
                edges_visited.add(edge)

            vertices_checked.add(current)

            step_log.append("")
            step_log.append("Momentálne najkratšie vzdialenosti do vrcholov po tomto kroku:")
            for v, d in distances.items():
                step_log.append(f"Vrchol {v.tag} {'(navštívený)' if v in vertices_checked else ''} = {('nekonečno' if d == float('inf') else d)}")

            step_log.append("")
            step_log.append("Zoznam predošlých vrchlov pre jednotlivé vrcholy:")
            for v, d in previous.items():
                step_log.append(f"Vrchol {v.tag} = {d[0].tag}")

            logs.append(step_log)
            edges_logs.append(edges)
            vertices_logs.append({current: True})

        if end_vertex not in previous and end_vertex != start_vertex:
            return None

        path = []
        path_tag = []
        edge_objects = set()
        current = end_vertex
        edges = {}
        vertices = {current: True}

        while current != start_vertex:
            step_log = []
            step_log.append("Zoznam predošlých vrchlov pre jednotlivé vrcholy:")
            for v, d in previous.items():
                step_log.append(f"Vrchol {v.tag} = {d[0].tag}")
            path.insert(0, current.id)
            path_tag.insert(0, current.tag)
            prev_vertex, prev_edge = previous[current]
            vertices[prev_vertex] = True
            edges[prev_edge] = True
            step_log.append(f"\nDo vrcholu {current.tag} vedie najvýhodnejšia cesta z vrcholu {prev_vertex.tag} hranou s váhou {prev_edge.weight}, vrchol a hranu pridávam do cesty")
            logs.append(step_log)
            vertices_logs.append(vertices.copy())
            edges_logs.append(edges.copy())
            edge_objects.add(prev_edge)
            current = prev_vertex

        path.insert(0, start_vertex.id)
        path_tag.insert(0, start_vertex.tag)
        step_logs = []
        step_logs.append(f"Vrchol {start_vertex.tag} je počiatočný vrchol, ukončujem rekonštrukciu cesty a algoritmus")
        step_logs.append(f"Najkratšia cesta: {path_tag}")
        logs.append(step_logs)
        edges_logs.append(edges)
        vertices_logs.append(vertices)

        return (path, path_tag, edge_objects, logs, edges_logs, vertices_logs)
    
    def prim(self, start_vertex):
        self.app.infobox.clear()
        self.app.infobox.log("Spúšťam vizualizáciu Primovho algoritmu")

        if self.__is_graph_oriented():
            self.app.infobox.log("Chyba: Primov algoritmus nefunguje na orientované grafy")
            return False

        visited = set()
        mst_edges = []
        cyclic_edges = []
        pq = []

        logs = []
        vertex_logs = []
        edges_logs = []

        first_log = f"Spúštam Primov algoritmus od vrcholu {start_vertex.tag}"
        second_log = f"Vrchol {start_vertex.tag} pridávam do minimálnej kostry"
        logs.append([first_log, second_log])
        vertex_logs.append({start_vertex: True})
        edges_logs.append({})
        visited.add(start_vertex)

        counter = 0
        for edge in start_vertex.edges:
            v1, v2 = edge.vertices
            neighbour = v2 if v1 == start_vertex else v1
            heapq.heappush(pq, (edge.weight, counter, start_vertex, neighbour, edge))
            counter += 1

        mst_cost = 0
        while pq:
            steps_log = []
            weight, _, previous_vertex, current_vertex, edge = heapq.heappop(pq)

            steps_log.append(f"Z navštívených vrcholov vyberám hranu s najmenšou váhou {weight} medzi vrcholmi {previous_vertex.tag} a {current_vertex.tag}")

            if current_vertex in visited:
                cyclic_edges.append(edge)
                steps_log.append("Vzniká cyklus, danú hranu nepridávam do minimálnej kostry grafu")
                logs.append(steps_log)
                mst = {e: True for e in mst_edges}
                cyclic = {e: False for e in cyclic_edges}
                merged = mst | cyclic
                edges_logs.append(merged)
                vertex_logs.append({v: True for v in visited})
                continue

            visited.add(current_vertex)
            mst_edges.append(edge)
            mst_cost += weight

            steps_log.append(f"Vrchol {current_vertex.tag} ešte nebol navštívený, pridávam ho do minimálnej kostry grafu")
            steps_log.append(f"Momentálna váha minimálnej kostry grafu je {mst_cost}")
            logs.append(steps_log)
            mst = {e: True for e in mst_edges}
            cyclic = {e: False for e in cyclic_edges}
            merged = mst | cyclic
            edges_logs.append(merged)
            vertex_logs.append({v: True for v in visited})

            for edge in current_vertex.edges:
                v1, v2 = edge.vertices
                neighbour = v2 if v1 == current_vertex else v1

                if neighbour not in visited:
                    heapq.heappush(pq, (edge.weight, counter, current_vertex, neighbour, edge))
                    counter += 1

        final_step_logs = []
        final_step_logs.append("Všetky vrcholy boli navštívené, hrany tvoriace minimálnu kostru sú zvýraznené")
        final_step_logs.append(f"Celková cena minimálnej kostry grafu je {mst_cost}")

        logs.append(final_step_logs)
        edges_logs.append({e: True for e in mst_edges})
        vertex_logs.append({v: True for v in visited})

        return (mst_edges, mst_cost, logs, edges_logs, vertex_logs)
    
    def kruskal(self):
        self.app.infobox.clear()

        if self.__is_graph_oriented():
            self.app.infobox.log("Chyba: Kruskalov algoritmus nefunguje na orientované grafy")
            return False
        
        logs = []
        edges = []
        for edge in self.app.edges:
            v1, v2 = edge.vertices
            edges.append((edge.weight, edge.id, v1, v2))

        edges.sort(key=lambda x: x[0])

        logs.append("Spúštam Kruskalov algoritmus a zoraďujem si hrany od najmenšej po najväčšiu")

        parent = {v: v for v in self.app.vertices}
        rank = {v: 0 for v in self.app.vertices}

        def find(vertex):
            if parent[vertex] != vertex:
                parent[vertex] = find(parent[vertex])
            return parent[vertex]
        
        def union(u, v, weight):
            root_u = find(u)
            root_v = find(v)
            logs.append(f"Kontrola hrany medzi vrcholmi {u.tag} - {v.tag} s váhou {weight}")

            if root_u == root_v:
                logs.append("Vznikol cyklus, preskakujem")
                return False
            
            if rank[root_u] < rank[root_v]:
                parent[root_u] = root_v
            elif rank[root_u] > rank[root_v]:
                parent[root_v] = root_u
            else:
                parent[root_v] = root_u
                rank[root_u] += 1

            logs.append("Cyklus nevznikol, pridávam ju do minimálnej kostry grafu")
            return True
        
        mst_edges = []
        for weight, edge_id, u, v in edges:
            if union(u,v,weight):
                mst_edges.append(edge_id)

        return (mst_edges, logs)
    
    def bfs(self, start_vertex):
        self.app.infobox.clear()
        visited = set()
        queue = deque()
        traversal_order = []
        tree_edges = []
        logs = []

        logs.append("Spúšťam algoritmus BFS")

        visited.add(start_vertex)
        queue.append(start_vertex)

        counter = 1
        visited_number = {}
        visited_number[start_vertex] = counter
        counter += 1

        while queue:
            current = queue.popleft()
            traversal_order.append(current.id)
            logs.append(f"Navštevujem vrchol s pôvodným označením {current.tag} -> (poradie v BFS - {visited_number[current]})")

            logs.append(f"Pozerám sa na všetky hrany, ktoré vedú z vrcholu {current.tag} -> (poradie v BFS - {visited_number[current]})")
            for edge in current.edges:
                v1, v2 = edge.vertices

                if edge.orientation == "yes":
                    if v1 != current:
                        continue
                    neighbour = v2
                else:
                    neighbour = v2 if v1 == current else v1

                if neighbour not in visited:
                    visited_number[neighbour] = counter
                    logs.append(f"Vrchol s pôvodným označením {neighbour.tag} ešte nebol navštívený, navštevujem ho -> (Určujem mu poradie v BFS na {counter})")
                    visited.add(neighbour)
                    queue.append(neighbour)
                    tree_edges.append((current.id, neighbour.id))
                    counter += 1

        return (traversal_order, tree_edges, logs)
    
    def dfs(self, start_vertex):
        self.app.infobox.clear()
        visited = set()
        traversal_order = []
        tree_edges = []
        logs = []

        visited_number = {}
        counter = 1
        visited_number[start_vertex] = counter
        counter += 1

        def dfs_visit(current):
            nonlocal counter
            visited.add(current.id)
            traversal_order.append(current.id)
            logs.append(f"Navštevujem vrchol s pôvodným označením {current.tag} -> (poradie v DFS - {visited_number[current]})")

            neighbours = []
            logs.append(f"Pozerám sa na všetky hrany, ktoré vedú z vrcholu {current.tag} -> (poradie v DFS - {visited_number[current]})")
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
            neighbours_to_visit = [neighbour for neighbour in neighbours if neighbour.id not in visited]

            if neighbours_to_visit:
                logs.append("Zoraďujem vrcholy")
            else:
                logs.append("Nenašli sa žiadne dostupné vrcholy, presúvam sa ďalej")

            for neighbour in neighbours_to_visit:
                if neighbour.id not in visited:
                    visited_number[neighbour] = counter
                    logs.append(f"Vrchol s pôvodným označením {neighbour.tag} ešte nebol navštívený, navštevujem ho -> (Určujem mu poradie v DFS na {counter})")
                    tree_edges.append((current.id, neighbour.id))
                    counter += 1
                    dfs_visit(neighbour)
        
        dfs_visit(start_vertex)

        return (traversal_order, tree_edges, logs)

    def floyd_warshall(self):
        pass

    def hamilton_cycle(self):
        pass

    def euler_path(self):
        pass
    
    def dijkstra_info(self):
        self.app.infobox.clear()
        self.app.infobox.log("Informácie o Dijkstrovom algoritme.")

    def prim_info(self):
        self.app.infobox.clear()
        self.app.infobox.log("Informácie o Primovom algoritme.")

    def kruskal_info(self):
        self.app.infobox.clear()
        self.app.infobox.log("Informácie o Kruskalovom algoritme.")

    def dfs_info(self):
        self.app.infobox.clear()
        self.app.infobox.log("Informácie o DFS algoritme.")

    def bfs_info(self):
        self.app.infobox.clear()
        self.app.infobox.log("Informácie o BFS algoritme.")

    def a_star_info(self):
        self.app.infobox.clear()
        self.app.infobox.log("Informácie o A Star algoritme.")

    def floyd_warshall_info(self):
        self.app.infobox.clear()
        self.app.infobox.log("Informácie o Floyd-Warshallovom algoritme.")

    def hamilton_cycle_info(self):
        self.app.infobox.clear()
        self.app.infobox.log("Informácie o Hamiltonovej kružnici.")

    def euler_path_info(self):
        self.app.infobox.clear()
        self.app.infobox.log("Informácie o Eulerovom ťahu.")

    
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

