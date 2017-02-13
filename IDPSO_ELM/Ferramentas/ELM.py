#-*- coding: utf-8 -*-
'''
Created on 31 de jan de 2017

@author: gusta
'''

import numpy as np
from sklearn.metrics import mean_absolute_error
from Ferramentas.Particionar_Series import Particionar_series
import matplotlib.pyplot as plt 

#criando o construtor da classe ELMRegressor
class ELMRegressor():
    def __init__(self, neuronios_escondidos = None):
        '''
        Construtor do algoritmo ELM
        :param neuronios_escondidos: quantidade de neuronios para a camada escondida
        '''
        
        self.neuronios_escondidos = neuronios_escondidos

    #treinamento do ELM
    def Treinar(self, Entradas, Saidas, pesos_iniciais = None):
        '''
        Metodo para treinar a ELM por meio da pseudo-inversa
        :param Entradas: entradas para o treinamento da rede, esses dados sao uma matriz com uma quantidade de lags definida
        :param Saidas: saidas para o treinamento da rede, esses dados sao um vetor com as saidas correspodentes as entradas
        :return: retorna os pesos de saida da rede treinada
        '''
        
        
        #Entradas é uma lista de arrays com os padroes de entrada, matriz com os lags definidos 
        #Saidas é a saida, que possui a mesma quantidade de linhas que a matriz Entradas 
        
        #Entradas.shape[0] retorna a quantidade de linhas
        #Entradas.shape[1] retorna a quantidade de colunas
        
        #empilhando dois arrays de mesma dimensao
        #se for um array, a primeira coluna é dada pelos valores do array, enquanto que a segunda é cheia de numeros uns
        Entradas = np.column_stack([Entradas,np.ones([Entradas.shape[0],1])])
        
        #definindo os pesos iniciais aleatoriamente
        #cria uma matriz com numeros aleatorios de tamanho linha x coluna
        #pesos iniciais correspondentes a entrada
        
        if(pesos_iniciais == None):
            self.pesos_iniciais = np.random.randn(Entradas.shape[1], self.neuronios_escondidos)
        else:
            self.pesos_iniciais = pesos_iniciais
        
        #np.dot - multiplicação de matrizes
        #np.tan - tangente hiperbolica
        #np.linalg.pinv - pseudo inversa 
        
        
        G = np.tanh(Entradas.dot(self.pesos_iniciais))
        
        #cria-se os pesos da camada de saida
        self.pesos_saida = np.linalg.pinv(G).dot(Saidas)

    def Predizer(self, Entradas):
        '''
        Metodo para realizar a previsao de acordo com um conjunto de entrada
        :param Entradas: padroes que serao usados para realizar a previsao
        :return: retorna a previsao para o conjunto de padroes inseridos
        '''
        
        
        #empilhando dois arrays em colunas, o primeiro é dado pelo array Entradas e a segunda coluna é feita de numeros 1
        Entradas = np.column_stack([Entradas,np.ones([Entradas.shape[0],1])])
        
        G = np.tanh(Entradas.dot(self.pesos_iniciais))
            
        #previsao
        return G.dot(self.pesos_saida)
    
    def Otimizar_rede(self, neuronios_max, lista):
        '''
        Metodo para otimizar a arquitetura da ELM
        :param neuronios_max: quantidade maxima de neuronios que serao variados
        :param lista: esse parametro é uma lista com os seguintes dados [treinamento_entrada, treinamento_saida, validacao_entrada, validacao_saida]]
        '''
        
        
        BEST = []
        MAE_TEST_MINS = []
        
        #range (start, stop, step)
        for M in range(1, neuronios_max, 1):
            
            #variaveis para treinamento e teste
            #MAES_TRAIN = []
            MAES_TEST = []
            
            print("Training with %s neurons..."%M)
            
            #variando os pesos iniciais
            for i in range(10):
                #classe recebendo uma quantidade M de neuronios_max
                ELM = ELMRegressor(M)
                #ajustando o ELM para o conjunto de treinamento
                ELM.Treinar(lista[0], lista[1])
                #realizando a previsão para o treinamento
                prediction = ELM.Predizer(lista[0])
                #adicionando na lista o MAE do treinamento
                #MAES_TRAIN.append(mean_absolute_error(lista[1], prediction))
        
                #realizando a previsão para o teste
                prediction = ELM.Predizer(lista[2])
                #adicionando na lista o MAE do teste
                MAES_TEST.append(mean_absolute_error(lista[3], prediction))
                
            #salvando o menor MAE obtido no teste    
            MAE_TEST_MINS.append(np.mean(MAES_TEST))
            n_min = min(MAE_TEST_MINS)
            n_pos = MAE_TEST_MINS.index(n_min)
            self.neuronios_escondidos = n_pos
        
        #printando o menor erro obtido
        print("Minimum MAE ELM =", n_min)


def main():
    #Como usar
    
    
    #load da serie
    serie = np.loadtxt('Series/NN3-017.txt', 'float')
    divisao = [0.6, 0.2, 0.2]
    particao = Particionar_series(serie, divisao, 4)
    
    #tratamento dos dados
    [train_entrada, train_saida] = particao.Part_train()
    [val_entrada, val_saida] = particao.Part_val()
    [teste_entrada, teste_saida] = particao.Part_val()
    
    #transformação das listas em arrays
    train_entrada = np.asarray(train_entrada)
    train_saida = np.asarray(train_saida)
    val_entrada = np.asarray(val_entrada)
    val_saida = np.asarray(val_saida)
    teste_entrada = np.asarray(teste_entrada)
    teste_saida = np.asarray(teste_saida)
    
    #criando uma lista para os dados
    lista_dados = []
    lista_dados.append(train_entrada)
    lista_dados.append(train_saida)
    lista_dados.append(val_entrada)
    lista_dados.append(val_saida)
    lista_dados.append(teste_entrada)
    lista_dados.append(teste_saida)
    
    #Otimizando a arquitetura de uma ELM
    ELM = ELMRegressor()
    ELM.Otimizar_rede(100, lista_dados)
    ELM = ELMRegressor(ELM.neuronios_escondidos)
        
    #ELM treinando com a entrada e a saida
    ELM.Treinar(train_entrada, train_saida)
    prediction_train = ELM.Predizer(train_entrada)
    MAE_train = mean_absolute_error(train_saida, prediction_train)
    print('MAE Treinamento: ', MAE_train)
    
    #previsao do ELM para o conjunto de teste
    prediction_test = ELM.Predizer(teste_entrada)
    MAE_test = mean_absolute_error(teste_saida, prediction_test)
    print('MAE Teste: ', MAE_test)
    
    
    #grafico de previsao para treinamento
    plt.plot(train_saida, label = 'Real Treinamento', color = 'Blue')
    plt.plot(prediction_train, label = 'Real Previsão', color = 'Red')
    plt.title('Gráfico Treinamento, MAE: %s' %MAE_train)
    plt.legend()
    plt.tight_layout()
    plt.show()
    
    #grafico de previsao para teste
    plt.plot(teste_saida, label = 'Real Teste', color = 'Blue')
    plt.plot(prediction_test, label = 'Real Teste', color = 'Red')
    plt.title('Gráfico Teste, MAE: %s' %MAE_test)
    plt.legend()
    plt.tight_layout()
    plt.show()
    
    
    
if __name__ == "__main__":
    main()