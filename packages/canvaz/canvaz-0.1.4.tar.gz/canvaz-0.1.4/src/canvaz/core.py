""" 这是一个包，用于处理canvas的文件，并提供一些方法来操作canvas 
    本包的核心思路在于获取canvas 中的Node和Edge 结点, 这些结点都是Box格式 
    通过直接修改Box的属性值来修改Node和Edge
    常见的属性值为 id, text, x, y, width, height, color
"""
import json
from enum import Enum
import re
import os
from uuid import uuid4
from box import Box
from .log import Log
logger = Log.logger


class Color(Enum):
    """ 颜色枚举

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

class Canvas():
    def __init__(self,file_path:str):
        """ 初始化

        Args:
            file_path (str, optional): 传入格式为canvas的文件路径. Defaults to None.
        """
        assert file_path is not None, 'file_path is not None'
        assert os.path.exists(file_path), 'file_path is not exists'
        assert file_path.endswith('.canvas'), 'file_path is not a canvas file'

        self.file_path = file_path
        with open(file_path,'r') as f:
            text = f.read()
            bdict = Box(json.loads(text))
        self.bdict = bdict
        # 设置默认颜色
        for edge in bdict.edges:
            if not edge.get('color'):
                edge.setdefault('color','0')
        for node in bdict.nodes:
            if not node.get('color'):
                node.setdefault('color','0')
                
        self.edges = bdict.edges
        self.nodes = bdict.nodes
    
    def add_node(self,text:str,color:Color | str =Color.gray):
        """ 添加节点

        Args:
            text (str): 节点文本
            color (Color | str, optional): 节点颜色. Defaults to Color.gray.
        """
        logger.info('add_node')
        if isinstance(color,Color):
            color = color.value
        else:
            color = color
        self.nodes.append(
            {'id': str(uuid4())[:16], 
             'type': 'text', 
             'text': text, 
             'x': 0, 'y': 0, 
             'width': 250, 'height': 60, 
             'color': color.value})
    
    def add_edge(self,from_node:str,to_node:str,color:Color | str =Color.gray):
        """ TODO 等待实现
        """
        pass

    def delete(self):
        """ TODO 等待实现
        """
        pass

    
    def select_by_id(self,key:str='',type:str ='edge',)->Box:
        """ 通过id 来选择 Box
        可以通过在key中传入id 获得不同type的
        Args:
            type (str, optional): 类型. Defaults to 'edge'.
            key (str, optional): id. Defaults to ''.
        
        For example:
            select_by_id(type='edge',key='123')
            select_by_id(type='node',key='123')
            
        Returns:
            Box: 返回的Box
        """
        logger.info('select_by_id')

        def check_id(obj,id=''):
            if obj.id == id:
                return obj
        id = key
        if type == 'edge':
            for edge in self.edges:
                if check_id(edge,id=id):
                    return edge
        else:
            for node in self.nodes:
                if check_id(node,id=id):
                    return node
                
    def select_by_color(self, key: Color | str =Color.gray, type='edge')->list[Box]:
        """ 通过颜色来选择 Box
        可以通过在key中传入颜色 获得不同type的 Box
        
        For example:
            select_by_color(key='0',type='edge')
            select_by_color(key='0',type='node')
            select_by_color(key='0',type='all')
            
        Args:
            key (Color, optional): 颜色. Defaults to ''.
            type (str, optional): 类型. Defaults to 'edge'.

        Returns:
            Box: 返回的Box
        """
        logger.info('select_by_color')
        def check_key(obj, key=''):
            if obj.color == key.value:
                return obj
            
        color = key
        if type == 'edge':              
            # If type is 'edge', select from edges
            objs = self.edges
        elif type == 'node':
            # If type is 'node', select from nodes
            objs = self.nodes
        elif type == 'all':
            # If type is 'all', select from both nodes and edges
            objs = self.nodes + self.edges
        else:
            # Default to select from both nodes and edges if type is unknown
            objs = self.nodes + self.edges
            
        # Return a list of objects whose color matches the key
        return [i for i in objs if check_key(i, key=color)]
    
    def select_nodes_by_type(self,key:str='')->list[Box]:
        """ 通过类型来选择 Box
        可以通过在key中传入类型 获得不同type的 Box(edge 只有text类型,所以没有设置type参数)
        
        For example:
            select_nodes_by_type(key='text')
            select_nodes_by_type(key='file')
            
        Args:
            key (str, optional): 类型. Defaults to ''.

        Returns:
            list: 返回的Box
        """
        logger.info('select_nodes_by_type')
        def check_key(obj,key='text'):
            if obj.type == key:
                return obj
        objs = self.nodes

        return [i for i in objs if check_key(i,key=key)]

    def select_nodes_by_text(self,key:str='')->list:
        """
        Select nodes containing specific text.

        key: str
            The text to search for in nodes.
        
        Returns a list of nodes whose text contains the specified key.
        """
        logger.info('select_nodes_by_text')
        def check_key(obj,key:str=''):
            obj_text = obj.get('text') or ''
            if key in obj_text:
                return obj
        objs = self.nodes
        return [i for i in objs if check_key(i,key=key)]
    def select_edges_by_text(self,key:str='')->list[Box]:
        """ 通过文本来选择 Box
        可以通过在key中传入文本 获得不同type的 Box(edge 只有label类型,所以没有设置type参数)
        
        For example:
            select_edges_by_text(key='text')
            select_edges_by_text(key='file')
            

        Args:
            key (str, optional): 文本. Defaults to ''.

        Returns:
            list: 返回的Box
        """
        logger.info('select_edges_by_text')
        def check_key(obj,key:str=''):
            obj_text = obj.get('label') or ''
            if key in obj_text:
                return obj
        objs = self.edges
        return [i for i in objs if check_key(i,key=key)]
        
    def select_by_styleAttributes(self,type = 'file',key:Color=''):
        """ TODO 等待实现
        """
        pass
    
    def to_file(self,file_path:str)->None:
        """保存到文件夹

        Args:
            file_path (_type_): _description_
        """
        with open(file_path,'w') as f:
            f.write(self.bdict.to_json())

    def to_mermaid(self):
        """输出为mermaid文件

        Returns:
            str: 对应输出的mermaid文件
        """
        edges = self.edges
        nodes = self.nodes
    
        def work(text:str):
            # 正则表达式匹配 title 属性
            match = re.search(r'\[\[(.*?)\]\(', text)
            # 替换为新的 title
            new_text = re.sub(r'\[\[(.*?)\)\]', f'[{match.group(1)}]', text)
            return new_text
        def work2(text:str):
            # 正则表达式匹配 title 属性
            match = re.search(r'!\[\[(.*?)\]', text)
            # 替换为新的 title
            new_text = re.sub(r'!\[\[(.*?)\]\]', f'{match.group(1)}', text)
            return new_text

        # 处理节点
        node_lines = []
        for node in nodes:
            node_id = node['id']
            node_text = node.get('text') or node.get('file')
            node_lines.append(f"{node_id}[{node_text}]")

        # 处理边
        edge_lines = []
        for edge in edges:
            from_node = edge['fromNode']
            to_node = edge['toNode']
            if 'label' in edge:
                label = edge['label']
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
