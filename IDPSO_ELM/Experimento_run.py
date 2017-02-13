#-*- coding: utf-8 -*-
'''
Created on 13 de fev de 2017

@author: gusta
'''

from Ferramentas.Tabela_Excel import Tabela_excel
from Ferramentas.Dataset import Datasets
from Comportamento.Run_Comportamento import Algoritmo_comportamento
from Sensores.Run_Sensores import Algoritmo_sensores
from Comportamento_sensores.Run_Comportameto_Sensor import Algoritmo_comportamento_sensor


def main():
    '''
        metodo para rodar o experimento
        
    '''
    
    #vez = [0, 1, 2, 3]
    #tipo = [1, 2, 3]
    #variacao = range(30, 50)
    
    ###########################################definindo os indices das series que serão experimentadas#################################################################################
    
    vez = [0]
    tipo = [1]
    variacao = range(30, 31)
    
    for i in vez:
        for j in tipo:
            for k in variacao:
               
                ###########################################instanciando o dataset#################################################################################
                if(i == 0):
                    dtst = Datasets()
                    dataset = dtst.Leitura_dados(dtst.bases_nlinear_abruptas(j, k))
                    nome_arquivo = 'nlin_abt_' + str(j) + '_variacao_' + str(k)
                    
                elif(i == 1):
                    dtst = Datasets()
                    dataset = dtst.Leitura_dados(dtst.bases_linear_abruptas(j, k))
                    nome_arquivo = 'lin_abt_' + str(j) + '_variacao_' + str(k)
                    
                elif(i == 2):
                    dtst = Datasets()
                    dataset = dtst.Leitura_dados(dtst.bases_nlinear_graduais(j, k))
                    nome_arquivo = 'nlin_grad_' + str(j) + '_variacao_' + str(k)
                    
                    
                elif(i == 3):
                    dtst = Datasets()
                    dataset = dtst.Leitura_dados(dtst.bases_linear_graduais(j, k))
                    nome_arquivo = 'nlin_grad_' + str(j) + '_variacao_' + str(k)
                ##################################################################################################################################################
                
                
                ######################################## criando a tabela onde as informa��es ser�o armazenadas ##################################################    
                tabela = Tabela_excel()
                nome = "Tabelas/"+nome_arquivo+".xls"
                folhas = ["comportamento", "sensores", "comportamento+sensores"]
                cabecalho = ["falsos alarmes", "atrasos", "falta deteccao", "MAPE", "tempo_execucao"]
                largura_col = 5000
                tabela.Criar_tabela(nome, folhas, cabecalho, largura_col)
                ##################################################################################################################################################
                
            
                
                #####################instanciando as variaveis para o construtor das classes#######################################################################
                qtd_train_inicial = 1000
                tamanho_janela = 500 
                passo = 3
                lags = 4
                qtd_neuronios = 10 
                numero_particulas = 30
                n_particulas_comportamento = numero_particulas
                qtd_sensores = 1  
                limite = 1
                ##################################################################################################################################################
                
                
                ##############################################definindo quantas vezes cada algoritmo ser� executado##############################################
                qtd_execucoes = 4
            
                for execucao in range(qtd_execucoes):
                    print(nome_arquivo + " -  Execucao [%s]"  %(execucao))
                    
                    #[falsos_alarmes, atrasos, falta_deteccao, MAPE, tempo_execucao] = [0, 1, 2, 3, 4]
                    
                    ########################################### instanciando os algoritmo e escrevendo as execucoes ####################################################
                    alg_cpt = Algoritmo_comportamento(dataset, qtd_train_inicial, tamanho_janela, passo, lags, qtd_neuronios, numero_particulas, n_particulas_comportamento, limite)
                    [falsos_alarmes, atrasos, falta_deteccao, MAPE, tempo_execucao] = alg_cpt.Executar(grafico=False)
                    tabela.Adicionar_Sheet_Linha(0, execucao, [falsos_alarmes, atrasos, falta_deteccao, MAPE, tempo_execucao])
                    
                    #alg_s = Algoritmo_sensores(dataset, qtd_train_inicial, tamanho_janela, passo, lags, qtd_neuronios, numero_particulas, qtd_sensores)
                    #[falsos_alarmes, atrasos, falta_deteccao, MAPE, tempo_execucao] = alg_s.Executar(grafico=False)
                    #tabela.Adicionar_Sheet_Linha(1, execucao, [falsos_alarmes, atrasos, falta_deteccao, MAPE, tempo_execucao])
                    
                    #alg_cpt_s = Algoritmo_comportamento_sensor(dataset, qtd_train_inicial, tamanho_janela, passo, lags, qtd_neuronios, numero_particulas, n_particulas_comportamento, qtd_sensores, limite)
                    #[falsos_alarmes, atrasos, falta_deteccao, MAPE, tempo_execucao] = alg_cpt_s.Executar(grafico=False)
                    #tabela.Adicionar_Sheet_Linha(2, execucao, [falsos_alarmes, atrasos, falta_deteccao, MAPE, tempo_execucao])
                    ##################################################################################################################################################
                        
                tabela.Calcular_Medias(qtd_execucoes)
                ##################################################################################################################################################
                
   
   
   
   
    
if __name__ == "__main__":
    main()

