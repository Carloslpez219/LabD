# -*- coding: utf-8 -*-﻿
import LR0
import pickle



with open('grammar.pkl', 'rb') as archivo_entrada:
        grammar = pickle.load(archivo_entrada)

print(grammar)

grammar = LR0.augment_grammar(grammar)

automata = LR0.generate_LRAutomata(grammar)
automata_graph = LR0.plot_af(automata.start)
nombre_archivo_pdf = 'Automata LR'
automata_graph.view(filename=nombre_archivo_pdf,cleanup=True)


# with open('compare_tokens.pkl', 'rb') as archivo_entrada_compare_tokens:
#     compare_tokens = pickle.load(archivo_entrada_compare_tokens)

# with open('tokens.pkl', 'rb') as archivo_tokens:
#     tokens = pickle.load(archivo_tokens)

# set_compare_tokens = set(compare_tokens)
# set_tokens = set(tokens)

# print(set_compare_tokens)
# print("------------")
# print(set_tokens)

# if set_compare_tokens == set_tokens:
#     with open('grammar.pkl', 'rb') as archivo_entrada:
#         grammar = pickle.load(archivo_entrada)

#     grammar = LR0.augment_grammar(grammar)

#     automata = LR0.generate_LRAutomata(grammar)
#     automata_graph = LR0.plot_af(automata.start)
#     nombre_archivo_pdf = 'Automata LR'
#     automata_graph.view(filename=nombre_archivo_pdf,cleanup=True)
# else:
#     print("Los TOKENS del yalp no coinciden los del yal")