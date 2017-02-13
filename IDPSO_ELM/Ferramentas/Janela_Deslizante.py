#-*- coding: utf-8 -*-
'''
Created on 6 de fev de 2017

@author: gusta
'''
import numpy as np
import pandas as pd

class Janela():
    '''
    Classe para instanciar a janela deslizante 
    '''
    
    pass
        
    def Ajustar(self, valores):
        '''
        Metodo para ajustar o tamanho da jenela deslizante 
        :param valores: valores para serem inseridos na janela
        '''
        
        self.dados = valores
    
    def Add(self, valor):
        '''
        Metodo para inserir na janela deslizante, o valor mais antigo sera excluido 
        :param valor: valor de entrada
        '''
        
        self.dados = np.append(self.dados, valor)
        self.dados = np.delete(self.dados, 0)
        self.dados = np.column_stack(self.dados)
        
def main():
    stream = pd.read_excel('E:\Documentos\Cin - UFPE\Dissertação\Dataset\Series XLSX\Lineares\Abruptas\lin1_abt30.xlsx', header = None)
    stream = stream[0]
    stream = stream.as_matrix()
    
    janela = Janela()
    janela.Ajustar(stream[1:5])
    print(janela.dados)
    janela.Add(10)
    print(janela.dados)
    
if __name__ == "__main__":
    main() 
        
        