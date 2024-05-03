# -*- coding: utf-8 -*-
from email import header
from graphviz import Digraph
import regexLib
import astLib
import sys
import AfdLib
import AfLib
import pickle
import traceback


def eliminar_comentarios_yalex(contenido):
    """
    Elimina los comentarios del contenido de un archivo YALex, manejando correctamente 
    los comentarios anidados. Ignora los comentarios de cierre sin una apertura correspondiente.

    Args:
    - contenido (str): Contenido del archivo YALex como una cadena de texto.
    
    Returns:
    - str: Contenido del archivo con los comentarios eliminados, ignorando cierres no emparejados.
    """
    inicio_comentario = "(*"
    fin_comentario = "*)"
    pila = []
    i = 0
    nuevo_contenido = []

    while i < len(contenido):
        if contenido.startswith(inicio_comentario, i):
            pila.append(i)
            i += len(inicio_comentario)
        elif contenido.startswith(fin_comentario, i):
            if pila:
                inicio = pila.pop()
                nuevo_contenido.append(contenido[:inicio])
                contenido = contenido[i + len(fin_comentario):]
                i = 0
            else:
                i += len(fin_comentario)
        else:
            i += 1

    if not pila:
        nuevo_contenido.append(contenido)

    return ''.join(nuevo_contenido)

def extraer_header_y_contenido(contenido):
    """
    Extrae el encabezado (definido como texto dentro de llaves antes de la primera
    aparición de 'let') y elimina ese encabezado del contenido original.

    Args:
    - contenido (str): Contenido del archivo YALex como una cadena de texto.

    Returns:
    - tuple: (contenido_sin_header, header). 'contenido_sin_header' es el contenido
      sin el encabezado. 'header' es el texto extraído entre las llaves.
    """
    # Buscar el inicio de las definiciones.
    inicio_definiciones = contenido.find("let")
    
    if inicio_definiciones == -1:
        # No hay definiciones, devolver el contenido original y un header vacío.
        return contenido, ""
    
    # Buscar el encabezado antes de las definiciones.
    inicio_header = contenido.rfind("{", 0, inicio_definiciones)
    fin_header = contenido.find("}", inicio_header, inicio_definiciones)
    
    if inicio_header == -1 or fin_header == -1:
        # No se encontró un encabezado válido, devolver el contenido original y un header vacío.
        return contenido, ""
    
    # Extraer el encabezado y el contenido sin el encabezado.
    header = contenido[inicio_header + 1:fin_header]
    contenido_sin_header = contenido[:inicio_header] + contenido[fin_header + 1:]
    
    return contenido_sin_header, header


def extraer_footer_y_contenido(contenido):
    """
    Extrae el footer (definido como texto dentro de las últimas llaves) y elimina
    ese footer del contenido original.

    Args:
    - contenido (str): Contenido del archivo YALex como una cadena de texto.

    Returns:
    - tuple: (contenido_sin_footer, footer). 'contenido_sin_footer' es el contenido
      sin el footer. 'footer' es el texto extraído entre las últimas llaves.
    """
    # Buscar el último '}' que debería cerrar el footer.
    fin_footer = contenido.rfind("}")
    if fin_footer == -1:
        # No hay footer, devolver el contenido original y un footer vacío.
        return contenido, ""
    
    # Buscar hacia atrás desde el fin_footer para encontrar el inicio del footer.
    inicio_footer = contenido.rfind("{", 0, fin_footer)
    if inicio_footer == -1:
        # No se encontró un inicio de footer válido, devolver el contenido original y un footer vacío.
        return contenido, ""
    
    # Extraer el footer.
    footer = contenido[inicio_footer + 1:fin_footer]
    
    # Eliminar el footer del contenido.
    contenido_sin_footer = contenido[:inicio_footer] + contenido[fin_footer + 1:]
    
    return contenido_sin_footer, footer




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
    contenido_normalizado = contenido
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
        if not definicion.strip().startswith("let"):
            print(f"Error de sintaxis. Definicion mal formada o incompleta: {definicion}")
            sys.exit(1)

        partes = definicion.split("=", 1)  # Divide en dos partes en el primer "="
        if len(partes) != 2:
            print(f"Error de sintaxis. Definicion mal formada o incompleta: {definicion}")
            sys.exit(1)

        identificador_partes = partes[0].strip().split()

        # Verificar que después de "let" hay exactamente un identificador antes del "="
        if len(identificador_partes) != 2:
            print(f"Error: Formato incorrecto, se esperaba 'let id = valor': {definicion}")
            sys.exit(1)

        clave = identificador_partes[1].strip()  # Extraer identificador
        valor = partes[1].strip()  # Extraer valor

        # Verificar que el valor no esté vacío
        if not valor:
            print(f"Error: Falta valor para el identificador '{clave}' en la definición: {definicion}")
            sys.exit(1)

        diccionario_definiciones[clave] = valor

    return diccionario_definiciones



def reglas_a_diccionario(lista_reglas):
    diccionario_reglas = {}

    for regla in lista_reglas:
        # Encontrar la posición de las llaves para separar la clave del valor.
        inicio_llave = regla.find('{')
        fin_llave = regla.rfind('}')

        # Extraer la clave y el valor basándose en las posiciones de las llaves.
        clave = regla[:inicio_llave].strip()
        valor = regla[inicio_llave + 1:fin_llave].strip()

        # Verificar y ajustar las claves que vienen entrecomilladas.
        if clave.startswith(("'", '"')) and clave.endswith(("'", '"')):
            clave = clave[1:-1]

        # Asignar "return none" si el valor está vacío.
        if not valor:
            valor = "return none"

        diccionario_reglas[clave] = "{ " + valor + " }"

    return diccionario_reglas


def explotar_valores(diccionario):
    def explotar_valor(valor, diccionario):
        cambios = True
        while cambios:
            cambios = False
            for clave in sorted(diccionario.keys(), key=len, reverse=True):
                # Almacenamos la longitud original del valor para ver si cambia después del reemplazo
                original_length = len(valor)

                # Buscamos todas las ocurrencias de la clave, asegurando que no sean parte de otra palabra
                pos = 0
                while pos < len(valor):
                    pos = valor.find(clave, pos)
                    if pos == -1:
                        break
                    # Comprobar delimitadores
                    if (pos == 0 or not valor[pos-1].isalnum()) and (pos + len(clave) == len(valor) or not valor[pos + len(clave)].isalnum()):
                        # Realizar el reemplazo
                        valor = valor[:pos] + diccionario[clave] + valor[pos + len(clave):]
                        cambios = True
                        # No avanzamos 'pos' porque el reemplazo podría contener la misma clave o nuevas claves
                    else:
                        pos += len(clave)  # Avanzar posición si no es un punto válido para reemplazar

        return valor

    # Construir el diccionario de valores explotados
    diccionario_explotado = {}
    for clave, valor in diccionario.items():
        valor_explotado = explotar_valor(valor, diccionario)
        diccionario_explotado[clave] = valor_explotado

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
        # Buscar si la regla contiene un bloque entre llaves
        if '{' in regla:
            # Separa la regla por el primer '{' para obtener la clave y el valor
            partes = regla.split('{', 1)
            clave = partes[0].strip()
            valor = partes[1].rstrip('}').strip()  # Elimina el "}" final y espacios adicionales
        else:
            clave = regla.strip()
            valor = None  # Asigna None si no hay un bloque entre llaves
        # Asigna la clave y el valor al diccionario
        diccionario_de_reglas[clave] = valor
    return diccionario_de_reglas




def generate_scan(path):
    try:    
        with open(path, 'r', encoding='utf-8') as archivo:
            contenido_archivo = archivo.read()

        contenido_sin_comentarios = eliminar_comentarios_yalex(contenido_archivo)
        contenido_sin_comentarios, header = extraer_header_y_contenido(contenido_sin_comentarios)
        contenido_sin_comentarios, footer = extraer_footer_y_contenido(contenido_sin_comentarios)
        definiciones, reglas = normalizar_y_separar(contenido_sin_comentarios)
        diccionario_definiciones = definiciones_a_diccionario(definiciones)
        diccionario_reglas = reglas_a_diccionario(reglas)
        diccionario_explotado = explotar_valores(diccionario_definiciones)
        
        print("-----------------------------------------------------")
        for clave, valor in diccionario_explotado.items():
            print(f"{clave}: {valor}")
        print("-----------------------------------------------------")
        

        #LEER YAL
        
        with open('slr-1.yal', 'r', encoding='utf-8') as archivo:
            tokens = archivo.read()
        
        contenido_sin_comentarios_tokens = eliminar_comentarios_yalex(tokens)
        definiciones_tokens, reglas_tokens = normalizar_y_separar(contenido_sin_comentarios_tokens)

        tokens = list(reglas_tokens)
        with open('tokens.pkl', 'wb') as archivo_tokens:
            pickle.dump(tokens, archivo_tokens)


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

        # arbol_no = 0
        # for item in valores_para_unir:
        #     arbol_no=arbol_no+1
        #     postfix = regexLib.shunting_yard(item)
        #     ast_root = astLib.create_ast(postfix)
        #     ast_graph = astLib.plot_tree(ast_root)
        #     nombre = "arbol" + str(arbol_no)
        #     ast_graph.view(filename=nombre, cleanup=True)

        valores_para_unir = [item + '■' for item in valores_para_unir]
        resultado = '|'.join(valores_para_unir)
        resultado = '('+resultado+')'

        for clave, valor in diccionario_reglas.items():
            print(f"{clave}: {valor}")

        # postfixCompleto = regexLib.shunting_yard(resultado)            
        # ast_root_complete = astLib.create_ast(postfixCompleto)
        # ast_graph_complete = astLib.plot_tree(ast_root_complete)
        # nombre = "arbol completo"
        # ast_graph_complete.view(filename=nombre, cleanup=True)

        postfix = regexLib.shunting_yard(resultado)
        ast_root = astLib.create_ast(postfix)
        afd = AfdLib.ast_to_afdd(regexLib.regexAlphabet(postfix),ast_root)
        uniquePos = sorted(list(set(state.acceptPos for state in afd.accept)))
        for state in afd.accept:
                state.action = list(diccionario_reglas.values())[uniquePos.index(state.acceptPos)]
        # afd_graph = AfLib.plot_af(afd.start)
        # afd_graph.view(filename='AFD',cleanup=True)

        with open('afd.pkl', 'wb') as archivo_salida:
            pickle.dump(afd, archivo_salida)
            
        with open('header.pkl', 'wb') as archivo_salida_header:
            pickle.dump(header, archivo_salida_header)
            
        with open('footer.pkl', 'wb') as archivo_salida_footer:
            pickle.dump(footer, archivo_salida_footer)
            
        grammar = dict()

        with open('grammar.pkl', 'wb') as archivo_grammar:
            pickle.dump(grammar, archivo_grammar)
            
        compare_tokens = []

        with open('compare_tokens.pkl', 'wb') as archivo_compare_tokens:
            pickle.dump(compare_tokens, archivo_compare_tokens)
            
        return True
    except Exception as e:
        # Imprime el mensaje de error
        print("Ha ocurrido un error:", str(e))
        # Obtiene la información completa del traceback
        tb = traceback.format_exc()
        print("Detalle del error:", tb)
        # Obtiene solo el número de línea
        _, _, tb_info = sys.exc_info()
        # Extrae la traza de la pila más reciente
        filename, line, func, text = traceback.extract_tb(tb_info)[-1]
        print(f"El error ocurrió en el archivo '{filename}', línea {line}, en {func}. Texto: {text}")
        return False












































