# -*- coding: utf-8 -*-
from graphviz import Digraph
import regexLib
import astLib
import sys



def eliminar_comentarios_yalex(contenido):
    """
    Elimina los comentarios del contenido de un archivo YALex, manejando correctamente 
    los comentarios anidados y verificando que todos los comentarios se cierren.
    
    Args:
    - contenido (str): Contenido del archivo YALex como una cadena de texto.
    
    Returns:
    - str: Contenido del archivo con los comentarios eliminados.
    """
    inicio_comentario = "(*"
    fin_comentario = "*)"
    pila = []
    i = 0
    while i < len(contenido):
        if contenido.startswith(inicio_comentario, i):
            pila.append(i)
            i += len(inicio_comentario)
        elif contenido.startswith(fin_comentario, i):
            if not pila:
                print("Error de sintaxis. Comentario cerrado sin abrir.")
                sys.exit(1)
            inicio = pila.pop()
            fin = i + len(fin_comentario)
            contenido = contenido[:inicio] + contenido[fin:]
            i = inicio  # Reiniciar la busqueda desde el ultimo inicio de comentario encontrado
        else:
            i += 1

    if pila:
        print("Error de sintaxis. Comentario no cerrado correctamente.")
        sys.exit(1)

    return contenido


def normalizar_y_separar(contenido):
    """
    Normaliza el contenido para manejar irregularidades en los saltos de linea y espacios,
    y luego separa las definiciones y todas las reglas del contenido de un archivo de especificacion,
    incluyendo aquellas sin una accion de return.
    
    Args:
    - contenido (str): Contenido del archivo de especificacion sin comentarios.
    
    Returns:
    - Tuple[List[str], List[str]]: Una tupla conteniendo dos listas, una con las definiciones y otra con todas las reglas.
    """
    # Normalizar saltos de linea y espacios extra
    contenido_normalizado = contenido.replace('\n', ' ')
    while '  ' in contenido_normalizado:
        contenido_normalizado = contenido_normalizado.replace('  ', ' ')
    
    # Separar el contenido en definiciones y reglas
    inicio_reglas = contenido_normalizado.find("rule tokens =")
    definiciones_texto = contenido_normalizado[:inicio_reglas].strip()
    reglas_texto = contenido_normalizado[inicio_reglas:].strip()

    # Extraer las definiciones
    definiciones = [linea.strip() for linea in definiciones_texto.split('let ') if linea]

    # Preparar las definiciones añadiendo "let " al inicio de cada una
    definiciones = ['let ' + defi for defi in definiciones if defi]

    # Modificacion para incluir todas las reglas desde "rule tokens ="
    reglas_texto = reglas_texto.replace('rule tokens =', '').strip()
    reglas = [linea.strip() for linea in reglas_texto.split('|') if linea]

    return definiciones, reglas


def definiciones_a_diccionario(definiciones):
    """
    Convierte una lista de definiciones en un diccionario, asegurandose de que cada definicion
    cumpla con el formato esperado de "let id = valor". Falla si encuentra definiciones incompletas
    o mal formadas.
    
    Args:
    - definiciones (List[str]): Lista de definiciones extraidas del archivo de especificacion.
    
    Returns:
    - Dict[str, str]: Diccionario con las definiciones mapeadas a sus expresiones.
    """
    diccionario_definiciones = {}
    for definicion in definiciones:
        # Verificar formato minimo requerido "let id = valor"
        if definicion.count("=") != 1 or not definicion.strip().startswith("let"):
            print(f"Error de sintaxis. Definicion mal formada o incompleta: {definicion}")
            sys.exit(1)

        partes = definicion.split("=")
        identificador_partes = partes[0].strip().split()

        # Verificar que despues de "let" hay exactamente un identificador antes del "="
        if len(identificador_partes) != 2:
            print(f"Error: Formato incorrecto, se esperaba 'let id = valor': {definicion}")
            sys.exit(1)

        clave = identificador_partes[1].strip()  # Extraer identificador
        valor = partes[1].strip()  # Extraer valor

        # Verificar que el valor no este vacio
        if not valor:
            print(f"Error: Falta valor para el identificador '{clave}' en la definición: {definicion}")
            sys.exit(1)

        diccionario_definiciones[clave] = valor

    return diccionario_definiciones


def explotar_valores(diccionario):
    def explotar_valor(valor, diccionario):
        # Utilizamos una variable modificada para saber si se realizo un cambio en la iteracion
        # para evitar la mutacion de la cadena mientras la iteramos.
        valor_modificado = valor
        se_realizo_cambio = True

        while se_realizo_cambio:
            se_realizo_cambio = False
            for clave in sorted(diccionario.keys(), key=len, reverse=True):
                inicio = 0  # Posicion inicial para buscar la clave
                while clave in valor_modificado[inicio:]:
                    indice = valor_modificado[inicio:].find(clave) + inicio
                    # Verificar si la clave esta dentro de comillas
                    if indice > 0 and (valor_modificado[indice-1] in ("'", '"')):
                        inicio = indice + len(clave)
                        continue
                    # Verificar si la clave esta seguida de comillas
                    if indice + len(clave) < len(valor_modificado) and (valor_modificado[indice + len(clave)] in ("'", '"')):
                        inicio = indice + len(clave)
                        continue
                    
                    valor_basico = diccionario[clave]
                    if valor_basico != valor_modificado:
                        # Reemplazar la clave por su valor basico, anadiendo parentesis si necesario
                        valor_modificado = valor_modificado[:indice] + valor_basico + valor_modificado[indice + len(clave):]
                        se_realizo_cambio = True
                        # Reiniciamos la busqueda desde el principio del valor modificado para manejar anidaciones
                        break  # Salimos del bucle para reiniciar con el valor modificado

                if se_realizo_cambio:
                    break  # Si se realizo un cambio, reiniciar la revision desde el principio

        return valor_modificado

    diccionario_explotado = {}
    for clave, valor in diccionario.items():
        diccionario_explotado[clave] = explotar_valor(valor, diccionario)

    return diccionario_explotado


def expandir_rangos_numericos(diccionario):
    """
    Expande los rangos numericos en las definiciones del diccionario a una forma explicita,
    sin utilizar expresiones regulares.
    
    Args:
    - diccionario (Dict[str, str]): Diccionario con valores que pueden contener rangos numericos.
    
    Returns:
    - Dict[str, str]: Diccionario con los rangos numericos expandidos.
    """
    def expandir_rango(valor):
        # Buscar y expandir todos los rangos numericos
        resultado = ""
        i = 0
        while i < len(valor):
            if valor[i] == "[":
                inicio_rango = i
                fin_rango = valor.find("]", inicio_rango)
                if fin_rango != -1:
                    rango_partes = valor[inicio_rango+1:fin_rango].replace("'", "").replace(" ", "").split("-")
                    if len(rango_partes) == 2 and rango_partes[0].isdigit() and rango_partes[1].isdigit():
                        rango_expandido = "|".join(str(x) for x in range(int(rango_partes[0]), int(rango_partes[1]) + 1))
                        resultado += rango_expandido
                        i = fin_rango + 1
                        continue
            resultado += valor[i]
            i += 1
        return resultado
    
    diccionario_expandido = {clave: expandir_rango(valor) for clave, valor in diccionario.items()}
    return diccionario_expandido


def expandir_multiples_rangos_alfabeticos(diccionario):
    """
    Expande multiples rangos alfabeticos en las definiciones del diccionario a una forma explicita,
    incluyendo aquellos con más de un rango en una sola definicion.
    
    Args:
    - diccionario (Dict[str, str]): Diccionario con valores que pueden contener multiples rangos alfabeticos.
    
    Returns:
    - Dict[str, str]: Diccionario con los rangos alfabeticos expandidos y envueltos en parentesis.
    """
    def expandir_rango(valor):
        resultado = ""
        i = 0
        while i < len(valor):
            if valor[i] == "[":
                inicio_rango = i
                fin_rango = valor.find("]", inicio_rango)
                segmento = valor[inicio_rango+1:fin_rango].replace(" ", "")
                segmentos = segmento.split("''")
                rango_expandido = ""
                for seg in segmentos:
                    if '-' in seg:
                        inicio, fin = seg.replace("'", "").split("-")
                        if inicio.isalpha() and fin.isalpha():
                            rango_expandido += "|".join(chr(x) for x in range(ord(inicio), ord(fin) + 1)) + "|"
                if rango_expandido:
                    # Anade parentesis alrededor del rango expandido
                    resultado += "(" + rango_expandido.rstrip('|') + ")"
                    i = fin_rango + 1
                    continue
            resultado += valor[i]
            i += 1
        
        return resultado
    
    diccionario_expandido = {clave: expandir_rango(valor) for clave, valor in diccionario.items()}
    return diccionario_expandido



def expandir_clases_caracteres(diccionario):
    """
    Expande clases de caracteres especiales en las definiciones del diccionario a una forma explicita,
    dividiendolos con | y sin agregar comillas adicionales.
    
    Args:
    - diccionario (Dict[str, str]): Diccionario con valores que pueden contener clases de caracteres especiales.
    
    Returns:
    - Dict[str, str]: Diccionario con las clases de caracteres expandidas.
    """
    def expandir_clase(valor):
        resultado = ""
        i = 0
        while i < len(valor):
            if valor[i] == "[":
                inicio_clase = i
                fin_clase = valor.find("]", inicio_clase)
                clase_partes = valor[inicio_clase+1:fin_clase].split("''")
                clase_expandida = "(" + "|".join(clase_partes).replace("'", "").replace("\\s", " ").replace("\\t", "\t").replace("\\n", "\n") + ")"
                resultado += clase_expandida
                i = fin_clase + 1
            else:
                resultado += valor[i]
                i += 1
        return resultado
    
    diccionario_expandido = {clave: expandir_clase(valor) for clave, valor in diccionario.items()}
    return diccionario_expandido


def convertir_reglas_a_diccionario(reglas):
    diccionario_de_reglas = {}
    for regla in reglas:
        # Buscar si la regla contiene un bloque de retorno
        if '{ return' in regla:
            # Separa la regla por " { return " para obtener clave y valor
            clave, resto = regla.split(' { return ')
            valor = resto.rstrip(' }')  # Elimina el " }" final
        else:
            clave = regla
            valor = None  # Asigna None si no hay "return"
        # No se elimina las comillas de los extremos de la clave
        diccionario_de_reglas[clave] = valor
    return diccionario_de_reglas


with open('slr-4.yal', 'r') as archivo:
    contenido_archivo = archivo.read()

contenido_sin_comentarios = eliminar_comentarios_yalex(contenido_archivo)
definiciones, reglas = normalizar_y_separar(contenido_sin_comentarios)
diccionario_definiciones = definiciones_a_diccionario(definiciones)

diccionario_con_multiples_rangos_alfabeticos_expandidos = expandir_multiples_rangos_alfabeticos(diccionario_definiciones)
#diccionario_con_rangos_expandidos_sin_re = expandir_rangos_numericos(diccionario_con_multiples_rangos_alfabeticos_expandidos)
# diccionario_con_clases_caracteres_expandidos = expandir_clases_caracteres(diccionario_con_rangos_expandidos_sin_re)

diccionario_explotado = explotar_valores(diccionario_con_multiples_rangos_alfabeticos_expandidos)



print("-------------------------------------------------------------------------------")

for clave, valor in diccionario_explotado.items():
    print(f"{clave}: {valor}")

print("-------------------------------------------------------------------------------")




diccionario_de_reglas = convertir_reglas_a_diccionario(reglas)
claves = list(diccionario_de_reglas.keys())
valores_para_unir = []
for clave in diccionario_de_reglas.keys():
    if clave in diccionario_explotado:
        valor = diccionario_explotado[clave]
    else:
        valor = clave
    # Verifica si el valor contiene '.', si es así, encierra '.' con comillas simples
    valor_modificado = valor.replace('.', "'.'")
    valores_para_unir.append(valor_modificado)

 


arbol_no = 0
for item in valores_para_unir:
    arbol_no=arbol_no+1
    postfix = regexLib.shunting_yard(item)
    ast_root = astLib.create_ast(postfix)
    ast_graph = astLib.plot_tree(ast_root)
    nombre = "arbol" + str(arbol_no)
    ast_graph.view(filename=nombre, cleanup=True)
    

resultado = '|'.join(valores_para_unir)
print(resultado)
postfixCompleto = regexLib.shunting_yard(resultado)            
ast_root_complete = astLib.create_ast(postfixCompleto)
ast_graph_complete = astLib.plot_tree(ast_root_complete)
nombre = "arbol completo"
ast_graph_complete.view(filename=nombre, cleanup=True)

    














































