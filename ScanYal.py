
import pickle 
import AfdLib


grammar = dict()

            
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
    

print("trailer")

