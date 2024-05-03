from graphviz import Digraph


#Plot de Automata Finito
def plot_af(state, graph=None, visited=None):
    if visited is None:
        visited = set()

    if state in visited:
        return graph

    if graph is None:
        graph = Digraph(engine='dot', graph_attr={'rankdir': 'LR'})
    
    if state.is_accept:
        graph.node(name=str(id(state)), label=state.name, shape='doublecircle', color="green")
        if len(visited)==0:
             graph.node(name="start", label="start", shape='point')
             graph.edge("start", str(id(state)), label="inicio")
    elif len(visited)==0:
        graph.node(name="start", label="start", shape='point')
        graph.node(name=str(id(state)), label=state.name, shape='circle', color="blue")
        graph.edge("start", str(id(state)), label="inicio")
    else:
        graph.node(name=str(id(state)), label=state.name, shape='circle')
        
    visited.add(state)

    for symbol, next_states in state.transitions.items():
        for next_state in next_states:
            graph.edge(str(id(state)), str(id(next_state)), label=symbol)
            plot_af(next_state, graph, visited)

    return graph

#Cerradura epsilon para un estado
def e_closure_state(state, visited=None):
    if visited is None:
        visited = set()

    if state in visited:
        return
        
    visited.add(state)

    for symbol, next_states in state.transitions.items():
        for next_state in next_states:
            if symbol == 'ε':
                e_closure_state(next_state,visited)

    return visited

#Cerradura epsilon para un conjunto de estados
def e_closure(S):
    res = set()
    for state in S:
        res = res.union(e_closure_state(state))
        
    return res

#Estados alcanzables desde un estado y simbolo dado
def move(S,c):
    res = set()
    
    for state in S:
        for symbol,next_states in state.transitions.items():
            for next_state in next_states:
                if symbol == c:
                    res.add(next_state)
    
    return res