import pickle
import LabC
import AfLib

if __name__ == "__main__":
    
    with open('header.pkl', 'rb') as archivo_entrada_header:
        header = pickle.load(archivo_entrada_header)

    success = LabC.generate_scan('conflicto.yal', 'YAL')
        
    with open('footer.pkl', 'rb') as archivo_entrada_footer:
        footer = pickle.load(archivo_entrada_footer)
        

    if success:
        contenido = f"""
import pickle 
import AfdLib

{header}
            
if __name__ == "__main__":
    #Lectura del objeto pkl
    with open('afd_YAL.pkl', 'rb') as archivo_entrada:
        afd = pickle.load(archivo_entrada)
    
    input_tokens = []
    with open('input_tokens.pkl', 'wb') as archivo_input_tokens:
            pickle.dump(input_tokens, archivo_input_tokens)
        
    #Lectura del documento txt
    with open('entrada1.txt', 'r', encoding='utf-8') as file:
        txtContent = file.read()  # Leer todo el contenido del archivo
        
    AfdLib.tokensRecognizeYAL(afd,txtContent)
    
{footer}
"""


        # Especificar el nombre del archivo que deseas crear
        nombre_archivo = 'ScanYal.py'

        # Abrir el archivo para escritura
        with open(nombre_archivo, 'w') as archivo:
            # Escribir el contenido al archivo
            archivo.write(contenido)

        print("---------------------------------------")
        print(f'{nombre_archivo} generado!')
        print("---------------------------------------")
        


######################################################################################################################
#GENERAR SEGUNDO ESCANER
######################################################################################################################        




    with open('header.pkl', 'rb') as archivo_entrada_header:
        header = pickle.load(archivo_entrada_header)

    success = LabC.generate_scan('yalex.yal', "YAPARYAL")
        
    with open('footer.pkl', 'rb') as archivo_entrada_footer:
        footer = pickle.load(archivo_entrada_footer)
        

    if success:
        contenido = f"""
import pickle 
import AfdLib

{header}
            
if __name__ == "__main__":
    #Lectura del objeto pkl
    with open('afd_YAPARYAL.pkl', 'rb') as archivo_entrada:
        afd = pickle.load(archivo_entrada)
            
    #Lectura del documento txt
    with open('conflicto.yalp', 'r', encoding='utf-8') as file:
        txtContent = file.read()  # Leer todo el contenido del archivo
        
    AfdLib.tokensRecognize(afd,txtContent)
    
{footer}
"""


        # Especificar el nombre del archivo que deseas crear
        nombre_archivo = 'Scan.py'

        # Abrir el archivo para escritura
        with open(nombre_archivo, 'w') as archivo:
            # Escribir el contenido al archivo
            archivo.write(contenido)

        print("---------------------------------------")
        print(f'{nombre_archivo} generado!')
        print("---------------------------------------")