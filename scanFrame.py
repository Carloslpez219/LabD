import pickle
import LabC
import AfLib

if __name__ == "__main__":

    success = LabC.generate_scan('slr-2.yal')

    if success:
        contenido = """# Este es un archivo Python generado automaticamente
import pickle 
import AfdLib
            
if __name__ == "__main__":
    #Lectura del objeto pkl
    with open('afd.pkl', 'rb') as archivo_entrada:
        afd = pickle.load(archivo_entrada)
            
    #Lectura del documento txt
    with open('texto.txt', 'r', encoding='utf-8') as file:
        txtContent = file.read()  # Leer todo el contenido del archivo
        
    AfdLib.tokensRecognize(afd,txtContent)
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