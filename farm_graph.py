
from collections import deque


class FarmGraph:
    
    def __init__(self):
        self.adjacency_list = {}
        self.node_data = {}  # Store additional data for each node
        self._initialize_farm_graph()
    
    def _initialize_farm_graph(self):
        locations = [
            ("house", {"type": "building", "description": "Player's house"}),
            ("barn", {"type": "building", "description": "Animal barn"}),
            ("field_north", {"type": "farmland", "description": "Northern crop field"}),
            ("field_south", {"type": "farmland", "description": "Southern crop field"}),
            ("field_east", {"type": "farmland", "description": "Eastern crop field"}),
            ("water_source", {"type": "resource", "description": "River for irrigation"}),
            ("shop", {"type": "building", "description": "Trader's shop"}),
            ("forest", {"type": "resource", "description": "Forest for wood"}),
        ]
        
        for name, data in locations:
            self.add_node(name, data)
        
        paths = [
            ("house", "field_north", 2),
            ("house", "field_south", 3),
            ("house", "barn", 4),
            ("house", "shop", 5),
            ("field_north", "field_east", 2),
            ("field_north", "water_source", 3),
            ("field_south", "field_east", 2),
            ("field_south", "forest", 4),
            ("field_east", "water_source", 2),
            ("barn", "field_north", 3),
            ("shop", "field_south", 4),
            ("water_source", "forest", 5),
        ]
        
        for node1, node2, weight in paths:
            self.add_edge(node1, node2, weight)
    
    
    def add_node(self, name, data=None):
        if name not in self.adjacency_list:
            self.adjacency_list[name] = []
            self.node_data[name] = data or {}
    
    def add_edge(self, node1, node2, weight=1):
        if node1 not in self.adjacency_list:
            self.add_node(node1)
        if node2 not in self.adjacency_list:
            self.add_node(node2)
        
        self.adjacency_list[node1].append((node2, weight))
        self.adjacency_list[node2].append((node1, weight))
    
    def get_neighbors(self, node):
        return self.adjacency_list.get(node, [])
    
    def get_nodes(self):
        return list(self.adjacency_list.keys())
    
    
    def bfs(self, start):
        if start not in self.adjacency_list:
            return []
        
        visited = set()
        queue = deque([start])  # Using Queue data structure!
        traversal_order = []
        
        while queue:
            current = queue.popleft()  # FIFO - dequeue from front
            
            if current not in visited:
                visited.add(current)
                traversal_order.append(current)
                
                for neighbor, weight in self.adjacency_list[current]:
                    if neighbor not in visited:
                        queue.append(neighbor)
        
        return traversal_order
    
    def find_path_bfs(self, start, end):
        if start not in self.adjacency_list or end not in self.adjacency_list:
            return []
        
        if start == end:
            return [start]
        
        visited = set([start])
        queue = deque([(start, [start])])  # (current_node, path_so_far)
        
        while queue:
            current, path = queue.popleft()
            
            for neighbor, weight in self.adjacency_list[current]:
                if neighbor not in visited:
                    new_path = path + [neighbor]
                    
                    if neighbor == end:
                        return new_path
                    
                    visited.add(neighbor)
                    queue.append((neighbor, new_path))
        
        return []  # No path found
    
    
    def dfs(self, start, visited=None):
        if visited is None:
            visited = set()
        
        if start not in self.adjacency_list:
            return []
        
        visited.add(start)
        traversal_order = [start]
        
        for neighbor, weight in self.adjacency_list[start]:
            if neighbor not in visited:
                traversal_order.extend(self.dfs(neighbor, visited))
        
        return traversal_order
    
    def dfs_iterative(self, start):
        if start not in self.adjacency_list:
            return []
        
        visited = set()
        stack = [start]  # Using STACK data structure!
        traversal_order = []
        
        while stack:
            current = stack.pop()  # LIFO - pop from top
            
            if current not in visited:
                visited.add(current)
                traversal_order.append(current)
                
                for neighbor, weight in self.adjacency_list[current]:
                    if neighbor not in visited:
                        stack.append(neighbor)
        
        return traversal_order
    
    
    def shortest_path(self, start, end):
        if start not in self.adjacency_list or end not in self.adjacency_list:
            return [], float('inf')
        
        distances = {node: float('inf') for node in self.adjacency_list}
        distances[start] = 0
        previous = {node: None for node in self.adjacency_list}
        unvisited = set(self.adjacency_list.keys())
        
        while unvisited:
            current = min(unvisited, key=lambda x: distances[x])
            
            if distances[current] == float('inf'):
                break  # Remaining nodes are unreachable
            
            if current == end:
                break  # Found shortest path to destination
            
            unvisited.remove(current)
            
            for neighbor, weight in self.adjacency_list[current]:
                if neighbor in unvisited:
                    new_distance = distances[current] + weight
                    if new_distance < distances[neighbor]:
                        distances[neighbor] = new_distance
                        previous[neighbor] = current
        
        if distances[end] == float('inf'):
            return [], float('inf')
        
        path = []
        current = end
        while current is not None:
            path.insert(0, current)
            current = previous[current]
        
        return path, distances[end]
    
    
    def is_connected(self):
        if not self.adjacency_list:
            return True
        
        start = next(iter(self.adjacency_list))
        visited = set(self.bfs(start))
        return len(visited) == len(self.adjacency_list)
    
    def find_all_paths(self, start, end, path=None):
        if path is None:
            path = []
        
        path = path + [start]
        
        if start == end:
            return [path]
        
        if start not in self.adjacency_list:
            return []
        
        paths = []
        for neighbor, weight in self.adjacency_list[start]:
            if neighbor not in path:  # Avoid cycles
                new_paths = self.find_all_paths(neighbor, end, path)
                paths.extend(new_paths)
        
        return paths
    
    
    def get_locations_by_type(self, location_type):
        return [
            node for node, data in self.node_data.items()
            if data.get("type") == location_type
        ]
    
    def get_farmlands(self):
        return self.get_locations_by_type("farmland")
    
    def get_buildings(self):
        return self.get_locations_by_type("building")
    
    def get_resources(self):
        return self.get_locations_by_type("resource")
    
    def calculate_farm_efficiency(self, player_location="house"):
        farmlands = self.get_farmlands()
        if not farmlands:
            return 0
        
        total_distance = 0
        for field in farmlands:
            path, distance = self.shortest_path(player_location, field)
            total_distance += distance
        
        return total_distance / len(farmlands)
    
    def __str__(self):
        lines = ["Farm Map Graph:"]
        for node, edges in self.adjacency_list.items():
            edge_str = ", ".join([f"{n}({w})" for n, w in edges])
            lines.append(f"  {node} -> [{edge_str}]")
        return "\n".join(lines)



def create_farm_graph():
    return FarmGraph()


if __name__ == "__main__":
    farm = FarmGraph()
    
    print("=== Farm Map Graph ===")
    print(farm)
    
    print("\n=== BFS from house ===")
    print(farm.bfs("house"))
    
    print("\n=== DFS from house ===")
    print(farm.dfs("house"))
    
    print("\n=== Shortest path: house -> water_source ===")
    path, dist = farm.shortest_path("house", "water_source")
    print(f"Path: {path}, Distance: {dist}")
    
    print("\n=== All paths: house -> forest ===")
    paths = farm.find_all_paths("house", "forest")
    for p in paths:
        print(f"  {' -> '.join(p)}")
    
    print("\n=== Farm efficiency from house ===")
    print(f"Average distance to fields: {farm.calculate_farm_efficiency():.2f}")
