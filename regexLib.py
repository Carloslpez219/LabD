# -*- coding: utf-8 -*-
import string

def tokenizeRegex(regex):
    tokens = []
    reserved = ['|','*','.','(',')','+','?']
    i = 0
    while i < len(regex):
        char = regex[i]

        # Caracter de escape
        if char == '\\':
            if i + 1 < len(regex):
                if regex[i+1]=="s":
                    tokens.append(' ')
                elif regex[i+1]=="t":
                    tokens.append('\t')
                elif regex[i+1]=="n":
                    tokens.append('\n')
                else:
                    tokens.append(regex[i:i+2])
                i += 2
            else:
                tokens.append(char)
                i += 1
                
        elif char=="'":
            if i + 2 < len(regex) and regex[i+2]=="'":
                res = regex[i+1] if regex[i+1] not in reserved else '\\'+regex[i+1]
                tokens.append(res)
                i += 3 if i+3<len(regex) else len(regex)
            else:
                tokens.append(char)
                i += 1
                
        elif char == '"':
            string = char
            i += 1
            
            first_i=i
            first_char = char
            
            while i < len(regex) and regex[i] != '"':
                if regex[i] == '\\':
                    if i + 1 < len(regex):
                        #Escape de caracteres importantes en las clases
                        if regex[i+1]=='s':
                            string+=' '
                        elif regex[i+1]=='"':
                            string+='"'
                        else:
                            string+='\\'+regex[i+1]
                        
                        i += 1
                    else:
                        string += regex[i]
                else:
                    string += regex[i]
                    
                i += 1
            if i < len(regex):  # Asegurarse de incluir el '"' si no se ha llegado al final de la regex
                string += regex[i]
                string = string[1:-1]
                j = 0
                while j<len(string):
                    if string[j]=='\\':
                        tokens.append('\\'+string[j+1])
                        j+=1
                    else:
                        tokens.append(string[j])
                    j += 1
                i+=1
            else:
                #Si no se encuentra la estructura de un string, se agrega unicamente el caracter '"'
                tokens.append(first_char)
                i=first_i
                
        # Inicio de clase de caracteres
        elif char == '[':
            clase_char = char
            i += 1
            
            first_i=i
            first_char = char
            
            while i < len(regex) and regex[i] != ']':
                if regex[i] == '\\':
                    if i + 1 < len(regex):
                        #Escape de caracteres importantes en las clases
                        if regex[i+1]=='s':
                            clase_char+=' '
                        elif regex[i+1]=='t':
                            clase_char+='\t'
                        elif regex[i+1]=='n':
                            clase_char+='\n'
                        elif regex[i+1]=='[':
                            clase_char+='['
                        elif regex[i+1]==']':
                            clase_char+=']'
                        else:
                            clase_char+='\\'+regex[i+1]
                        
                        i += 1
                    else:
                        clase_char += regex[i]
                else:
                    clase_char += regex[i]
                    
                i += 1
            if i < len(regex):  # Asegurarse de incluir el ']' si no se ha llegado al final de la regex
                clase_char += regex[i]
                tokens.append(clase_char)
                i += 1
            else:
                #Si no se encuentra la estructura de una clase, se agrega unicamente el caracter '['
                tokens.append(first_char)
                i=first_i
                

        # Operadores
        elif char in {'*', '+', '?', '|'}:
            tokens.append(char)
            i += 1

        # Grupos
        elif char in {'(', ')'}:
            tokens.append(char)
            i += 1

        # Caracteres literales y otros
        else:
            tokens.append(char)
            i += 1

    return tokens

def regexAlphabet(postfix):
    alphabet = set()
    reserved = ['|','*','.','ε']
    
    i=0
    while i<len(postfix):
        char = postfix[i]
        if char[0] == '\\':
            if len(char)>1:
                alphabet.add(char[1])
            else:
                alphabet.add(char[0])
        elif char not in reserved:
            alphabet.add(char)
            
        i+=1
            
    return alphabet

def validateRegexSyntax(regex):
    if not balancedRegex(regex):
        return (False,"expresion no balanceada.")
    
    if not validOperators(regex):
        return (False,"expresion con uso invalido de operadores.")
    
    if not validChars(regex):
        return (False,"expresion con uso invalido de caracteres.")
    
    return (True,"")

def balancedRegex(regex):
    stack = []
    simbolos = {'(': ')'}

    for caracter in regex:
        if caracter in simbolos.keys():
            stack.append(caracter)
        elif caracter in simbolos.values():
            if not stack or simbolos[stack.pop()] != caracter:
                return False
    
    if len(stack) == 0:
        return True
    else:
        return False
    
def validOperators(regex):
    allOperators = {'|','?','+','*'}
    if regex[0] in allOperators:
        return False
    
    if regex[-1]=='|':
        return False
    
    for i in range(0,len(regex)-1):
        if regex[i]=='|' and regex[i+1] in allOperators:
            return False
    
    return True

def validChars(regex):
    invalidChars = {'.'}
    
    for c in regex:
        if c in invalidChars:
            return False
        
    return True

def getPrecedence(c):
    if c=='(':
        return 1
    elif c=='|':
        return 2
    elif c=='.':
        return 3
    elif c=='*':
        return 4
    
def formatRegEx(tokens):
    allOperators = ['|', '?', '+', '*']
    binaryOperators = ['|']
    res = []
    
    # Función auxiliar para manejar los casos de '+' y '?'
    def handle_operator(index, operator, empty_symbol='ε'):
        nonlocal tokens
        if tokens[index - 1] != ')':
            if operator == '+':
                tokens[index - 1:index + 1] = ['(',tokens[index - 1], tokens[index - 1], '*',')']
            elif operator == '?':
                tokens[index - 1:index + 1] = ['(', tokens[index - 1], '|', empty_symbol, ')']
        else:
            j = index - 2
            count = 0
            while j >= 0 and (tokens[j] != '(' or count != 0):
                if tokens[j] == ')':
                    count += 1
                elif tokens[j] == '(':
                    count -= 1
                j -= 1
            if tokens[j] == '(' and count == 0:
                if operator == '+':
                    tokens[j:index + 1] = ['(']+tokens[j:index] + tokens[j:index] + ['*'] +[')']
                elif operator == '?':
                    tokens[j:index + 1] = ['('] + tokens[j:index] + ['|', empty_symbol, ')']
    
    #Funcion para reconstruir todas las clases en un solo formato ["abc..."]
    def expand_character_class(char_class):
       characters = []
       i=0
       while i < len(char_class):
           c = char_class[i]
           
           if c=="'":
               if char_class[i+1]=="\\":
                   characters.append(char_class[i+2])
                   i+=1
               else:
                   characters.append(char_class[i+1])
               i+=2
           elif c=="-":
               start = characters.pop()
               end = char_class[i+2]
               
               for c in range(ord(start), ord(end) + 1):
                   characters.append(chr(c))
               i+=3
           elif c=='"':
               j=i+1
               while j<len(char_class):
                   if char_class[j]!='"':
                       characters.append(char_class[j])
                   else:
                       break
                   j+=1
               i=j
           i+=1
       
       expanded = ''.join(item for item in characters)
       return expand_string('"'+expanded+'"')
               

    #Funcion para reconstruir la clase en formato ["abc.."] en (a|b|c...)    
    def expand_string(string):
        reserved = ['|','*','.','(',')','+','?']
        expanded = []
        
        char_class = string[1:-1]
        for c in char_class:
            if c in reserved:
                expanded.append('\\'+c)
            else:
                expanded.append(c)
            expanded.append('|')
        
        expanded.pop()
        return ['('] + [char for char in expanded] + [')']

    # Manejar los casos de '+'
    i = 0
    while i < len(tokens):
        if tokens[i] == '+':
            handle_operator(i, '+')
            continue  # Evita incrementar i para revisar el nuevo token en la misma posición
        i += 1

    # Manejar los casos de '?'
    i = 0
    while i < len(tokens):
        if tokens[i] == '?':
            handle_operator(i, '?')
            continue
        i += 1
        
    # Agregar operadores de concatenación y manejar clases de caracteres
    i = 0
    while i < len(tokens):
        token = tokens[i]
        
        # Verifica si el token actual es una clase de caracteres
        if token.startswith('[') and token.endswith(']'):
            expanded_tokens = expand_character_class(token)
            res.extend(expanded_tokens)
            
        else:
            res.append(token)
            
        # Agregar operadores de concatenación según sea necesario
        if i + 1 < len(tokens):
            next_token = tokens[i + 1]
            if token not in binaryOperators + ['('] and next_token not in allOperators + [')', '.']:
                res.append('.')
        i += 1
        
    
    return res

def shunting_yard(regex):

    postfix = []
    operators = ['|','*','.']
    stack = []
    tokens = tokenizeRegex(regex)
    formattedRegEx = formatRegEx(tokens)
    
    i=0
    while i<len(formattedRegEx):
        c = formattedRegEx[i]
        
        if c=='(':
            stack.append(c)
        elif c==')':
            while stack[-1]!='(':
                postfix.append(stack.pop())
            
            stack.pop()
        elif c in operators:
            while len(stack)>0:
                peekedChar = stack[-1]
                peekedCharPrecedence = getPrecedence(peekedChar)
                currentCharPrecedence = getPrecedence(c)
                
                if peekedCharPrecedence>=currentCharPrecedence:
                    postfix.append(stack.pop())
                else:
                    break
            
            stack.append(c)
        else:
            postfix.append(c)
        
        i+=1
    
    while len(stack)>0:
        postfix+=stack.pop()
    
    return postfix