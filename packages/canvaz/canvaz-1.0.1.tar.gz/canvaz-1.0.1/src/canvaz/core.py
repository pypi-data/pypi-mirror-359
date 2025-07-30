"""这是一个包，用于处理canvas的文件，并提供一些方法来操作canvas
本包的核心思路在于获取canvas 中的Node和Edge 结点, 这些结点都是Box格式
通过直接修改Box的属性值来修改Node和Edge
常见的属性值为 id, text, x, y, width, height, color
"""

import json
from enum import Enum
import re
import os
from uuid import uuid4
from .log import Log

logger = Log.logger


class Color(Enum):
    """颜色枚举

    Args:
        Enum (_type_): 颜色枚举

    Attributes:
        gray: 灰色
        red: 红色
        origne: 橙色
        yellow: 黄色
        green: 绿色
        blue: 蓝色
        purpol: 紫色
    """

    gray = "0"
    red = "1"
    origne = "2"
    yellow = "3"
    green = "4"
    blue = "5"
    purpol = "6"


class Range(Enum):
    """搜索范围枚举

    Args:
        Enum (_type_): 范围枚举

    Attributes:
        edge: edge
        node: node
        all: all
    """

    edge = "edge"
    node = "node"
    all = "all"


class Node:
    """Canvas 的结点概念
    """
    def __init__(self, node_info: dict[str, str | dict]):
        """Node对象, 存储Node的属性, 可以使用python标准的属性赋值来修改它

        Args:
            node_info (dict[str,str  |  dict]): _description_

        Attributes:
            self.id : str
            self.text : str
            self.type : str
            self.width : str
            self.height : str
            self.styleAttributes : dict
            self.x : str
            self.y : str
            self.color : str

        """
        self.id = node_info.get("id")
        self.styleAttributes = node_info.get("styleAttributes")
        self.text = node_info.get("text")
        self.type = node_info.get("type")
        self.width = node_info.get("width")
        self.height = node_info.get("height")
        self.x = node_info.get("x")
        self.y = node_info.get("y")
        self.color = node_info.get("color")

    def to_dict(self) -> dict:
        """
        将Edge对象的属性转换为字典格式。

        Returns:
            dict: 包含Edge所有属性的字典。
        """
        _dict = {
            "id": self.id,
            "text": self.text,
            "type": self.type,
            "styleAttributes": self.styleAttributes,
            "width": self.width,
            "height": self.height,
            "x": self.x,
            "y": self.y,
            "color": self.color.value if isinstance(self.color,Color) else self.color,
        }
        return _dict


class Edge:
    """Canvas 的边概念
    """
    def __init__(self, edge_info: dict[str, str | dict]):
        """Edge对象, 存储Edge的属性, 可以使用python标准的属性赋值来修改它

        Args:
            edge_info (dict[str,str  |  dict]): _description_

        Attributes:
            self.id : str
            self.fromNode : str
            self.fromSide : str
            self.styleAttributes : str
            self.toNode : str
            self.toSide : str
            self.color : str

        """
        self.id = edge_info.get("id")
        self.fromNode = edge_info.get("fromNode")
        self.fromSide = edge_info.get("fromSide")
        self.styleAttributes = edge_info.get("styleAttributes")
        self.toNode = edge_info.get("toNode")
        self.toSide = edge_info.get("toSide")
        self.color = edge_info.get("color")

    def to_dict(self) -> dict:
        """
        将Edge对象的属性转换为字典格式。

        Returns:
            dict: 包含Edge所有属性的字典。
        """
        edge_dict = {
            "id": self.id,
            "fromNode": self.fromNode,
            "fromSide": self.fromSide,
            "styleAttributes": self.styleAttributes,
            "toNode": self.toNode,
            "toSide": self.toSide,
            "color": self.color.value if isinstance(self.color,Color) else self.color,
        }
        return edge_dict


class Canvas:
    """提供一些方法来方便的操作Canvas类文件
    """
    def __init__(self, file_path: str):
        """初始化

        Args:
            file_path (str, optional): 传入格式为canvas的文件路径. Defaults to None.

        有一些可以调用的属性
        self.all  canvas文件中的所有源内容
        self.edges edges内容
        self.nodes nodes内容
        self.file_path 文件路径
        """
        assert file_path is not None, "file_path is not None"
        assert os.path.exists(file_path), "file_path is not exists"
        assert file_path.endswith(".canvas"), "file_path is not a canvas file"

        self.file_path = file_path
        with open(file_path, "r") as f:
            text = f.read()
            all = json.loads(text)
        self.all = all
        # 设置默认颜色
        for edge in all.get("edges"):
            if not edge.get("color"):
                edge.setdefault("color", "0")
        for node in all.get("nodes"):
            if not node.get("color"):
                node.setdefault("color", "0")

        self.edges = [Node(i) for i in all.get("edges")]
        self.nodes = [Node(i) for i in all.get("nodes")]

    def add_node(self, text: str, color: Color = Color.gray):
        """添加节点

        Args:
            text (str): 节点文本
            color (Color): 节点颜色. Defaults to Color.gray.
        """
        logger.info("add_node")
        assert isinstance(color, Color)
        self.nodes.append(
            Node({
                "id": str(uuid4())[:16],
                "type": "text",
                "text": text,
                "x": 0,
                "y": 0,
                "width": 250,
                "height": 60,
                "color": color.value,
            })
        )

    def add_edge(self, from_node: str, to_node: str, color: Color | str = Color.gray):
        """TODO 等待实现"""
        pass

    def delete(self):
        """TODO 等待实现"""
        pass

    def select_by_id(self, id: str = "", range: Range = Range.node) -> Node | Edge:
        """可以通过在key中传入id 获取内容

        Args:
            id (str, optional): Node or Edge 类型的id. Defaults to ''.
            range (Range, optional): Range Enum. Defaults to Range.node.

        Returns:
            Node | Edge: 输出类型
        """
        logger.info("select_by_id")

        def check_id(obj, id=""):
            if obj.id == id:
                return obj

        if range.value == "edge":
            for edge in self.edges:
                if check_id(edge, id=id):
                    return edge
        elif range.value == "node":
            for edge in self.nodes:
                if check_id(edge, id=id):
                    return edge
        else:
            for i in self.nodes + self.edges:
                if check_id(i, id=id):
                    return i

    def select_by_color(
        self, color: Color = Color.gray, range: Range = Range.node
    ) -> list[Node | Edge]:
        """可以通过在key中传入颜色

        Args:
            color (Color, optional): _description_. Defaults to Color.gray.
            range (Range, optional): _description_. Defaults to Range.node.

        Returns:
            list[Node | Edge]: _description_
        """
        logger.info("select_by_color")

        def check_key(obj, key=""):
            if obj.color == key.value:
                return obj

        if range.value == "edge":
            objs = self.edges
        elif range.value == "node":
            objs = self.nodes
        elif range.value == "all":
            objs = self.nodes + self.edges
        else:
            objs = self.nodes + self.edges
        return [i for i in objs if check_key(i, key=color)]

    def select_nodes_by_type(self, key: str) -> list[Node]:
        """
        通过类型筛选节点（Node）。

        你可以通过传入类型字符串，获得所有该类型的节点。
        例如:
            select_nodes_by_type(key='text')
            select_nodes_by_type(key='file')

        参数:
            key (str): 节点类型。

        返回:
            list[Node]: 匹配类型的节点列表。
        """
        logger.info("select_nodes_by_type")

        def check_key(obj, key="text"):
            if obj.type == key:
                return obj

        objs = self.nodes
        return [i for i in objs if check_key(i, key=key)]

    def select_nodes_by_text(self, key: str) -> list[Node]:
        """
        优先选择文本包含指定关键字的节点。

        参数:
            key (str): 要在节点文本中搜索的关键字。

        返回:
            list[Node]: 文本包含该关键字的节点列表。
        """
        logger.info("select_nodes_by_text")

        def check_key(obj, key: str = ""):
            obj_text = obj.text or ""
            if key in obj_text:
                return obj

        objs = self.nodes
        return [i for i in objs if check_key(i, key=key)]

    def select_edges_by_text(self, key: str) -> list[Edge]:
        """
        通过文本内容筛选边（Edge）。
        可以通过在 key 中传入文本，获得 label 属性包含该文本的边。

        例如:
            select_edges_by_text(key='text')
            select_edges_by_text(key='file')

        Args:
            key (str): 要搜索的文本。

        Returns:
            list[Edge]: 返回 label 属性包含指定文本的边对象列表。
        """
        logger.info("select_edges_by_text")

        def check_key(obj, key: str = ""):
            obj_text = obj.get("label") or ""
            if key in obj_text:
                return obj

        objs = self.edges
        return [i for i in objs if check_key(i, key=key)]

    def select_by_styleAttributes(self, type="file", key: Color = ""):
        """TODO 等待实现"""
        pass

    def to_file(self, file_path: str) -> None:
        """保存到文件夹

        Args:
            file_path (_type_): _description_
        """
        with open(file_path, "w") as f:
            edges = [i.to_dict() for i in self.edges]
            nodes = [i.to_dict() for i in self.nodes]
            all = {"edges": edges, "nodes": nodes}
            f.write(json.dumps(all))

    def to_mermaid(self):
        """输出为mermaid文件

        Returns:
            str: 对应输出的mermaid文件
        """
        edges = self.edges
        nodes = self.nodes

        def work(text: str):
            # 正则表达式匹配 title 属性
            match = re.search(r"\[\[(.*?)\]\(", text)
            # 替换为新的 title
            new_text = re.sub(r"\[\[(.*?)\)\]", f"[{match.group(1)}]", text)
            return new_text

        def work2(text: str):
            # 正则表达式匹配 title 属性
            match = re.search(r"!\[\[(.*?)\]", text)
            # 替换为新的 title
            new_text = re.sub(r"!\[\[(.*?)\]\]", f"{match.group(1)}", text)
            return new_text

        # 处理节点
        node_lines = []
        for node in nodes:
            node_id = node["id"]
            node_text = node.get("text") or node.get("file")
            node_lines.append(f"{node_id}[{node_text}]")

        # 处理边
        edge_lines = []
        for edge in edges:
            from_node = edge["fromNode"]
            to_node = edge["toNode"]
            if "label" in edge:
                label = edge["label"]
                edge_lines.append(f"{from_node} -->|{label}| {to_node}")
            else:
                edge_lines.append(f"{from_node} --> {to_node}")

        node_lines2 = []
        for node in node_lines:
            try:
                node = work(node)
            except:
                pass
            try:
                node = work2(node)
            except:
                pass
            node_lines2.append(node)

        # 生成 Mermaid.js 格式
        mermaid_graph = "graph TD\n   "
        mermaid_graph += "\n   ".join(node_lines2) + "\n   "
        mermaid_graph += "\n   ".join(edge_lines)

        return mermaid_graph
