#-*- coding: utf-8 -*-
import random
import numpy as np
import copy
import matplotlib.pyplot as plt
import deap.benchmarks as dp
from numpy import array
from numpy.random.mtrand import uniform
from Ferramentas.Particionar_Series import Particionar_series
from Ferramentas.ELM import ELMRegressor
from sklearn.metrics.regression import mean_absolute_error, mean_squared_error
from Ferramentas.Dataset import Datasets

#limites
Xmax = 2
Xmin = -Xmax
posMax = 1
posMin = -1
mi = 100

#variaveis auxiliares
contador = 0
fitness = 0
grafico = []
lista_MSE = []

class Particulas():
    pass

class IDPSO_ELM():
    def __init__(self, serie, divisao, janela, qtd_neuronios):
        '''
        Contrutor para o algoritmo de treinamento do ELM, o algoritmo utilizado e o IDPSO
        :param serie: vetor, com a serie temporal utilizada para treinamento 
        :param divisao: lista com porcentagens, da seguinte forma [pct_treinamento_entrada, pct_treinamento_saida, pct_validacao_entrada, pct_validacao_saida]
        :param janela: quantidade de lags usados para modelar os padroes de entrada da ELM
        :param qtd_neuronios: quantidade de neuronios da camada escondida da ELM
        '''
        
        #serie = vetor
        #divisao = lista com três porcentagens para divisao da serie
        #janela = quantidade de lags
        #qtd_neuronios = quantidade de neuronios
        
        #tratando os dados
        #dataset = [treinamento_entrada, treinamento_saida, validacao_entrada, valic_saida, teste_entrada, teste_saida]
        dataset = self.Tratamento_Dados(serie, divisao, janela)
        
        self.dataset = dataset
        self.qtd_neuronios = qtd_neuronios
        self.best_elm = []
        
        #default IDPSO
        self.linhas = self.dataset[0].shape[1] + 1
        self.numero_dimensoes =  self.linhas * qtd_neuronios
        
        self.iteracoes = 1000
        self.numero_particulas = 30
        self.inercia_inicial = 0.5
        self.inercia_final = 0.3
        self.c1_fixo = 2.4
        self.c2_fixo = 1.4
        self.crit_parada = 50
        self.particulas = []
        self.gbest = []
        
        self.particulas_ordenadas = [0] * self.numero_particulas
        self.sensores = [0] * self.numero_particulas
        
    def Parametros_IDPSO(self, iteracoes, numero_particulas, inercia_inicial, inercia_final, c1, c2, crit_parada):
        '''
        Metodo para alterar os parametros basicos do IDPSO 
        :param iteracoes: quantidade de geracoes para o treinamento 
        :param numero_particulas: quantidade de particulas usadas para treinamento
        :param inercia_inicial: inercial inicial para treinamento
        :param inercia_final: inercia final para variacao
        :param c1: coeficiente cognitivo
        :param c2: coeficiente pessoal
        :param crit_parada: criterio de parada para limitar a repeticao nao melhora do gbest
        '''
        
        self.iteracoes = iteracoes
        self.numero_particulas = numero_particulas
        self.inercia_inicial = inercia_inicial
        self.inercia_final = inercia_final
        self.c1_fixo = c1
        self.c2_fixo = c2
        self.crit_parada = crit_parada
        
        self.particulas_ordenadas = [0] * self.numero_particulas
        self.sensores = [0] * self.numero_particulas
    
    def Tratamento_Dados(self, serie, divisao, janela):
        '''
        Metodo para dividir a serie temporal em treinamento e validacao 
        :param serie: vetor, com a serie temporal utilizada para treinamento 
        :param divisao: lista com porcentagens, da seguinte forma [pct_treinamento_entrada, pct_treinamento_saida, pct_validacao_entrada, pct_validacao_saida]
        :param janela: quantidade de lags usados para modelar os padroes de entrada da ELM
        :return: retorna uma lista com os seguintes dados [treinamento_entrada, treinamento_saida, validacao_entrada, validacao_saida]
        '''
        
        #tratamento dos dados
        particao = Particionar_series(serie, divisao, janela)
        [train_entrada, train_saida] = particao.Part_train()
        [val_entrada, val_saida] = particao.Part_val()
        
        #inserindo os dados em uma lista
        lista_dados = []
        lista_dados.append(train_entrada)
        lista_dados.append(train_saida)
        lista_dados.append(val_entrada)
        lista_dados.append(val_saida)
        
        #retornando o valor
        return lista_dados
      
    def Criar_Particula(self):
        '''
        Metodo para criar todas as particulas do enxame de forma aleatoria 
        '''
        
        global contador, fitness, grafico, lista_MSE
        contador = 0
        fitness = 0
        grafico = []
        lista_MSE = []
        
        for i in range(self.numero_particulas):
            p = Particulas()
            p.posicao = array([uniform(posMin,posMax) for i in range(self.numero_dimensoes)])
            p.fitness = self.Funcao(p.posicao)
            p.velocidade = array([0.0 for i in range(self.numero_dimensoes)])
            p.best = p.posicao
            p.fit_best = p.fitness
            p.c1 = self.c1_fixo
            p.c2 = self.c2_fixo
            p.inercia = self.inercia_inicial
            p.phi = 0
            self.particulas.append(p)
        
        self.gbest = self.particulas[0]
        
    def Funcao(self, posicao):
        '''
        Metodo para calcular a funcao objetivo do IDPSO, nesse caso a funcao e a previsao de um ELM 
        :param posicao: posicao seria os pesos da camada de entrada e os bias da rede ELM 
        :return: retorna o MSE obtido da previsao de uma ELM
        '''
        
        ELM = ELMRegressor(self.qtd_neuronios)
        
        #modelando a dimensao das particulas para serem usadas 
        posicao = posicao.reshape(self.linhas, self.qtd_neuronios)
        
        #ELM treinando com a entrada e a saida e os pesos iniciais definidos pelo IDPSO 
        ELM.Treinar(self.dataset[0], self.dataset[1], posicao)
        prediction_train = ELM.Predizer(self.dataset[0])
        MSE_train = mean_squared_error(self.dataset[1], prediction_train)
        
        return MSE_train
    
    def Fitness(self):
        '''
        Metodo para computar o fitness de todas as particulas 
        '''
        
        for i in self.particulas:   
            i.fitness = self.Funcao(i.posicao)
        
    def Velocidade(self):
        '''
        Metodo para computar a velocidade de todas as particulas 
        '''
        
        calculo_c1 = 0
        calculo_c2 = 0
        
        for i in self.particulas:
            for j in range(len(i.posicao)):
                calculo_c1 = (i.best[j] - i.posicao[j])
                calculo_c2 = (self.gbest.posicao[j] - i.posicao[j])
                
                influecia_inercia = (i.inercia * i.velocidade[j])
                influencia_cognitiva = ((i.c1 * random.random()) * calculo_c1)
                influecia_social = ((i.c2 * random.random()) * calculo_c2)
              
                i.velocidade[j] = influecia_inercia + influencia_cognitiva + influecia_social
                
                if (i.velocidade[j] >= Xmax):
                    i.velocidade[j] = Xmax
                elif(i.velocidade[j] <= Xmin):
                    i.velocidade[j] = Xmin
              
    def Atualizar_particulas(self):
        '''
        Metodo para atualizar a posicao de todas as particulas 
        '''
        
        
        for i in self.particulas:
            for j in range(len(i.posicao)):
                i.posicao[j] = i.posicao[j] + i.velocidade[j]
                
                if (i.posicao[j] >= posMax):
                    i.posicao[j] = posMax
                elif(i.posicao[j] <= posMin):
                    i.posicao[j] = posMin

    def Atualizar_parametros(self, iteracao):
        '''
        Metodo para atualizar os parametros: inercia, c1 e c2 
        '''
        
        
        for i in self.particulas:
            parte1 = 0
            parte2 = 0
            
            for j in range(len(i.posicao)):
                parte1 = parte1 + self.gbest.posicao[j] - i.posicao[j]
                parte2 = parte2 + i.best[j] - i.posicao[j]
                
                if(parte1 == 0):
                    parte1 = 1
                if(parte2 == 0):
                    parte2 = 1
                    
            i.phi = abs(parte1/parte2)
            
        for i in self.particulas:
            ln = np.log(i.phi)
            calculo = i.phi * (iteracao - ((1 + ln) * self.iteracoes) / mi)
            i.inercia = ((self.inercia_inicial - self.inercia_final) / (1 + np.exp(calculo))) + self.inercia_final
            i.c1 = self.c1_fixo * (i.phi ** (-1))
            i.c2 = self.c2_fixo * i.phi
       
    def Pbest(self):
        '''
        Metodo para computar os pbests das particulas  
        '''
        
        for i in self.particulas:
            if(i.fit_best >= i.fitness):
                i.best = i.posicao
                i.fit_best = i.fitness

    def Gbest(self):
        '''
        Metodo para computar o gbest do enxame  
        '''
        
        for i in self.particulas:
            if(i.fitness <= self.gbest.fitness):
                self.gbest = copy.deepcopy(i)
    
    
    
    def Criterio_parada(self, i):
        '''
        Metodo para computar os criterios de parada, tanto o GL5 como o para nao melhora da melhor solucao
        :param i: atual geracao
        :return: retorna a indice da ultima geracao para parar o algoritmo  
        '''
        
        global contador, fitness, lista_MSE
        
        if(i == 0):
            fitness = copy.deepcopy(self.gbest.fitness)
            return i
        
        else:
            atual_MSE = self.Validacao()
            lista_MSE.append(atual_MSE)
            
            min_MSE = np.min(lista_MSE)
            GL5 = min_MSE + (min_MSE * 0.05)
            
            if(atual_MSE >= GL5 and i > 5):
                #print("[%d] GL5: " % (i) + " : ", self.gbest.fitness)
                return self.iteracoes
            
            if(contador == self.crit_parada):
                #print("[%d] Sem melhora: " % (i) + " : ", self.gbest.fitness)
                return self.iteracoes
            
            if(fitness == self.gbest.fitness):
                contador+=1
                return i
            
            else:
                fitness = copy.deepcopy(self.gbest.fitness)
                contador = 0
                return i
            
    def Grafico_Convergencia(self, fitness, i):
        '''
        Metodo para apresentar o grafico de convergencia
        :param fitness: fitness da melhor particula da geracao
        :param i: atual geracao
        '''
        
        global grafico
        
        grafico.append(fitness)
        
        if(i == self.iteracoes):
            plt.plot(grafico)
            plt.title('Gráfico de Convergência')
            plt.show()
            
    def Predizer(self, Entradas, Saidas = None, grafico = None):
        '''
        Metodo para realizar a previsao com a melhor particula (ELM) do enxame e apresentar o grafico de previsao
        :param Entradas: padroes de entrada para realizar a previsao
        :param Saidas: padroes de saida para computar o MSE
        :param grafico: variavel booleana para ativar ou desativar o grafico de previsao
        :return: Retorna a predicao para as entradas apresentadas. Se as entradas e saidas sao apresentadas o MSE e retornado
        '''
        
        #retorna somente a previsao
        if(Saidas == None):
            prediction = self.best_elm.Predizer(Entradas)
            return prediction
        else:
            prediction = self.best_elm.Predizer(Entradas)
            MSE = mean_squared_error(Saidas, prediction)
            print('\n MSE: %s' %MSE)

            #apresentar grafico
            if(grafico == True):
                plt.plot(Saidas, label = 'Real', color = 'Blue')
                plt.plot(prediction, label = 'Previsão', color = 'Red')
                plt.title('MSE: %s' %MSE)
                plt.legend()
                plt.tight_layout()
                plt.show()
            
            return MSE
        
    def Realizar_Previsao(self, Entradas):
        '''
        Metodo para realizar a previsao com a melhor particula (ELM) do enxame
        :param Entradas: padroes de entrada para realizar a previsao
        :return: Retorna a predicao para as entradas apresentadas
        '''
        
        return self.best_elm.Predizer(Entradas)
    
    def Validacao (self):
        '''
        Metodo para calcular o erro no conjunto de validacao
        :return: Retorna o erro para o conjunto de validacao 
        '''
        
        ELM = ELMRegressor(self.qtd_neuronios)
        
        #modelando a dimensao das particulas para serem usadas 
        posicao = self.gbest.posicao.reshape(self.linhas, self.qtd_neuronios)
        
        #ELM treinando com a entrada e a saida e os pesos iniciais definidos pelo IDPSO 
        ELM.Treinar(self.dataset[0], self.dataset[1], posicao)
        
        #previsao do ELM para o conjunto de teste
        prediction_val = ELM.Predizer(self.dataset[2])
        MAE_val = mean_squared_error(self.dataset[3], prediction_val)
        
        return MAE_val
    
    def Calcular_estatistica(self, real, previsao):
        '''
        Metodo para calcular a media e desvio padrao de uma particula para um cojunto de dados de entrada 
        :param real: dados reais
        :param real: previsao para os dados reais
        :return: retorna uma lista com as estatisticas da particula, da seguinte forma: [acuracia_media, acuracia_desvio]
        '''
        
        acuracias = []
        
        for x, i in enumerate(real):
            acuracias.append(mean_squared_error(real[x:x+1], previsao[x:x+1]))
        
        acuracia_media = np.mean(acuracias)
        acuracia_desvio = np.std(acuracias)
        
        return [acuracia_media, acuracia_desvio]
    
    def Ordenar_particulas(self):
        '''
        Metodo para ordenar as particulas por menor fitness  
        '''
        
        self.particulas_ordenadas = copy.deepcopy(self.particulas)
        
        for i in range(0, len(self.particulas_ordenadas)-1):
            imin = i
            for j in range(i+1, len(self.particulas_ordenadas)):
                if(self.particulas_ordenadas[j].fitness < self.particulas_ordenadas[imin].fitness):
                    imin = j
            aux = self.particulas_ordenadas[imin]
            self.particulas_ordenadas[imin]  = self.particulas_ordenadas[i]
            self.particulas_ordenadas[i] = aux
            
    def Obter_sensores(self):
        '''
        Metodo para obter os sensores (particulas) ordenados 
        '''
        
        self.Ordenar_particulas()
        
        for x, i in enumerate(self.particulas_ordenadas):
            ELM = ELMRegressor(self.qtd_neuronios)
            posicao = i.posicao.reshape(self.linhas, self.qtd_neuronios)
            ELM.Treinar(self.dataset[0], self.dataset[1], posicao)
            self.sensores[x] = ELM
            
        self.best_elm = self.sensores[0]
        
    def Treinar(self):
        '''
        Metodo para treinar a rede ELM com o IDPSO 
        '''
        
        self.Criar_Particula()       
        
        i = 0
        while(i < self.iteracoes):
            i = i + 1
            
            self.Fitness()
            self.Gbest()
            self.Pbest()
            self.Velocidade()
            self.Atualizar_parametros(i)
            self.Atualizar_particulas()
            
            #print("[%d]" % (i) + " : ", self.gbest.fitness)
            
            i = self.Criterio_parada(i)
            #self.Grafico_Convergencia(self.gbest.fitness, i)
        
        self.Obter_sensores()
        
def main():
    #load da serie
    dtst = Datasets()
    serie = dtst.Leitura_dados(dtst.bases_nlinear_abruptas(1, 49))

    modelo = IDPSO_ELM(serie, [0.8, 0.2, 0], 4, 30)
    modelo.Parametros_IDPSO(50, 30, 0.8, 0.4, 2, 2, 5)
    modelo.Treinar()  
    
    #exemplo de como predizer um valor:
    #modelo.Predizer(modelo.dataset[0][1:2])
    
    #exemplo de como plotar um grafico:
    #modelo.Predizer(modelo.dataset[0], modelo.dataset[1], True)
    #modelo.Predizer(modelo.dataset[2], modelo.dataset[3], True)      
    
    #exemplo de como se calcular a estatistica:
    #previsao = modelo.Predizer(modelo.dataset[0])
    #modelo.Calcular_estatistica(modelo.dataset[1], previsao)
    
if __name__ == "__main__":
    main()
    

