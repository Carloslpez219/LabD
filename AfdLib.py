from astLib import Node
import AfLib
import regexLib
import astLib
import AfdLib

#Clase de estado de AFD
class AFDState:
    def __init__(self,afd,subset=set()):
        self.name = str(afd.state_counter)

        #Modificacion de state_counter y states de la instancia de AFD dada
        afd.state_counter = chr(ord(afd.state_counter) + 1)
        afd.states.add(self)

        self.subset = subset

        self.transitions = {}
        self.is_accept = False
        
        #Implementaciones para Lexer
        self.acceptPos = 0
        self.action = ""

#Clase AFD
class AFD:
    def __init__(self):
        self.start = None
        self.accept = set()
        self.states = set()
        self.simulationStates = set()
        self.state_counter = 'A'
    
    #Funcion utilizada para manejar los estados de una simulacion caracter por caracter
    def step_simulation(self,c,lookAhead):
        #Si los estados de simulacion son vacios, se reinicia con el estado inicial
        if len(self.simulationStates)==0:
            self.simulationStates.add(self.start)

        self.simulationStates = AfLib.move(self.simulationStates,c)
            
        return self.simulationStates
        

#Algoritmo AST a AFD Directo        
def ast_to_afdd(alphabet,ast_root):
    states = []
    
    afd = AFD()
    states.append(AFDState(afd,subset=ast_root.firstPos))
    afd.start = states[0]
    
    for elemento in afd.start.subset:
        if elemento in Node.posTable['#']:
            afd.accept.add(states[0])
            states[0].is_accept = True
            #Persistencia del Pos de #
            states[0].acceptPos = elemento
            break

    # if any(elemento in Node.posTable['#'] for elemento in afd.start.subset):
    #     afd.accept.add(states[0])
    #     states[0].is_accept = True
    
    contador=0
    nuevosEstados=0
    firstIteration = False
    
    while contador!=nuevosEstados or not firstIteration:
        
        firstIteration=True
        
        if nuevosEstados!=0:
            contador+=1
        
        for symbol in alphabet:

            cambio=True
            subset = set()

            for pos in states[contador].subset:
                if pos in Node.posTable[symbol]:
                    subset=subset.union(Node.followPosTable[pos])
            
            for state in states:
                if state.subset==subset:
                    states[contador].transitions[symbol] = [state]
                    cambio=False
                    break
            
            if cambio and len(subset)>0:
                newState = AFDState(afd,subset)
                
                for elemento in subset:
                    if elemento in Node.posTable['#']:
                        afd.accept.add(newState)
                        newState.is_accept = True
                        #Persistencia del Pos de #
                        newState.acceptPos = elemento
                        break
                
                # if any(elemento in Node.posTable['#'] for elemento in subset):
                #     afd.accept.add(newState)
                #     newState.is_accept = True
                
                states[contador].transitions[symbol] = [newState]
                states.append(newState)
                nuevosEstados+=1
    
    return afd

#Algoritmo AFN a AFD por subconjuntos       
def afn_to_afd(alphabet,afn):
    states = []
    
    So = set()
    So.add(afn.start)
    
    afd = AFD()
    
    states.append(AFDState(afd,subset=AfLib.e_closure(So)))
    afd.start = states[0]
    
    if afn.accept in afd.start.subset:
        afd.accept.add(states[0])
        states[0].is_accept = True
        

    contador=0
    nuevosEstados=0
    firstIteration = False

    while contador!=nuevosEstados or not firstIteration:
        
        firstIteration=True

        if nuevosEstados!=0:
            contador+=1
        
        for symbol in alphabet:
            cambio=True
            subset=AfLib.e_closure(AfLib.move(states[contador].subset,symbol))
            
            for state in states:
                if state.subset==subset:
                    states[contador].transitions[symbol] = [state]
                    cambio=False
                    break
            
            if cambio and len(subset)>0:
                newState = AFDState(afd,subset)
                
                if afn.accept in subset:
                    afd.accept.add(newState)
                    newState.is_accept = True
                
                states[contador].transitions[symbol] = [newState]
                states.append(newState)
                nuevosEstados+=1
    
    return afd

#Minimizacion de AFD
def afd_to_afdmin(alphabet, afd):
    #Paso 1 algoritmo
    #Partición conjunto de todos los estados de aceptación y no aceptación (diferencia de conjuntos)
    partition = [afd.states - afd.accept, afd.accept]


    #Paso 2 algoritmo
    while True:
        # Lista vacia para nueva partición de estados.
        partition_new = []
        for G in partition:
            # Para cada grupo de estados en la partición se hacen los subgrupos.
            subgroups = {}
            
            for state in G:
                #Lista de firma de estado
                state_key = []
                
                for c in alphabet:
                    
                    # Revisamos las transiciones del estado para cada símbolo del alfabeto.
                    transition_state = state.transitions.get(c, [])
                    transition_exists = False
                    found_destination_in_s = False
                    
                    for s in partition:
                        for dest_state in transition_state:
                            # Se verifica si el estado de destino está en alguno de los grupos de la partición.
                            if dest_state in s:
                                # Si está, añadimos esa transición a la 'firma' del estado.
                                state_key.append((c, tuple(s)))
                                transition_exists = True
                                found_destination_in_s = True
                                break
                            
                        if found_destination_in_s:
                            break
                        
                    if not transition_exists:
                        # Si no hay transición para este símbolo, añadimos un None a la 'firma'.
                        state_key.append((c, None))
                        
                state_key = tuple(state_key)  # Convertimos la 'firma' a una tupla para poder usarla como clave.
                # Añadimos el estado al subgrupo correspondiente a su 'firma'.
                subgroups.setdefault(state_key, set()).add(state)
                
            partition_new.extend(subgroups.values())
            
        # Si la nueva partición es igual a la anterior, se termina.
        if partition_new == partition:
            break
        else:
            # Si no, actualizamos la partición y lo volvemos a hacer todo de nuevo
            partition = partition_new


    #Paso 3 algoritmo
    #Relacion de estados originales a sus representantes en el AFD minimizado.
    state_relations = {}
    afd_min = AFD()

    for group in partition:
        # Crea un estado que representa todo el grupo, si uno de los estados es de aceptación lo marca asi.
        # Inicializar el estado representativo sin marcarlo como de aceptación por defecto.
        representative = AFDState(afd_min)
        representative.is_accept = False

        # Ver cada estado para ver si es de aceptacion
        for state in group:
            if state.is_accept:
                representative.is_accept = True
                break  # Si se encuentra un estado de aceptación, ya no importan los demas.

        if representative.is_accept:
            #agrega el estado a los estados de aceptación
            afd_min.accept.add(representative)
        for state in group:
            #relaciona el estado original al estado representativo en el AFD minimizado
            state_relations[state] = representative
        if afd.start in group:
            #Si el estado inicial del AFD original, entonces el estado representativo se establece como el estado inicial del AFD minimizado. 
            afd_min.start = representative


    #Paso 4 algoritmo
    #Asignacion de las nuevas transiciones
    for old_state, new_state in state_relations.items():
        for c, old_transitions in old_state.transitions.items():
            new_destination_state = state_relations.get(old_transitions[0], None)
            if new_destination_state:
                new_state.transitions[c] = [new_destination_state]

    return afd_min


#Simulacion de AFD con cadena completa    
def AFD_simulation(afd,w):
    F = afd.accept
    So = set()
    So.add(afd.start)
    
    S = So
    
    if w!='ε':
        i=0
        while i<len(w):
            c = w[i]
            if c=='ε':
                i+=1
                continue
            if c=='\\' and w[i+1]=='s':
                S = AfLib.move(S,' ')
                i+=1
            else:
                S = AfLib.move(S,c)
            i+=1
    
    if S:
        s = S.pop()
    else:
        s = None
        
    if s in F:
        return "sí"
    else:
        return "no"
    
def createAFD(item):
    #Construccion de postfix
    postfix = regexLib.shunting_yard(item)
            
    #Construccion AST
    ast_root = astLib.create_ast(postfix)
            
    #Construccion AFD
    afd = ast_to_afdd(regexLib.regexAlphabet(postfix),ast_root)
            
    #Minimizacion AFD
    afdmin = afd_to_afdmin(regexLib.regexAlphabet(postfix),afd)
    
    return afdmin

def step_simulate_AFD(afd,c,lookAhead):
    res = afd.step_simulation(c, lookAhead)
    state = list(res)[0] if len(list(res))>0 else None

    if state in afd.accept:
        return (0,state.action)
    elif state in afd.states:
        return (1,"")
    else:
        return (2,"")
            
def segmentRecognize(afd,i,content):
    accept = (False,0,"")
    first = i
    # Bucle hasta que se alcance el final del contenido
    while i <= len(content):  # Asegura que haya espacio para lookAhead
        char = content[i] if i<len(content) else ""  # Caracter actual
        lookAhead = content[i + 1] if i<len(content)-1 else ""  # Caracter siguiente
        
        # Procesa el caracter aqui
        res = step_simulate_AFD(afd, char, lookAhead)
        if res[0] == 0:
            last = i+1
            accept = (True,last,content[first:last],res[1]) #Estado de aceptacion, ultima posicion de lookAhead, contenido aceptado, accion
        
        elif res[0] == 2:
            if accept[0]:
                return accept
            else:
                return (False,i,"","")

        i += 1  # Incrementa la posicion para el proximo caracter
        
def genericFunction(content):
    # Define un espacio de nombres local para ejecutar la función.
    local_namespace = {}

    # Inicia la definición de la función con el código proporcionado.
    codigo_funcion = "def tempFunction():\n"
    
    # Agrega las líneas de contenido, asegurándote de que estén indentadas correctamente.
    if content.strip():
        for linea in content.split('\n'):
            codigo_funcion += f"    {linea}\n"
    else:
        codigo_funcion += "    return None\n"
    
    # Termina la función y prepara la ejecución.
    codigo_funcion += "\nresultado = tempFunction()"

    try:
        # Ejecuta la definición de la función y luego la llama.
        exec(codigo_funcion, globals(), local_namespace)
    except SyntaxError as se:
        print(f"Error de sintaxis: {se}")
        return None
    except Exception as e:
        print(f"Error en la definición del código: {e}")
        return None

    # Devuelve el resultado de la función si fue ejecutada correctamente.
    return local_namespace.get('resultado')
            
def tokensRecognize(afd,txtContent):
    # Inicializa la posicion
    first = 0
    while first<=len(txtContent):
        res = segmentRecognize(afd,first,txtContent)
    
        if res[0]:
            resultado = genericFunction(res[3][2:-1])
            resultado = resultado if resultado!=None else ""
            print(resultado)
        else:
            message = f"ERROR al reconocer archivo txt en caracter no. {res[1]}: "
                
            return False

        first = res[1]
            
    return True