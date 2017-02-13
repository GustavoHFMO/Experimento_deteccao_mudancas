'''
Created on 13 de fev de 2017

@author: gusta
'''
import numpy as np

det1 = 2000
det2 = 5000
det3 = 8000

class Metricas_deteccao():
    '''
    Classe para instanciar as metricas de deteccao  
    '''
    
    pass

    def resultados(self, lista):
        '''
        Metodo para computar os falsos_alarmes, atrasos e a porcentagem de falta de deteccao
        :param lista: lista com os indices de todas as deteccoes encontradas
        :return: retorna uma lista com os seguintes valores [falsos_alarmes, atrasos, porcentagem_falta_deteccao] 
        '''
        
        
        deteccoes = 0
        deteccoes_verdadeiras = [False] * 3
        auxiliar = [False] * 3
        
        
        falsos_alarmes = 0
        atrasos = 0
        falta_deteccao = 0
        
        increment = 1
        
        for x, i in enumerate(lista):
            
            #condicoes para computar os atrasos e falsos alarmes
            if(i >= 0 and i < det1):
                falsos_alarmes += increment
            
            elif(i >= det1 and i < det2):
                deteccoes += increment
                
                if(auxiliar[0] == False):
                    atrasos = atrasos + i-det1
                
                auxiliar[0] = True  
                
                if(deteccoes_verdadeiras[0] == True):
                    falsos_alarmes += increment
            
                if(auxiliar[0] == True):
                    deteccoes_verdadeiras[0] = True
             
            elif(i >= det2 and i < det3):
                deteccoes += increment
                
                if(auxiliar[1] == False):
                    atrasos = atrasos + i-det2
                
                auxiliar[1] = True  
                
                if(deteccoes_verdadeiras[1] == True):
                    falsos_alarmes += increment
            
                if(auxiliar[1] == True):
                    deteccoes_verdadeiras[1] = True   
            
            
            elif(i >= det3):
                deteccoes += increment
                
                if(auxiliar[2] == False):
                    atrasos = atrasos + i-det3
                
                auxiliar[2] = True  
                
                if(deteccoes_verdadeiras[2] == True):
                    falsos_alarmes += increment
            
                if(auxiliar[2] == True):
                    deteccoes_verdadeiras[2] = True
            
            else:
                falta_deteccao += increment
                atrasos = atrasos + det3-det2
            
            
            
        #condicoes para computar as faltas de deteccoes e os atrasos
        if(deteccoes_verdadeiras[0] == False):
            falta_deteccao += increment
            atrasos = atrasos + det2-det1
        if(deteccoes_verdadeiras[1] == False):
            falta_deteccao += increment
            atrasos = atrasos + det3-det2
        if(deteccoes_verdadeiras[2] == False):
            falta_deteccao += increment
            atrasos = atrasos + 11000-det3
            
        
        porcentagem_falta_deteccao = falta_deteccao/3       
        
        return falsos_alarmes, atrasos, porcentagem_falta_deteccao

def main():
    #falsos alarmes: 11
    #atrasos: 7 + 13 = 3020
    #falta de detecao = 0.33
    lista = [2007, 2010, 2019, 2022, 2157, 2472, 2802, 2829, 2889, 5013, 5037, 5103, 5109]
    
    #falsos alarmes: 3
    #atrasos: 19 + 10 = 3029
    #falta de detecao = 0.33
    lista1 = [2019, 5010, 5016, 5037, 5040]
    
    
    #falsos alarmes: 2
    #atrasos: 18 + 15 + 40 = 73
    #falta de detecao = 0
    lista2 = [2018, 2803, 5015, 5077, 8040]
    
    #falsos alarmes: 1
    #atrasos: 2000 + 1000 + 0 = 3000
    #falta de detecao = 0
    lista3 = [4000, 6000, 8000, 10000]
    
    
    #falsos alarmes: 26
    #atrasos: 199 + 229 + 1654 = 2082
    #falta de detecao = 0
    lista4 = [2199, 2205, 2208, 2229, 2232, 2286, 2289, 2349, 2352, 2355, 2391, 2415, 2427, 2445, 2616, 2754, 2763, 2775, 2781, 2784, 2796, 2811, 3024, 3066, 5229, 5304,  5556, 5577, 9654]
    
    #falsos alarmes: 0
    #atrasos: 9000
    #falta de detecao = 1
    lista5 = []
    
    #falsos alarmes: 29
    #atrasos: 16 + 7 + 3000 = 3023
    #falta de detecao = 0.3
    lista6 = [0, 396, 399, 501, 708, 777, 2016, 2100, 2163, 2166, 2196, 2355, 3060, 3066, 3069, 3075, 3120, 3123, 3126, 3315, 3318, 3357, 3387, 3390, 4197, 4200, 4203, 5007, 5010, 5049, 7086]
    mt = Metricas_deteccao()
    [falsos_alarmes, atrasos, falta_deteccao] = mt.resultados(lista6)
    
    print("Falsos Alarmes: ", falsos_alarmes)
    print("Atrasos na deteccao: ", atrasos)
    print("Falta de deteccao: ", falta_deteccao)
    
    

if __name__ == "__main__":
    main()  