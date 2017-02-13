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

class Algoritmo_sensores():
    def __init__(self, dataset, qtd_train_inicial, tamanho_janela, passo, lags, qtd_neuronios, numero_particulas, qtd_sensores):
        '''
        construtor do algoritmo que detecta a mudanca de ambiente por meio de sensores
        :param dataset: serie temporal que o algoritmo vai executar
        :param qtd_train_inicial: quantidade de exemplos para o treinamento inicial
        :param tamanho_janela: tamanho da janela de caracteristicas para identificar a mudanca
        :param passo: tamanho do passo para reavaliar o metodo de deteccao
        :param lags: quantidade de lags para modelar as entradas da RNA
        :param qtd_neuronios: quantidade de neuronios escondidos da RNA
        :param numero_particulas: numero de particulas para serem usadas no IDPSO
        :param qtd_sensores: quantidade de sensores utilizados para detectar uma mudanca de conceito
        '''
        
        self.dataset = dataset
        self.qtd_train_inicial = qtd_train_inicial
        self.tamanho_janela = tamanho_janela
        self.passo = passo
        self.lags = lags
        self.qtd_neuronios = qtd_neuronios
        self.numero_particulas = numero_particulas
        self.qtd_sensores = qtd_sensores
        
    def Atualizar_sensores(self, vetor_caracteristicas, lags, modelo, sensor):
        '''
        Metodo para computar a deteccao de mudanca na serie temporal por meio do comportamento das particulas
        :param vetor_caracteristicas: vetor com uma amostra da serie temporal que sera avaliada para verificar a mudanca
        :param lags: quantidade de lags para modelar as entradas da RNA
        :param modelo: enxame utilizado para computar as estatisticas dos sensores
        :param sensor: particula utilizada como sensor
        :return: retorna a media e o desvio padrao do sensor para o vetor de caracteristicas: estatistica[media, desvio]
        '''
        
        particao = Particionar_series(vetor_caracteristicas, [1, 0, 0], lags)
        [caracteristicas_entrada, caracteristicas_saida] = particao.Part_train()
        predicao_caracteristica = sensor.Predizer(caracteristicas_entrada)
        #calculando a estatistica do sensor
        
        estatistica = [0] * 2
        [estatistica[0], estatistica[1]] = modelo.Calcular_estatistica(caracteristicas_saida, predicao_caracteristica)
        
        return estatistica

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
        
        
        #criando e treinando um modelo_vigente para realizar as previsões
        modelo_vigente = IDPSO_ELM(treinamento_inicial, [0.8, 0.2, 0], self.lags, self.qtd_neuronios)
        modelo_vigente.Parametros_IDPSO(50, self.numero_particulas, 0.9, 0.4, 2, 2, 5)
        modelo_vigente.Treinar()  
       
        #ajustando com os dados finais do treinamento a janela de predicao
        janela_predicao = Janela()
        janela_predicao.Ajustar(modelo_vigente.dataset[2][(len(modelo_vigente.dataset[2])-1):])
        predicao = modelo_vigente.Predizer(janela_predicao.dados)
        
        #janela com o atual conceito, tambem utilizada para armazenar os dados de retreinamento
        #tamanho = 400 
        janela_caracteristicas = Janela()
        ajuste = (len(treinamento_inicial) - self.tamanho_janela)
        janela_caracteristicas.Ajustar(treinamento_inicial[ajuste:])
    
        #ativando os sensores de acordo com a primeira janela de caracteristicas
        #qtd_sensores = 5
        sensores = []
        ativadores = [False] * self.qtd_sensores
        for i in range(self.qtd_sensores):
            sensores.append([0] * 2)
            
        for x, i in enumerate(sensores):
            [i[0], i[1]] = self.Atualizar_sensores(janela_caracteristicas.dados, self.lags, modelo_vigente, modelo_vigente.sensores[x])
            
        sensores_atuais = copy.deepcopy(sensores)
        
        
        ################################################################################################################################################
        ################################# PERIODO DINAMICO #############################################################################################
        ################################################################################################################################################
        
        
        #variavel para armazenar o erro do stream
        erro_stream = []
        #variavel para armazenar as deteccoes
        deteccoes = []
        #variavel para armazenar o tempo inicial
        start_time = time.time()
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
            predicao = modelo_vigente.Predizer(janela_predicao.dados)
            
            
            #adicionando a nova instancia na janela de caracteristicas
            janela_caracteristicas.Add(stream[i])
            
            #tamanho do passo para computar a deteccao de mudanca
            if(i%self.passo == 0):
                print("[%d]: %s" % (i, erro_stream[i]))
                
                #verificando os sensores
                for x, j in enumerate(sensores_atuais):
                    #computando a deteccao
                    [j[0], j[1]] = self.Atualizar_sensores(janela_caracteristicas.dados[0], self.lags, modelo_vigente, modelo_vigente.sensores[x])
                    #print("[%d] %s" % (i, j[0]))
                    #print("[%d] %s" % (i, sensores[x][0]))
                    
                    #verificando os ativadores
                    if(sensores_atuais[x][0] > (sensores[x][0]+sensores[x][1]) or sensores_atuais[x][0] < (sensores[x][0]-sensores[x][1])):
                        ativadores[x] = True
                    else:
                        ativadores[x] = False
                
                #procedimento pos mudança
                if(all(ativadores)):    
                    print("[%d] Detectou uma mudança" % (i))
                    deteccoes.append(i)
                    
                    #atualizando o modelo_vigente preditivo
                    modelo_novo = IDPSO_ELM(janela_caracteristicas.dados[0], [0.8, 0.2, 0], self.lags, self.qtd_neuronios)
                    modelo_novo.Parametros_IDPSO(50, self.numero_particulas, 0.9, 0.4, 2, 2, 5)
                    modelo_novo.Treinar() 
                    modelo_vigente = copy.deepcopy(modelo_novo)
                    
                    #atualizando os sensores com o atual conceito
                    for x, i in enumerate(sensores):
                        [i[0], i[1]] = self.Atualizar_sensores(janela_caracteristicas.dados[0], self.lags, modelo_vigente, modelo_vigente.sensores[x])
                    sensores_atuais = copy.deepcopy(sensores)
                    ativadores = [False] * self.qtd_sensores

        
        #plotando o grafico de erro
        if(grafico == True):
            plt.style.use('ggplot')
            plt.yscale('linear')
            plt.plot(erro_stream)
            plt.show()
            
            plt.plot(stream)
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
        
        #retorno do metodo
        return falsos_alarmes, atrasos, falta_deteccao, MAPE, tempo_execucao
    
def main():
    
    #instanciando o dataset
    dtst = Datasets()
    dataset = dtst.Leitura_dados(dtst.bases_nlinear_graduais(1, 40))
    #pt = Particionar_series(dataset, [1, 0, 0])
    #dataset = pt.Normalizar(dataset)
        
    #instanciando o algoritmo com sensores
    #dataset, qtd_train_inicial, tamanho_janela, passo, lags, qtd_neuronios, qtd_sensores
    qtd_train_inicial = 1000
    tamanho_janela = 500 
    passo = 3
    lags = 4
    qtd_neuronios = 10
    numero_particulas = 30 
    qtd_sensores = 3
    alg = Algoritmo_sensores(dataset, qtd_train_inicial, tamanho_janela, passo, lags, qtd_neuronios, numero_particulas, qtd_sensores)
    
    #colhendo os resultados
    [falsos_alarmes, atrasos, falta_deteccao, MAPE, tempo_execucao] = alg.Executar(grafico=False)
    
    print("\nFalsos Alarmes: ", falsos_alarmes)
    print("Atrasos: ", atrasos)
    print("Falta de deteccao: ", falta_deteccao)
    print("MAPE: ", MAPE)
    print("Tempo de execucao: ", tempo_execucao)
    
    
if __name__ == "__main__":
    main()      