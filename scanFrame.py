import pickle
import LabC
import AfLib

if __name__ == "__main__":
    
    with open('header.pkl', 'rb') as archivo_entrada_header:
        header = pickle.load(archivo_entrada_header)

    success = LabC.generate_scan('yalex.yal')
        
    with open('footer.pkl', 'rb') as archivo_entrada_footer:
        footer = pickle.load(archivo_entrada_footer)
        

    if success:
        contenido = f"""
import pickle 
import AfdLib

{header}
            
if __name__ == "__main__":
    #Lectura del objeto pkl
    with open('afd.pkl', 'rb') as archivo_entrada:
        afd = pickle.load(archivo_entrada)
            
    #Lectura del documento txt
    with open('YAPar2.txt', 'r', encoding='utf-8') as file:
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