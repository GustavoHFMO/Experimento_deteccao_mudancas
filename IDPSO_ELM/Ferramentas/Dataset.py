#-*- coding: utf-8 -*-
'''
Created on 8 de fev de 2017

@author: gusta
'''
import pandas as pd
import numpy as np

#caminho onde se encontram as bases xlsx
caminho_bases = 'E:\Documentos\Cin - UFPE\Dissertação\Dataset\Series XLSX'

class Datasets():
    '''
    classe que armazena as series com drifts
    '''
    
    pass

    def Leitura_dados(self, caminho):
        '''
        Metodo para fazer a leitura dos dados
        :param caminho: caminho da base que sera importada
        :return: retorna a serie temporal que o caminho direciona
        '''
        #leitura da serie dinamica
        stream = pd.read_excel(caminho, header = None)
        stream = stream[0]
        stream = stream.as_matrix()
        return stream
    
    def bases_linear_graduais(self, tipo, numero):
        '''
        Metodo para mostrar o caminho das bases lineares graduais
        :param tipo: tipo das series lineares, podem ser dos tipos: 1, 2 e 3
        :param numero: numero das variacoes das series, pode variar entre [30,49]
        :return: retorna o caminho da base
        '''
        
        base = (caminho_bases + '\Lineares\Graduais\lin' + str(tipo) + '_grad' + str(numero)+ '.xlsx') 
        return base
    
    def bases_linear_abruptas(self, tipo, numero):
        '''
        Metodo para mostrar o caminho das bases lineares abruptas
        :param tipo: tipo das series lineares, podem ser dos tipos: 1, 2 e 3
        :param numero: numero das variacoes das series, pode variar entre [30,49]
        :return: retorna o caminho da base
        '''
        
        base = (caminho_bases + '\Lineares\Abruptas\lin' + str(tipo) + '_abt' + str(numero)+ '.xlsx') 
        return base
    
    def bases_nlinear_graduais(self, tipo, numero):
        '''
        Metodo para mostrar o caminho das bases nao lineares graduais
        :param tipo: tipo das series lineares, podem ser dos tipos: 1, 2 e 3
        :param numero: numero das variacoes das series, pode variar entre [30,49]
        :return: retorna o caminho da base
        '''
        
        base = (caminho_bases + '\Lineares Não\Graduais\lin' +str(tipo)+ '_n_grad' +str(numero)+ '.xlsx') 
        return base
    
    def bases_nlinear_abruptas(self, tipo, numero):
        '''
        Metodo para mostrar o caminho das bases nao lineares abruptas
        :param tipo: tipo das series lineares, podem ser dos tipos: 1, 2 e 3
        :param numero: numero das variacoes das series, pode variar entre [30,49]
        :return: retorna o caminho da base
        '''
        
        base = (caminho_bases + '\Lineares Não\Abruptas\lin' + str(tipo) + '_n_abt' + str(numero)+ '.xlsx') 
        return base

def main():
    dtst = Datasets()
    dataset = dtst.Leitura_dados(dtst.bases_nlinear_abruptas(1, 30))
    print(dataset)
    
if __name__ == "__main__":
    main()