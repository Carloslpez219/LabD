
from graphviz import Digraph
from tabulate import tabulate
from abc import ABC, abstractmethod
import pickle

#Clase de estado de LR Automata
class LRAutomataState:
    def __init__(self,afd,canonicalSet=set()):
        self.name = afd.state_counter

        #Modificacion de state_counter y states de la instancia de AFD dada
        afd.state_counter = afd.state_counter[0]+str(int(afd.state_counter[1:]) + 1)
        afd.states.add(self)

        self.canonicalSet = canonicalSet

        self.transitions = {}
        self.is_accept = False

#Clase LRAutomata
class LRAutomata:
    def __init__(self):
        self.start = None
        self.accept = set()
        self.states = set()
        self.state_counter = 'I'+str(0)

# Funcion para representar un item en forma de string
def represent_item(item):
    value = list(item[1])
    position = item[2]

    value.insert(position,'.')

    production = item[0] + ' → '
    production += ' '.join(value)

    return production

#Funcion para aumentar una gramatica
def augment_grammar(grammar):
    new_grammar = {}

    simbolo_inicial = next(iter(grammar))
    new_simbolo_inicial = simbolo_inicial + '`'
    new_grammar[new_simbolo_inicial] = [simbolo_inicial]

    new_grammar.update(grammar)
    return new_grammar

# Cerradura de un conjunto de items
def closure(I,grammar):
    J = I

    while True:
        new_items = set()
        for head, body, indice_punto in J:
            if indice_punto < len(body):  # Verificacion de posicion del punto antes del final
                simbolo = body[indice_punto]
                # Si el simbolo es un no terminal, se agregan las producciones
                if simbolo in set(grammar.keys()):
                    for production in grammar[simbolo]:
                        item = (simbolo, tuple(production.split(' ')), 0)  # Punto al inicio
                        if item not in J:
                            new_items.add(item)
        if not new_items:
            break  # Finalizacion cuando no hay nuevos items
        J.update(new_items)

    return J

# Funcion GOTO
def goto(I,X,grammar):
    res = set()
    for head, body, indice_punto in I:
        if indice_punto < len(body):  # Verificacion de posicion del punto antes del final
            simbolo = body[indice_punto]
            if simbolo == X:
                res = res.union(closure({(head,body,indice_punto+1)},grammar))
    
    return res


def getGrammarSymbols(grammar):
    grammar_symbols = set(grammar.keys())

    for value in grammar.values():
        for prod in value:
            grammar_symbols = grammar_symbols.union(set(prod.split(' ')))
            
    return grammar_symbols

# Generacion de automata
def generate_LR0Automata(grammar):
    automata  = LRAutomata()
    
    grammar_symbols = getGrammarSymbols(grammar)    
    
    simbolo = next(iter(grammar))

    res = closure({(simbolo,tuple(grammar[simbolo][0].split(' ')),0)},grammar)
    initial_state = LRAutomataState(automata,res)
    automata.start = initial_state

    C = {initial_state}
    
    while True:
        new_states = set()

        for state in C:
            for X in grammar_symbols:
                res = goto(state.canonicalSet,X,grammar)

                if len(res)>0:
                    if res not in [state.canonicalSet for state in C]:
                        new_state = LRAutomataState(automata,res)
                        new_states.add(new_state)
                        state.transitions[X] = [new_state]

                        if (simbolo,tuple(grammar[simbolo][0].split(' ')),1) in new_state.canonicalSet:
                            new_state.is_accept = True
                            automata.accept.add(new_state)
                    else:
                        for stock_state in C:
                            if res == stock_state.canonicalSet:
                                state.transitions[X] = [stock_state]

        if not new_states:
            break  # Finalizacion cuando no hay nuevos estados
        C.update(new_states)

    return automata


# Plot Automata LR
def plot_af(state, graph=None, visited=None):
    if visited is None:
        visited = set()

    if state in visited:
        return graph

    if graph is None:
        graph = Digraph(engine='dot')
        graph.attr(rankdir='LR') 

    label = state.name+'\n'
    for item in state.canonicalSet:
        label += represent_item(item)+'\n'

    label = label[:-1]
    
    if state.is_accept:
        graph.node(name=str(id(state)), label=label, shape='box', color="green", fontsize='10')
        graph.node(name="accept", label="accept", shape='plaintext', fontsize='10')
        graph.edge(str(id(state)), "accept", label="$", fontsize='10')

        if len(visited)==0:
             graph.node(name="start", label="start", shape='point', fontsize='10')
             graph.edge("start", str(id(state)), label="inicio", fontsize='10')
    elif len(visited)==0:
        graph.node(name="start", label="start", shape='point', fontsize='10')
        graph.node(name=str(id(state)), label=label, shape='box', color="green", fontsize='10')
        graph.edge("start", str(id(state)), label="inicio", fontsize='10')
    else:
        graph.node(name=str(id(state)), label=label, shape='box', fontsize='10')
        
    visited.add(state)

    for symbol, next_states in state.transitions.items():
        for next_state in next_states:
            graph.edge(str(id(state)), str(id(next_state)), label=symbol, fontsize='10')
            plot_af(next_state, graph, visited)

    return graph

def first(symbol,grammar):
    firstSet = set()
    
    if symbol not in set(grammar.keys()):
        firstSet.add(symbol)
    elif symbol in set(grammar.keys()):
        for prod in grammar[symbol]:
            symbols = prod.split(' ')
            for i in range(0,len(symbols)):
                if symbols[i]!= symbol:
                    res = first(symbols[i],grammar)
                    if '' not in res:
                        firstSet.update(res)
                        break
                    elif i==len(symbols)-1:
                        firstSet.add('')
                else:
                    break
    else:
        firstSet.add('')


    print(firstSet)
        
    return firstSet

def firstString(symbols,grammar):
    firstSet = set()
    
    symbols = symbols.split(' ')
    for i in range(0,len(symbols)):
        res = first(symbols[i],grammar)
        if i==0 or '' not in res:
            firstSet.update(res)
        elif i==len(symbols)-1:
            firstSet.add('')
            
    return firstSet

def follow(non_terminal,grammar):
        if non_terminal not in set(grammar.keys()):
            return None
        
        followSet = set()    
        simbolo_inicial = next(iter(grammar))
        
        if non_terminal == simbolo_inicial:
            followSet.add('$')
            
        for head,prods in grammar.items():
            for prod in prods:
                prod = prod.split(' ')
                for i in range(0,len(prod)):
                    if non_terminal==prod[i]:
                        if i<len(prod)-1:
                            firstSet = first(prod[i+1],grammar)
                            if '' in firstSet:
                                if head!=non_terminal:
                                    followSet.update(follow(head,grammar))
                                    
                                firstSet.remove('')
                                
                            followSet.update(firstSet)
                        else:
                            if head!=non_terminal:
                                    followSet.update(follow(head,grammar))
                          
            print(followSet)

        return followSet

#Funcion para obtencion de no terminales
def getNonTerminals(grammar):
    non_terminals = set(grammar.keys())
    
    return non_terminals

#Funcion para generacion de Tabla de Parseo SLR
def generate_SLRTable(grammar):
    
    automata = generate_LR0Automata(grammar)
    automata_graph = plot_af(automata.start)
    nombre_archivo_pdf = 'Automata LR'
    automata_graph.view(filename=nombre_archivo_pdf,cleanup=True)

    grammar_symbols = getGrammarSymbols(grammar)
    grammar_symbols.remove(next(iter(grammar)))
    
    non_terminals = getNonTerminals(grammar)
    non_terminals.remove(next(iter(grammar)))
    
    terminals = grammar_symbols.difference(non_terminals)
    
    parsing_table = goto_transitions(automata,non_terminals)
    accept_transitions(automata,parsing_table)
    
    if action_transitions(automata,parsing_table,terminals,grammar):
        return parsing_table
    else:
        return None

#Funcion para definir los valores GOTO de la tabla SLR    
def goto_transitions(automata,non_terminals):
    parsing_table = dict()
    
    for state in automata.states:
        parsing_table[state.name] = dict()
        for symbol in non_terminals:
            if symbol in state.transitions:
                nextState = state.transitions[symbol][0]
                parsing_table[state.name][symbol] = nextState.name
            else:
                parsing_table[state.name][symbol] = None
        
    return parsing_table

#Funcion para definir aceptacion
def accept_transitions(automata,parsing_table):
    for state in automata.states:
        if state in automata.accept:
            parsing_table[state.name]['$'] = "acc"
        else:
            parsing_table[state.name]['$'] = None

#Funcion para obtener las reglas de una gramatica
def getRules(grammar):
    rules = []
    for head,bodies in grammar.items():
        for body in bodies:
            rules.append(head+' -> '+body)
        
    return rules
            
#Funcion para definir los valores ACTION de la tabla SLR
def action_transitions(automata,parsing_table,terminals,grammar):
    rules = getRules(grammar)
        
    for state in automata.states:
        for symbol in terminals:
            if symbol in state.transitions:
                nextState = state.transitions[symbol][0]
                parsing_table[state.name][symbol] = 's'+nextState.name
            else:
                parsing_table[state.name][symbol] = None
                
        for head, body, indice_punto in state.canonicalSet:
            if indice_punto==len(body) and head!=next(iter(grammar)):
                values = follow(head,grammar)
                index = rules.index(head+' -> '+' '.join(body))
                
                for symbol in values:
                    if parsing_table[state.name][symbol] == None:
                        parsing_table[state.name][symbol] = 'r'+str(index)
                    elif parsing_table[state.name][symbol][0] == 's':
                        print("ERROR: Conflicto shif-reduce en la gramatica")
                        return False
                    else:
                        print("ERROR: Conflicto reduce-reduce en la gramatica")
                        return False
                    
    return True

#Funcion para impresion de la tabla de parseo SLR
def print_parsing_table(parsing_table):
    # Crear los encabezados de la tabla extrayendo las llaves de cualquier estado (elegimos el estado 0 como ejemplo)
    headers = ["State"] + list(parsing_table['I0'].keys())
    # Preparar las filas de la tabla incluyendo el numero de estado
    table = []
    for state, actions in parsing_table.items():
        row = [state] + list(actions.values())
        table.append(row)
    # Imprimir la tabla
    print(tabulate(table, headers=headers, tablefmt="grid"))
    

#Algoritmo de Parseo LR
def LRParsing(grammar,parsing_table,input_value):
    stack = Stack()
    stack.insert('I0')
    symbols = ""
    input_value.insert('$')
    
    rules = getRules(grammar)
    
    while True:
        action = parsing_table[stack.first()][input_value.first()]
        if action==None:
            print("ERROR SINTACTICO. CADENA NO ACEPTADA")
            break;
        elif action[0]=='s':
            stack.insert(action[1:])
            symbols=input_value.remove_first()
        elif action[0]=='r':
            prod = rules[int(action[1])].split(' -> ')
            head = prod[0]
            body = prod[1].split(' ')
            
            for i in range(len(body)):
                stack.remove_first()
            
            stack.insert(parsing_table[stack.first()][head])
            symbols=head
        elif action=="acc":
            print("-- CADENA ACEPTADA --")
            break;


# Definir la interfaz
class QueueInterface(ABC):
    @abstractmethod
    def empty(self):
        pass
    
    @abstractmethod
    def first(self):
        pass
    
    @abstractmethod
    def remove_first(self):
        pass
    
    @abstractmethod
    def insert(self,item):
        pass

# Clase Padre que implementa la interfaz
class Queue(QueueInterface):
    def __init__(self):
       self.content = []         

    def empty(self):
        return len(self.content)==0
        
    def first(self):
        if not self.empty():
            return self.content[0]
        
    def remove_first(self):
        item = self.first()
        if item:
            self.content.pop(0)
            return item
        
    def insert(self,item):
        pass
    
#Clase Hija FIFO
class Fifo(Queue):
    def insert(self,item):
        self.content.append(item)
        return self.content
    
#Clase Hija LIFO
class Stack(Queue):
    def insert(self,item):
        self.content.insert(0,item)
        return self.content