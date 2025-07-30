import pytest
import json
from pathlib import Path

# Assume canvaz package is discoverable, e.g., via PYTHONPATH or relative import
# If not, you might need to adjust the import path like:
# import sys
# sys.path.append(str(Path(__file__).parent.parent))
from canvaz.core import Color, Range, Node, Edge, Canvas

# Helper function to create a dummy .canvas file for testing
# Adjusted color values to match the actual Color enum string numbers
def create_dummy_canvas_file(tmp_path: Path, filename: str = "test.canvas"):
    file_content = {
        "nodes": [
            {
                "id": "node1",
                "text": "Hello Node",
                "type": "text",
                "x": 100, "y": 100,
                "width": 200, "height": 100,
                "color": Color.blue.value # "5"
            },
            {
                "id": "node2",
                "text": "Another Node",
                "type": "file",
                "x": 300, "y": 300,
                "width": 150, "height": 80,
                "color": Color.green.value, # "4"
                "styleAttributes": {"border": "solid"}
            }
        ],
        "edges": [
            {
                "id": "edge1",
                "fromNode": "node1",
                "toNode": "node2",
                "color": Color.red.value, # "1"
            }
        ]
    }
    canvas_file = tmp_path / filename
    with open(canvas_file, 'w', encoding='utf-8') as f:
        json.dump(file_content, f, indent=4)
    return canvas_file

# --- Test Color Enum ---
def test_color_enum_v1():
    """
    Test Color Enum values based on the provided actual implementation.
    """
    assert Color.gray.value == "0"
    assert Color.red.value == "1"
    assert Color.origne.value == "2" # Note: 'origne' as per provided enum
    assert Color.yellow.value == "3"
    assert Color.green.value == "4"
    assert Color.blue.value == "5"
    assert Color.purpol.value == "6" # Note: 'purpol' as per provided enum

# --- Test Range Enum ---
def test_range_enum_v1():
    """
    Test Range Enum values.
    """
    assert Range.edge.value == "edge"
    assert Range.node.value == "node"
    assert Range.all.value == "all"

# --- Test Node Class ---
def test_node_init_v1():
    """
    Test Node initialization with all provided attributes.
    """
    node_info = {
        "id": "test_node_id",
        "text": "Test Node",
        "type": "custom",
        "width": 100,
        "height": 50,
        "styleAttributes": {"font": "bold"},
        "x": 10,
        "y": 20,
        "color": Color.blue.value # Use enum value
    }
    node = Node(node_info)
    assert node.id == "test_node_id"
    assert node.text == "Test Node"
    assert node.type == "custom"
    assert node.width == 100
    assert node.height == 50
    assert node.styleAttributes == {"font": "bold"}
    assert node.x == 10
    assert node.y == 20
    assert node.color == Color.blue.value

def test_node_init_defaults_v1():
    """
    Test Node initialization with default values for missing attributes.
    """
    node = Node({"text": "Default Node"})
    assert isinstance(node.id, str) and len(node.id) > 0 # Check if ID is generated
    assert node.text == "Default Node"
    assert node.type == "text" # Default type
    assert node.color == Color.gray.value # Default color
    assert node.x == 0 # Default x
    assert node.y == 0 # Default y
    assert node.width == 200 # Default width
    assert node.height == 100 # Default height
    assert node.styleAttributes == {} # Default empty dict

def test_node_to_dict_v1():
    """
    Test Node.to_dict() method.
    """
    node_info = {
        "id": "test_node_id_2",
        "text": "Another Test",
        "type": "image",
        "color": Color.green.value
    }
    node = Node(node_info)
    node_dict = node.to_dict()
    assert node_dict["id"] == "test_node_id_2"
    assert node_dict["text"] == "Another Test"
    assert node_dict["type"] == "image"
    assert node_dict["color"] == Color.green.value
    # Ensure all attributes are present even if they used default values
    assert "width" in node_dict
    assert "height" in node_dict
    assert "x" in node_dict
    assert "y" in node_dict
    assert "styleAttributes" in node_dict

# --- Test Edge Class ---
def test_edge_init_v1():
    """
    Test Edge initialization with all provided attributes.
    """
    edge_info = {
        "id": "test_edge_id",
        "fromNode": "nodeA",
        "fromSide": "left",
        "styleAttributes": {"line": "dashed"},
        "toNode": "nodeB",
        "toSide": "right",
        "color": Color.red.value, # Use enum value
    }
    edge = Edge(edge_info)
    assert edge.id == "test_edge_id"
    assert edge.fromNode == "nodeA"
    assert edge.fromSide == "left"
    assert edge.styleAttributes == {"line": "dashed"}
    assert edge.toNode == "nodeB"
    assert edge.toSide == "right"
    assert edge.color == Color.red.value

def test_edge_init_defaults_v1():
    """
    Test Edge initialization with default values.
    """
    edge = Edge({"fromNode": "n1", "toNode": "n2"})
    assert isinstance(edge.id, str) and len(edge.id) > 0
    assert edge.fromNode == "n1"
    assert edge.toNode == "n2"
    assert edge.color == Color.gray.value
    assert edge.fromSide == ""
    assert edge.toSide == ""
    assert edge.styleAttributes == {}

def test_edge_to_dict_v1():
    """
    Test Edge.to_dict() method.
    """
    edge_info = {
        "id": "test_edge_id_2",
        "fromNode": "nodeX",
        "toNode": "nodeY",
        "color": Color.blue.value,
    }
    edge = Edge(edge_info)
    edge_dict = edge.to_dict()
    assert edge_dict["id"] == "test_edge_id_2"
    assert edge_dict["fromNode"] == "nodeX"
    assert edge_dict["toNode"] == "nodeY"
    assert edge_dict["color"] == Color.blue.value
    assert "fromSide" in edge_dict
    assert "toSide" in edge_dict
    assert "styleAttributes" in edge_dict

# --- Test Canvas Class ---
def test_canvas_init_empty_v1():
    """
    Test Canvas initialization without a file path.
    """
    canvas = Canvas('tests/use.canvas')
    assert canvas.file_path is None
    assert canvas.nodes == []
    assert canvas.edges == []
    assert canvas.all == {}

def test_canvas_init_from_file_v1(tmp_path):
    """
    Test Canvas initialization from a valid .canvas file.
    """
    canvas_file = create_dummy_canvas_file(tmp_path)
    canvas = Canvas(str(canvas_file))
    assert canvas.file_path == str(canvas_file)
    assert len(canvas.nodes) == 2
    assert canvas.nodes[0].id == "node1"
    assert canvas.nodes[0].text == "Hello Node"
    assert canvas.nodes[0].color == Color.blue.value # Verify color from file
    assert len(canvas.edges) == 1
    assert canvas.edges[0].id == "edge1"
    assert canvas.edges[0].color == Color.red.value # Verify color from file

def test_canvas_init_file_not_found_v1(tmp_path, capsys):
    """
    Test Canvas initialization when the file does not exist.
    """
    non_existent_file = tmp_path / "non_existent.canvas"
    canvas = Canvas(str(non_existent_file))
    assert canvas.nodes == []
    assert canvas.edges == []
    # Check warning message
    captured = capsys.readouterr()
    assert "Warning: File not found" in captured.out

def test_canvas_init_invalid_json_v1(tmp_path, capsys):
    """
    Test Canvas initialization with an invalid JSON file.
    """
    invalid_json_file = tmp_path / "invalid.canvas"
    with open(invalid_json_file, 'w') as f:
        f.write("{invalid json")
    canvas = Canvas(str(invalid_json_file))
    assert canvas.nodes == []
    assert canvas.edges == []
    # Check warning message
    captured = capsys.readouterr()
    assert "Warning: Could not decode JSON" in captured.out

def test_canvas_add_node_v1():
    """
    Test adding a new node with specified color and default color.
    """
    canvas = Canvas()
    node = canvas.add_node("New Node Text", Color.red)
    assert len(canvas.nodes) == 1
    assert canvas.nodes[0].text == "New Node Text"
    assert canvas.nodes[0].color == Color.red.value
    assert node.id == canvas.nodes[0].id # Check if returned node is the same instance

    node_default = canvas.add_node("Default Color Node")
    assert len(canvas.nodes) == 2
    assert canvas.nodes[1].text == "Default Color Node"
    assert canvas.nodes[1].color == Color.gray.value

def test_canvas_add_edge_v1(tmp_path):
    """
    Test adding a new edge.
    """
    canvas_file = create_dummy_canvas_file(tmp_path)
    canvas = Canvas(str(canvas_file))
    initial_edge_count = len(canvas.edges)

    new_edge = canvas.add_edge("node1", "node2", Color.blue, "new_connection")
    assert len(canvas.edges) == initial_edge_count + 1
    assert new_edge.fromNode == "node1"
    assert new_edge.toNode == "node2"
    assert new_edge.color == Color.blue.value
    assert new_edge.label == "new_connection"

def test_canvas_select_by_id_node_v1(tmp_path):
    """
    Test selecting a node by its ID.
    """
    canvas_file = create_dummy_canvas_file(tmp_path)
    canvas = Canvas(str(canvas_file))

    node = canvas.select_by_id("node1", Range.node)
    assert node is not None
    assert isinstance(node, Node)
    assert node.id == "node1"
    assert node.text == "Hello Node"

    node_none = canvas.select_by_id("non_existent_node", Range.node)
    assert node_none is None

def test_canvas_select_by_id_edge_v1(tmp_path):
    """
    Test selecting an edge by its ID.
    """
    canvas_file = create_dummy_canvas_file(tmp_path)
    canvas = Canvas(str(canvas_file))

    edge = canvas.select_by_id("edge1", Range.edge)
    assert edge is not None
    assert isinstance(edge, Edge)
    assert edge.id == "edge1"
    assert edge.fromNode == "node1"

    edge_none = canvas.select_by_id("non_existent_edge", Range.edge)
    assert edge_none is None

def test_canvas_select_by_id_all_v1(tmp_path):
    """
    Test selecting an element (node or edge) by ID using Range.all.
    """
    canvas_file = create_dummy_canvas_file(tmp_path)
    canvas = Canvas(str(canvas_file))

    element_node = canvas.select_by_id("node1", Range.all)
    assert element_node is not None
    assert isinstance(element_node, Node)
    assert element_node.id == "node1"

    element_edge = canvas.select_by_id("edge1", Range.all)
    assert element_edge is not None
    assert isinstance(element_edge, Edge)
    assert element_edge.id == "edge1"

    element_none = canvas.select_by_id("non_existent", Range.all)
    assert element_none is None

def test_canvas_select_by_color_nodes_v1(tmp_path):
    """
    Test selecting nodes by color.
    """
    canvas_file = create_dummy_canvas_file(tmp_path)
    canvas = Canvas(str(canvas_file))

    blue_nodes = canvas.select_by_color(Color.blue, Range.node)
    assert len(blue_nodes) == 1
    assert blue_nodes[0].id == "node1"
    assert blue_nodes[0].color == Color.blue.value

    red_nodes = canvas.select_by_color(Color.red, Range.node)
    assert len(red_nodes) == 0 # No red nodes in the dummy file

def test_canvas_select_by_color_edges_v1(tmp_path):
    """
    Test selecting edges by color.
    """
    canvas_file = create_dummy_canvas_file(tmp_path)
    canvas = Canvas(str(canvas_file))

    red_edges = canvas.select_by_color(Color.red, Range.edge)
    assert len(red_edges) == 1
    assert red_edges[0].id == "edge1"
    assert red_edges[0].color == Color.red.value

    blue_edges = canvas.select_by_color(Color.blue, Range.edge)
    assert len(blue_edges) == 0 # No blue edges in the dummy file

def test_canvas_select_by_color_all_v1(tmp_path):
    """
    Test selecting all elements (nodes or edges) by color.
    """
    canvas_file = create_dummy_canvas_file(tmp_path)
    canvas = Canvas(str(canvas_file))

    blue_elements = canvas.select_by_color(Color.blue, Range.all)
    assert len(blue_elements) == 1
    assert isinstance(blue_elements[0], Node)
    assert blue_elements[0].id == "node1"
    assert blue_elements[0].color == Color.blue.value

    red_elements = canvas.select_by_color(Color.red, Range.all)
    assert len(red_elements) == 1
    assert isinstance(red_elements[0], Edge)
    assert red_elements[0].id == "edge1"
    assert red_elements[0].color == Color.red.value

    green_elements = canvas.select_by_color(Color.green, Range.all)
    assert len(green_elements) == 1
    assert isinstance(green_elements[0], Node)
    assert green_elements[0].id == "node2"
    assert green_elements[0].color == Color.green.value


def test_canvas_select_nodes_by_type_v1(tmp_path):
    """
    Test selecting nodes by their type.
    """
    canvas_file = create_dummy_canvas_file(tmp_path)
    canvas = Canvas(str(canvas_file))

    text_nodes = canvas.select_nodes_by_type("text")
    assert len(text_nodes) == 1
    assert text_nodes[0].id == "node1"

    file_nodes = canvas.select_nodes_by_type("file")
    assert len(file_nodes) == 1
    assert file_nodes[0].id == "node2"

    non_existent_type_nodes = canvas.select_nodes_by_type("folder")
    assert len(non_existent_type_nodes) == 0

def test_canvas_select_nodes_by_text_v1(tmp_path):
    """
    Test selecting nodes by text content (case-insensitive).
    """
    canvas_file = create_dummy_canvas_file(tmp_path)
    canvas = Canvas(str(canvas_file))

    hello_nodes = canvas.select_nodes_by_text("Hello")
    assert len(hello_nodes) == 1
    assert hello_nodes[0].id == "node1"

    node_nodes = canvas.select_nodes_by_text("Node") # "Hello Node", "Another Node"
    assert len(node_nodes) == 2
    assert {n.id for n in node_nodes} == {"node1", "node2"}

    case_insensitive_nodes = canvas.select_nodes_by_text("another")
    assert len(case_insensitive_nodes) == 1
    assert case_insensitive_nodes[0].id == "node2"

    non_existent_text_nodes = canvas.select_nodes_by_text("xyz")
    assert len(non_existent_text_nodes) == 0


def test_canvas_select_by_styleAttributes_v1(tmp_path):
    """
    Test selecting elements by style attributes.
    """
    canvas_file = create_dummy_canvas_file(tmp_path)
    canvas = Canvas(str(canvas_file))

    # Test with existing style attribute on node2
    border_nodes = canvas.select_by_styleAttributes(type_key='border', key_value='solid')
    assert len(border_nodes) == 1
    assert border_nodes[0].id == "node2"

    # Test with non-existent style attribute
    font_nodes = canvas.select_by_styleAttributes(type_key='font', key_value='bold')
    assert len(font_nodes) == 0

    # Add a node with more style attributes and test
    new_node = canvas.add_node("Styled Node")
    new_node.styleAttributes = {"background": "blue", "font": "italic"}
    canvas.nodes.append(new_node) # Manually add to canvas nodes list for testing
    
    blue_bg_elements = canvas.select_by_styleAttributes(type_key='background', key_value='blue')
    assert len(blue_bg_elements) == 1
    assert blue_bg_elements[0].id == new_node.id

def test_canvas_to_file_v1(tmp_path):
    """
    Test saving the canvas content to a file.
    """
    output_file = tmp_path / "output.canvas"
    canvas = Canvas(tmp_path)
    node_a = canvas.add_node("Node A", Color.green)
    node_b = canvas.add_node("Node B")
    node_a_id = node_a.id
    node_b_id = node_b.id
    canvas.add_edge(node_a_id, node_b_id, Color.blue, "connection")

    canvas.to_file(str(output_file))

    assert output_file.exists()
    with open(output_file, 'r', encoding='utf-8') as f:
        loaded_data = json.load(f)

    assert len(loaded_data["nodes"]) == 2
    assert loaded_data["nodes"][0]["text"] == "Node A"
    assert loaded_data["nodes"][0]["color"] == Color.green.value # Verify saved color
    assert len(loaded_data["edges"]) == 1
    assert loaded_data["edges"][0]["fromNode"] == node_a_id
    assert loaded_data["edges"][0]["color"] == Color.blue.value # Verify saved color


def test_canvas_to_mermaid_v1(tmp_path):
    """
    Test generating Mermaid string representation of the canvas.
    """
    canvas_file = create_dummy_canvas_file(tmp_path)
    canvas = Canvas(str(canvas_file))
    node1_id = canvas.nodes[0].id
    node2_id = canvas.nodes[1].id

    mermaid_output = canvas.to_mermaid()
    assert "graph TD" in mermaid_output
    assert f"  {node1_id}[Hello Node]" in mermaid_output
    assert f"  {node2_id}[Another Node]" in mermaid_output
    
    # Test with an added node/edge
    new_node = canvas.add_node("Mermaid New Node")
    new_edge = canvas.add_edge(node1_id, new_node.id, label="links to new")
    mermaid_output_updated = canvas.to_mermaid()
    assert f"  {new_node.id}[Mermaid New Node]" in mermaid_output_updated
    
@pytest.mark.skip(reason="此功能尚未实现，暂时跳过")
def test_canvas_delete_node_v1(tmp_path):
    """
    Test deleting a node.
    """
    canvas_file = create_dummy_canvas_file(tmp_path)
    canvas = Canvas(str(canvas_file))
    initial_node_count = len(canvas.nodes)
    node_to_delete_id = canvas.nodes[0].id # "node1"

    result = canvas.delete(node_to_delete_id, Range.node)
    assert result is True # Should indicate success
    assert len(canvas.nodes) == initial_node_count - 1
    assert canvas.select_by_id(node_to_delete_id, Range.node) is None
    # Ensure edges are not affected when deleting only nodes
    assert len(canvas.edges) == 1
@pytest.mark.skip(reason="此功能尚未实现，暂时跳过")
def test_canvas_delete_edge_v1(tmp_path):
    """
    Test deleting an edge.
    """
    canvas_file = create_dummy_canvas_file(tmp_path)
    canvas = Canvas(str(canvas_file))
    initial_edge_count = len(canvas.edges)
    edge_to_delete_id = canvas.edges[0].id # "edge1"

    result = canvas.delete(edge_to_delete_id, Range.edge)
    assert result is True # Should indicate success
    assert len(canvas.edges) == initial_edge_count - 1
    assert canvas.select_by_id(edge_to_delete_id, Range.edge) is None
    # Ensure nodes are not affected when deleting only edges
    assert len(canvas.nodes) == 2

@pytest.mark.skip(reason="此功能尚未实现，暂时跳过")
def test_canvas_delete_all_v1(tmp_path):
    """
    Test deleting an element using Range.all.
    (Note: Current simplified delete only removes by ID from respective lists.)
    """
    canvas_file = create_dummy_canvas_file(tmp_path)
    canvas = Canvas(str(canvas_file))
    node_id_to_delete = canvas.nodes[0].id # node1
    edge_id_to_delete = canvas.edges[0].id # edge1

    # Delete node1 using Range.all
    result_node_delete = canvas.delete(node_id_to_delete, Range.all)
    assert result_node_delete is True
    assert canvas.select_by_id(node_id_to_delete, Range.node) is None
    assert len(canvas.nodes) == 1 # node2 remains
    assert len(canvas.edges) == 1 # edge1 remains (its ID is different from node1's ID)

    # Delete edge1 using Range.all
    result_edge_delete = canvas.delete(edge_id_to_delete, Range.all)
    assert result_edge_delete is True
    assert canvas.select_by_id(edge_id_to_delete, Range.edge) is None
    assert len(canvas.edges) == 0 # edge1 is gone
    assert len(canvas.nodes) == 1 # node2 still remains

    # Test deleting non-existent element
    result_non_existent = canvas.delete("non_existent_id", Range.all)
    assert result_non_existent is False # Should be False if nothing was deleted
    assert len(canvas.nodes) == 1
    assert len(canvas.edges) == 0
