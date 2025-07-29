import pytest
import os
import json
import shutil # For copying the provided .canvas file

from canvaz.core import Canvas, Color, Box

# Helper to get the actual string value of a Color enum member
def get_color_str(color_input):
    if isinstance(color_input, Color):
        return color_input.name # Assuming enum.name is the string representation (e.g., Color.gray.name -> "gray")
    return color_input # Already a string

# Using pytest.fixture to create Canvas instances
@pytest.fixture
def empty_canvas(tmp_path):
    """Provides an empty Canvas instance for testing, using a temporary file."""
    temp_file = tmp_path / "temp_empty.canvas"
    initial_content = {"nodes": [], "edges": []}
    with open(temp_file, 'w') as f:
        json.dump(initial_content, f)
    return Canvas(file_path=str(temp_file))

@pytest.fixture
def populated_canvas(tmp_path):
    """Provides a Canvas instance with some pre-added nodes for testing."""
    original_canvas_path = os.path.join(os.path.dirname(__file__), "use.canvas")
    if not os.path.exists(original_canvas_path):
        pytest.fail(f"Error: tests/use.canvas not found at {original_canvas_path}. Please ensure the file exists.")

    temp_canvas_file = tmp_path / "temp_populated.canvas"
    shutil.copy(original_canvas_path, temp_canvas_file)

    canvas = Canvas(file_path=str(temp_canvas_file))

    # Add more nodes for testing specific scenarios beyond the initial file content
    canvas.add_node("Node A", color=Color.blue)
    canvas.add_node("Node B", color="red")
    canvas.add_node("Process C", color=Color.yellow)
    return canvas

class TestCanvazCore:

    def test_canvas_init_empty(self, empty_canvas):
        """Test Canvas initialization without a file (but with a temp file path)."""
        assert empty_canvas is not None
        assert hasattr(empty_canvas, 'nodes')
        assert hasattr(empty_canvas, 'edges')
        assert len(empty_canvas.nodes) == 0
        assert len(empty_canvas.edges) == 0

    def test_canvas_init_with_provided_file(self, tmp_path):
        """Test Canvas initialization with the user-provided use.canvas file."""
        original_canvas_path = os.path.join(os.path.dirname(__file__), "use.canvas")
        if not os.path.exists(original_canvas_path):
            pytest.fail(f"Error: tests/use.canvas not found at {original_canvas_path}. Please ensure the file exists.")

        temp_canvas_file = tmp_path / "loaded_canvas.canvas"
        shutil.copy(original_canvas_path, temp_canvas_file)

        canvas = Canvas(file_path=str(temp_canvas_file))
        assert canvas is not None
        assert len(canvas.nodes) > 0
        assert len(canvas.edges) > 0
        assert any(node.text == "Start" for node in canvas.nodes)
        assert any(edge.text == "connects" for edge in canvas.edges)


    def test_add_node(self, empty_canvas):
        """Test adding a single node."""
        node_text = "My First Node"
        empty_canvas.add_node(node_text)
        assert len(empty_canvas.nodes) == 1
        added_node = empty_canvas.nodes[0]
        assert isinstance(added_node, Box)
        assert added_node.text == node_text
        # Corrected: Expect the string representation of the default color
        assert added_node.color == get_color_str(Color.gray)

        # Test adding with a specific color (Color enum)
        empty_canvas.add_node("Green Node", color=Color.green)
        assert len(empty_canvas.nodes) == 2
        green_node = empty_canvas.nodes[1]
        assert green_node.text == "Green Node"
        # Corrected: Expect the string representation of the enum color
        assert green_node.color == get_color_str(Color.green)

        # Test adding with a specific color (string)
        empty_canvas.add_node("Orange Node", color="orange")
        assert len(empty_canvas.nodes) == 3
        orange_node = empty_canvas.nodes[2]
        assert orange_node.text == "Orange Node"
        # Corrected: Expect the string color directly
        assert orange_node.color == "orange"

    def test_select_by_id_node(self, populated_canvas):
        """Test selecting a node by its ID."""
        found_nodes = populated_canvas.select_nodes_by_text("Start")
        assert len(found_nodes) > 0, "Pre-condition failed: 'Start' node not found in populated_canvas"
        node_from_file = found_nodes[0]

        selected_node = populated_canvas.select_by_id(key=node_from_file.id, type='node')
        assert selected_node is not None
        assert selected_node.id == node_from_file.id
        assert selected_node.text == "Start"

        node_a = populated_canvas.select_nodes_by_text("Node A")[0]
        selected_node_a = populated_canvas.select_by_id(key=node_a.id, type='node')
        assert selected_node_a is not None
        assert selected_node_a.id == node_a.id
        assert selected_node_a.text == "Node A"

        selected_node = populated_canvas.select_by_id(key="non_existent_id", type='node')
        assert selected_node is None

    def test_select_by_id_edge(self, populated_canvas):
        """Test selecting an edge by its ID."""
        found_edges = populated_canvas.select_edges_by_text("connects")
        assert len(found_edges) > 0, "Pre-condition failed: 'connects' edge not found in populated_canvas"
        edge_from_file = found_edges[0]

        selected_edge = populated_canvas.select_by_id(key=edge_from_file.id, type='edge')
        assert selected_edge is not None
        assert selected_edge.id == edge_from_file.id
        assert selected_edge.text == "connects"

        selected_edge = populated_canvas.select_by_id(key="non_existent_edge_id", type='edge')
        assert selected_edge is None

    def test_select_by_color_node(self, populated_canvas):
        """Test selecting nodes by color."""
        blue_nodes = populated_canvas.select_by_color(key=Color.blue, type='node')
        assert any(n.text == "Node A" for n in blue_nodes)
        assert len(blue_nodes) >= 1
        # Corrected: Check color directly as string
        assert all(n.color == get_color_str(Color.blue) for n in blue_nodes if n.text == "Node A")

        red_nodes = populated_canvas.select_by_color(key="red", type='node')
        assert any(n.text == "Node B" for n in red_nodes)
        assert len(red_nodes) >= 1
        # Corrected: Check color directly as string
        assert all(n.color == "red" for n in red_nodes if n.text == "Node B")

        purple_nodes = populated_canvas.select_by_color(key=Color.purpol, type='node')
        assert len(purple_nodes) == 0

    def test_select_by_color_edge(self, populated_canvas):
        """Test selecting edges by color."""
        edge_box_blue = Box(id="e_blue", text="Blue Edge", color=get_color_str(Color.blue)) # Use helper here too for consistency
        edge_box_red = Box(id="e_red", text="Red Edge", color="red")
        populated_canvas.edges.extend([edge_box_blue, edge_box_red])

        blue_edges = populated_canvas.select_by_color(key=Color.blue, type='edge')
        assert any(e.id == "e_blue" for e in blue_edges)
        assert len(blue_edges) >= 1
        # Corrected: Check color directly as string
        assert all(e.color == get_color_str(Color.blue) for e in blue_edges if e.id == "e_blue")


        red_edges = populated_canvas.select_by_color(key="red", type='edge')
        assert any(e.id == "e_red" for e in red_edges)
        assert len(red_edges) >= 1
        # Corrected: Check color directly as string
        assert all(e.color == "red" for e in red_edges if e.id == "e_red")

        green_edges = populated_canvas.select_by_color(key=Color.green, type='edge')
        assert len(green_edges) == 0

    def test_select_by_color_all(self, populated_canvas):
        """Test selecting all types (nodes and edges) by color."""
        populated_canvas.add_node("Node D", color=Color.blue)
        edge_box_blue_all = Box(id="e_blue_all", text="Blue Edge All", color=get_color_str(Color.blue))
        populated_canvas.edges.append(edge_box_blue_all)

        blue_elements = populated_canvas.select_by_color(key=Color.blue, type='all')
        assert len(blue_elements) >= 3
        assert any(n.text == "Node A" for n in blue_elements)
        assert any(n.text == "Node D" for n in blue_elements)
        assert any(e.id == "e_blue_all" for e in blue_elements)
        # Corrected: Verify colors are stored as strings
        for elem in blue_elements:
            assert elem.color == get_color_str(Color.blue)


    def test_select_nodes_by_type(self, populated_canvas):
        """Test selecting nodes by type (assuming 'type' is an attribute of Box)."""
        node_text = Box(id="n_text_type", text="Hello World", type="text")
        node_file = Box(id="n_file_type", text="document.pdf", type="file")
        node_url = Box(id="n_url_type", text="https://example.com", type="url")
        populated_canvas.nodes.extend([node_text, node_file, node_url])

        text_nodes = populated_canvas.select_nodes_by_type(key='text')
        assert len(text_nodes) >= 1
        assert any(n.id == "n_text_type" for n in text_nodes)

        file_nodes = populated_canvas.select_nodes_by_type(key='file')
        assert len(file_nodes) >= 1
        assert any(n.id == "n_file_type" for n in file_nodes)

        image_nodes = populated_canvas.select_nodes_by_type(key='image')
        assert len(image_nodes) == 0

    def test_select_nodes_by_text(self, populated_canvas):
        """Test selecting nodes by text content."""
        populated_canvas.add_node("Important Process Step")
        populated_canvas.add_node("Another Process")
        populated_canvas.add_node("Final Node")

        process_nodes = populated_canvas.select_nodes_by_text(key='Process')
        assert len(process_nodes) >= 3
        assert {n.text for n in process_nodes} >= {"Process C", "Important Process Step", "Another Process"}

        start_nodes = populated_canvas.select_nodes_by_text(key='Start')
        assert len(start_nodes) >= 1
        assert any(n.text == "Start" for n in start_nodes)

        non_existent_nodes = populated_canvas.select_nodes_by_text(key='XYZ_NonExistent')
        assert len(non_existent_nodes) == 0

    def test_select_edges_by_text(self, populated_canvas):
        """Test selecting edges by text content."""
        edge1 = Box(id="e1_text", text="Data Flow", from_node="n1", to_node="n2")
        edge2 = Box(id="e2_text", text="Control Signal", from_node="n2", to_node="n3")
        edge3 = Box(id="e3_text", text="Another Data Flow", from_node="n3", to_node="n4")
        populated_canvas.edges.extend([edge1, edge2, edge3])

        data_edges = populated_canvas.select_edges_by_text(key='Data Flow')
        assert len(data_edges) >= 2
        assert {e.id for e in data_edges} >= {"e1_text", "e3_text"}

        control_edges = populated_canvas.select_edges_by_text(key='Control')
        assert len(control_edges) >= 1
        assert any(e.id == "e2_text" for e in control_edges)

        xyz_edges = populated_canvas.select_edges_by_text(key='XYZ_Edge')
        assert len(xyz_edges) == 0

    def test_to_file(self, populated_canvas, tmp_path):
        """Test saving the canvas to a file."""
        output_file = tmp_path / "output_canvas.canvas"
        populated_canvas.to_file(str(output_file))

        assert output_file.exists()
        with open(output_file, 'r') as f:
            content = json.load(f)
            assert "nodes" in content
            assert "edges" in content
            assert len(content["nodes"]) >= len(populated_canvas.nodes) - 3
            assert len(content["edges"]) >= len(populated_canvas.edges)

            assert any(node["text"] == "Node A" for node in content["nodes"])
            assert any(node["text"] == "Start" for node in content["nodes"])
            assert any(edge["text"] == "connects" for edge in content["edges"])

    def test_to_mermaid(self, populated_canvas):
        """Test generating Mermaid string."""
        mermaid_str = populated_canvas.to_mermaid()
        assert isinstance(mermaid_str, str)
        assert len(mermaid_str) > 0
        assert "graph TD" in mermaid_str or "flowchart TD" in mermaid_str

        assert "Node A" in mermaid_str
        assert "Node B" in mermaid_str
        assert "Process C" in mermaid_str
        assert "Start" in mermaid_str
        assert "End" in mermaid_str

        assert "connects" in mermaid_str
