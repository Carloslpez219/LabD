
from graphviz import Digraph

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

# Generacion de automata
def generate_LRAutomata(grammar):
    automata  = LRAutomata()
    grammar_symbols = set(grammar.keys())

    for value in grammar.values():
        for prod in value:
            grammar_symbols = grammar_symbols.union(set(prod.split(' ')))
        
    
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