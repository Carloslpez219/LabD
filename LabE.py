# -*- coding: utf-8 -*-﻿
import LR0
import pickle



with open('grammar.pkl', 'rb') as archivo_entrada:
        grammar = pickle.load(archivo_entrada)
        
with open('compare_tokens.pkl', 'rb') as archivo_entrada:
        compare_tokens = pickle.load(archivo_entrada)
        
with open('ignore_tokens.pkl', 'rb') as archivo_entrada:
        ignore_tokens = pickle.load(archivo_entrada)
        
with open('input_tokens.pkl', 'rb') as archivo_entrada:
        input_tokens = pickle.load(archivo_entrada)


print("Grammar: " + str(grammar))
print("--------------------------------------------------------------------------------")
print("compare_tokens: " + str(compare_tokens))
print("--------------------------------------------------------------------------------")
print("ignore_tokens: " + str(ignore_tokens))
print("--------------------------------------------------------------------------------")
print("input_tokens: " + str(input_tokens))


cleaned_tokens = [token for token in input_tokens if token not in ignore_tokens]

print(cleaned_tokens)

grammar = LR0.augment_grammar(grammar)

automata = LR0.generate_LR0Automata(grammar)
automata_graph = LR0.plot_af(automata.start)
nombre_archivo_pdf = 'Automata LR'
automata_graph.view(filename=nombre_archivo_pdf,cleanup=True)


grammar = LR0.augment_grammar(grammar)
input_value = LR0.Fifo()

for item in cleaned_tokens:
    input_value.insert(item)

parsing_table = LR0.generate_SLRTable(grammar)
if parsing_table:
    LR0.print_parsing_table(parsing_table)
    LR0.LRParsing(grammar,parsing_table,input_value)


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