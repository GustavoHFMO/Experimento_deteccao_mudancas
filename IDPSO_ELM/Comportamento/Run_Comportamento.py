#-*- coding: utf-8 -*-
'''
Created on 6 de fev de 2017

@author: gusta
'''
import matplotlib.pyplot as plt
from Ferramentas.Janela_Deslizante import Janela
from Ferramentas.Dataset import Datasets
from Ferramentas.Particionar_Series import Particionar_series
from Ferramentas.Metricas_deteccao import Metricas_deteccao
from Ferramentas.Metricas_previsao import Metricas_previsao
from Ferramentas.IDPSO_ELM import IDPSO_ELM
from sklearn.metrics.regression import mean_absolute_error, mean_squared_error
import copy
import time
import numpy as np
import pandas as pd

class Algoritmo_comportamento():
    def __init__(self, dataset, qtd_train_inicial, tamanho_janela, passo, lags, qtd_neuronios, numero_particulas, n_particulas_comportamento, limite):
        
        '''
        construtor do algoritmo que detecta a mudanca de ambiente por meio do comportamento das particulas
        :param dataset: serie temporal que o algoritmo vai executar
        :param qtd_train_inicial: quantidade de exemplos para o treinamento inicial
        :param tamanho_janela: tamanho da janela de caracteristicas para identificar a mudanca
        :param passo: tamanho do passo para reavaliar o metodo de deteccao
        :param lags: quantidade de lags para modelar as entradas da RNA
        :param qtd_neuronios: quantidade de neuronios escondidos da RNA
        :param numero_particulas: numero de particulas para serem usadas no IDPSO
        :param n_particulas_comportamento: numero de particulas para serem monitoradas na detecccao de mudanca
        :param limite: contador para verificar a mudanca
        '''
        
        self.dataset = dataset
        self.qtd_train_inicial = qtd_train_inicial
        self.tamanho_janela = tamanho_janela
        self.passo = passo
        self.lags = lags
        self.qtd_neuronios = qtd_neuronios
        self.numero_particulas = numero_particulas
        self.n_particulas_comportamento = n_particulas_comportamento
        self.limite = limite
        
    def Atualizar_comportamento(self, vetor_caracteristicas, lags, enxame):
        
        '''
        Metodo para computar a deteccao de mudanca na serie temporal por meio do comportamento das particulas
        :param vetor_caracteristicas: vetor com uma amostra da serie temporal que sera avaliada para verificar a mudanca
        :param lags: quantidade de lags para modelar as entradas da RNA
        :param enxame: enxame utilizado para verificar a mudanca
        :return: retorna a media ou o comportamento do enxame em relacao ao vetor de caracteristicas
        '''
        
        #particionando o vetor de caracteristicas para usar para treinar 
        particao = Particionar_series(vetor_caracteristicas, [1, 0, 0], lags)
        [caracteristicas_entrada, caracteristicas_saida] = particao.Part_train()
        
        #variavel para salvar as medias das predicoes
        medias = []
        
        #realizando as previsoes e armazenando as acuracias 
        for i in range(self.n_particulas_comportamento):
            predicao_caracteristica = enxame.sensores[i].Predizer(caracteristicas_entrada)
            MAE = mean_absolute_error(caracteristicas_saida, predicao_caracteristica)
            medias.append(MAE)          

        #print(medias)
        #salvando a media e desvio padrao das acuracias
        comportamento = [0] * 2
        comportamento[0] = np.mean(medias)
        comportamento[1] = np.std(medias)
            
        return comportamento

    def Executar(self, grafico = None):
        '''
        Metodo para executar o procedimento do algoritmo
        :param grafico: variavel booleana para ativar ou desativar o grafico
        :return: retorna 5 variaveis: [falsos_alarmes, atrasos, falta_deteccao, MAPE, tempo_execucao]
        '''
        
        
        ################################################################################################################################################
        ################################# CONFIGURACAO DO DATASET ######################################################################################
        ################################################################################################################################################
        
        #dividindo os dados da dataset dinamica para treinamento_inicial inicial e para uso do stream dinâmico
        #qtd_train_inicial = 1000
        treinamento_inicial = self.dataset[0:self.qtd_train_inicial]
        stream = self.dataset[self.qtd_train_inicial:]
    
    
        
        ################################################################################################################################################
        ################################# PERIODO ESTATICO #############################################################################################
        ################################################################################################################################################
        
        
        #criando e treinando um enxame_vigente para realizar as previsões
        enxame_vigente = IDPSO_ELM(treinamento_inicial, [0.8, 0.2, 0], self.lags, self.qtd_neuronios)
        enxame_vigente.Parametros_IDPSO(50, self.numero_particulas, 0.9, 0.4, 2, 2, 5)
        enxame_vigente.Treinar()  
       
       
        
        #ajustando com os dados finais do treinamento a janela de predicao
        janela_predicao = Janela()
        janela_predicao.Ajustar(enxame_vigente.dataset[2][(len(enxame_vigente.dataset[2])-1):])
        predicao = enxame_vigente.Predizer(janela_predicao.dados)
        
        
        #janela com o atual conceito, tambem utilizada para armazenar os dados de retreinamento
        #tamanho = 400 
        janela_caracteristicas = Janela()
        ajuste = (len(treinamento_inicial) - self.tamanho_janela)
        janela_caracteristicas.Ajustar(treinamento_inicial[ajuste:])
    
        #ativando o sensor de comportamento de acordo com a primeira janela de caracteristicas
        #n_particulas_comportamento = 5
        comportamento = [0] * 2
        [comportamento[0], comportamento[1]] = self.Atualizar_comportamento(janela_caracteristicas.dados, self.lags, enxame_vigente)
        comportamento_atual = copy.deepcopy(comportamento)
        
        
        ################################################################################################################################################
        ################################# PERIODO DINAMICO #############################################################################################
        ################################################################################################################################################
        
        
        #variavel para armazenar o erro do stream
        erro_stream = []
        #variavel para armazenar as deteccoes
        deteccoes = []
        #variavel para armazenar o tempo inicial
        start_time = time.time()
        #variavel para auxiliar na contagem de detecções
        contador = 0
        #vetor para armazenar a predicoes_vetor
        predicoes_vetor = []
        
        
        #entrando no stream de dados
        for i in range(len(stream)):
            
            #computando o erro
            loss = mean_absolute_error(stream[i:i+1], predicao)
            
            #salvando o erro 
            erro_stream.append(loss)
            
            #salvando a predicao
            predicoes_vetor.append(predicao)
            
            #adicionando o novo dado a janela de predicao
            janela_predicao.Add(stream[i])
            
            #realizando a nova predicao com a nova janela de predicao
            predicao = enxame_vigente.Predizer(janela_predicao.dados)
            #print("[%d]: predicao: %s" % (i, predicao))
            #print("[%d]: real: %s" % (i, stream[i:i+1]))
            #print("[%d]: erro: %s" % (i, erro_stream[i]))
            
            #adicionando a nova instancia na janela de caracteristicas
            janela_caracteristicas.Add(stream[i])
            
            #tamanho do passo para computar a deteccao de mudanca
            if(i%self.passo == 0):
                #print("[%d]: %s" % (i, erro_stream[i]))
                
                #computando o comportamento para a janela de predicao, para somente uma instancia
                [comportamento_atual[0], comportamento_atual[1]] = self.Atualizar_comportamento(janela_caracteristicas.dados[0], self.lags, enxame_vigente)
                
                #limite_inferior = (comportamento[0]-comportamento[1])
                #limite_superior = (comportamento[0]+comportamento[1])
                #print("%s > %s > %s" % (limite_inferior, comportamento_atual[0], limite_superior))
                
                
                #verificando os ativador
                if(comportamento_atual[0] > (comportamento[0]+comportamento[1]) or comportamento_atual[0] < (comportamento[0]-comportamento[1])):
                    contador = contador + 1
                else:
                    contador = 0
                
                #procedimento pos mudança
                if(contador == self.limite):    
                    print("[%d] Detectou uma mudança" % (i))
                    deteccoes.append(i)
                    
                    #atualizando o enxame_vigente preditivo
                    enxame_novo = IDPSO_ELM(janela_caracteristicas.dados[0], [0.8, 0.2, 0], self.lags, self.qtd_neuronios)
                    enxame_novo.Parametros_IDPSO(50, self.numero_particulas, 0.9, 0.4, 2, 2, 5)
                    enxame_novo.Treinar() 
                    enxame_vigente = copy.deepcopy(enxame_novo)
                    
                    #atualizando os comportamento com o atual conceito
                    [comportamento[0], comportamento[1]] = self.Atualizar_comportamento(janela_caracteristicas.dados[0], self.lags, enxame_vigente)
                    comportamento_atual = copy.deepcopy(comportamento)
                    contador = 0

        
        #plotando o grafico de erro
        if(grafico == True):
            plt.style.use('ggplot')
            plt.yscale('linear')
            plt.legend()
            
            plt.plot(erro_stream)
            plt.show()
            
            plt.plot(stream, label = 'Serie original', color = 'Blue')
            plt.plot(predicoes_vetor, label = 'Previsão', color = 'Red')
            plt.show()
            
    
        #variavel para armazenar o tempo final
        end_time = time.time()
        
        #computando as metricas de deteccao
        mt = Metricas_deteccao()
        [falsos_alarmes, atrasos, falta_deteccao] = mt.resultados(deteccoes)
        
        #computando a acuracia da previsao ao longo do fluxo de dados
        mp = Metricas_previsao()
        MAPE = mp.mean_absolute_percentage_error(stream, predicoes_vetor)
        
        #computando o tempo de execucao
        tempo_execucao = (end_time-start_time)
        
        print("Deteccoes: ")
        for i in deteccoes:
            print(i)
        
        print("\nFalsos Alarmes: ", falsos_alarmes)
        print("Atrasos: ", atrasos)
        print("Falta de deteccao: ", falta_deteccao)
        print("MAPE: ", MAPE)
        print("Tempo de execucao: ", tempo_execucao)
        
        #retorno do metodo
        return falsos_alarmes, atrasos, falta_deteccao, MAPE, tempo_execucao
    
def main():
    
    #instanciando o dataset
    dtst = Datasets()
    dataset = dtst.Leitura_dados(dtst.bases_nlinear_graduais(1, 40))
    #pt = Particionar_series(dataset, [1, 0, 0])
    #dataset = pt.Normalizar(dataset)
        
    #instanciando o algoritmo com sensores
    qtd_train_inicial = 1000
    tamanho_janela = 500 
    passo = 3
    lags = 4
    qtd_neuronios = 10 
    numero_particulas = 30
    n_particulas_comportamento = numero_particulas 
    limite = 1
    alg = Algoritmo_comportamento(dataset, qtd_train_inicial, tamanho_janela, passo, lags, qtd_neuronios, numero_particulas, n_particulas_comportamento, limite)
    
    #colhendo os resultados
    [falsos_alarmes, atrasos, falta_deteccao, MAPE, tempo_execucao] = alg.Executar(grafico=False)
    
    print("\nFalsos Alarmes: ", falsos_alarmes)
    print("Atrasos: ", atrasos)
    print("Falta de deteccao: ", falta_deteccao)
    print("MAPE: ", MAPE)
    print("Tempo de execucao: ", tempo_execucao)

    
if __name__ == "__main__":
    main()      