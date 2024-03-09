# -*- coding: utf-8 -*-
from graphviz import Digraph

class Node:
    pos_counter = 0
    followPosTable = dict()
    posTable = dict()
    
    def __init__(self, value, left=None, right=None, pos=None, nullable=None):
        self.value = value
        self.left = left
        self.right = right
        self.pos = pos
        self.nullable = nullable
        self.firstPos = set()
        self.lastPos = set()
        
def create_ast(postfix):
    stack = []
    operators = ['|','*','.']
    Node.pos_counter = 0
    Node.followPosTable = dict()
    Node.posTable = dict()

    j=0
    while j<len(postfix):
        char = postfix[j]
        new_node = Node(value=char)

        if char not in operators:  # si no es un operador, se crea un nuevo nodo y se empuja en la pila
            if char=='ε':
                new_node.nullable = True
            else:
                if char[0]=='\\' and len(char)>1:
                    char = char[1]
                    new_node.value = char
                        
                Node.pos_counter+=1
                new_node.pos = Node.pos_counter
                Node.followPosTable[new_node.pos] = set()
                
                if char in Node.posTable:
                    Node.posTable[char].add(new_node.pos)
                else:
                    Node.posTable[char] = set()
                    Node.posTable[char].add(new_node.pos)
                
                #Nulidad, Primera Pos y Ultima Pos
                new_node.nullable = False
                new_node.firstPos.add(new_node.pos)
                new_node.lastPos.add(new_node.pos)
                
        else:  # si es un operador, se crea un nuevo nodo y se conecta con dos nodos anteriores
            new_node.right = stack.pop()  # el segundo nodo se convierte en el hijo derecho
            
            if char != '*':  # '*' es un operador unario
                new_node.left = stack.pop()  # el primer nodo se convierte en el hijo izquierdo
                
            if char=='|':
                #Nulidad, Primera Pos y Ultima Pos
                new_node.nullable = new_node.left.nullable or new_node.right.nullable
                new_node.firstPos = new_node.left.firstPos.union(new_node.right.firstPos)
                new_node.lastPos = new_node.left.lastPos.union(new_node.right.lastPos)
            elif char=='.':
                #Nulidad
                new_node.nullable = new_node.left.nullable and new_node.right.nullable
                
                #Primera Pos
                if new_node.left.nullable:
                    new_node.firstPos = new_node.left.firstPos.union(new_node.right.firstPos)
                else:
                    new_node.firstPos = new_node.left.firstPos
                    
                #Ultima Pos
                if new_node.right.nullable:
                    new_node.lastPos = new_node.left.lastPos.union(new_node.right.lastPos)
                else:
                    new_node.lastPos = new_node.right.lastPos
                 
                #Siguiente Pos
                for i in new_node.left.lastPos:
                    Node.followPosTable[i].update(new_node.right.firstPos)
                    
            else:
                #Nulidad, Primera Pos y Ultima Pos
                new_node.nullable = True
                new_node.firstPos = new_node.right.firstPos
                new_node.lastPos = new_node.right.lastPos
                
                #Siguiente Pos
                for i in new_node.lastPos:
                    Node.followPosTable[i].update(new_node.firstPos)
        
        j+=1
        stack.append(new_node)
    
    return stack[0] if stack else None  # el último nodo en la pila es la raíz del AST

def plot_tree(root, graph=None):
    if graph is None:
        graph = Digraph()
        graph.node(name=str(id(root)), label=root.value)
    if root.left:  # si el nodo izquierdo existe, se agrega al gráfico y se conecta con la raíz
        graph.node(name=str(id(root.left)), label=root.left.value)
        graph.edge(str(id(root)), str(id(root.left)))
        plot_tree(root.left, graph)
    if root.right:  # si el nodo derecho existe, se agrega al gráfico y se conecta con la raíz
        graph.node(name=str(id(root.right)), label=root.right.value)
        graph.edge(str(id(root)), str(id(root.right)))
        plot_tree(root.right, graph)
    return graph