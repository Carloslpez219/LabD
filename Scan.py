
import pickle 
import AfdLib


print("header")

            
if __name__ == "__main__":
    #Lectura del objeto pkl
    with open('afd_YAPARYAL.pkl', 'rb') as archivo_entrada:
        afd = pickle.load(archivo_entrada)
            
    #Lectura del documento txt
    with open('conflicto.yalp', 'r', encoding='utf-8') as file:
        txtContent = file.read()  # Leer todo el contenido del archivo
        
    AfdLib.tokensRecognize(afd,txtContent)
    



