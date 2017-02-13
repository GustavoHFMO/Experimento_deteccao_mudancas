#-*- coding: utf-8 -*-
from datetime import datetime
from xlwt import Workbook, Formula, easyxf, Font
import xlrd
import xlwt

class Tabela_excel():
    def __init__(self):
        '''
        classe para escrever dados em um arquivo xlsx
        '''
        
        self.wb = Workbook()
        self.sheets = []
        self.nome_tabela = []
        self.ncols = 0
    
    def Estilo_cabecalho(self):
        '''
        metodo para colocar um estilo no cabecalho
        '''
        
        #Fonte do cabecalho
        font_cabecalho = xlwt.Font()
        font_cabecalho.name = "Times New Roman"
        font_cabecalho.bold = True
        self.estilo_cabecalho = xlwt.XFStyle()
        self.estilo_cabecalho.font = font_cabecalho
        #self.estilo_cabecalho.num_format_str = '0.00%'
        
        return self.estilo_cabecalho
    
    def Estilo_texto(self):
        '''
        metodo para colocar um estilo no texto comum
        '''
        
        #Fonte do texto
        font_texto = xlwt.Font()
        font_texto.name = "Times New Roman"
        font_texto.bold = False
        self.estilo_texto = xlwt.XFStyle()
        self.estilo_texto.font = font_texto
        
        return self.estilo_texto

    def Gerar_nome(self, nome):
        '''
        metodo para gerar o nome do arquivo xlsx
        :param nome: string com o nome do futuro arquivo xlsx
        '''
        
        #data = datetime.now()
        #self.nome_tabela = str(nome)+ ' ' +str(data.strftime("%A %d %B %Y %H %M %S")) + '.xls'
        self.nome_tabela = str(nome) + '.xls'
                
    def Criar_tabela(self, nome_tabela, folhas, cabecalho = None, largura_col = None):
        '''
        metodo para criar o arquivo xlsx com a quantidade de folhas especificas
        :param nome: string com o nome do futuro arquivo xlsx
        :param folhas: lista com o nome e a quantidade de folhas que o arquivo vai possuir
        :param cabecalho: cabecalho para ser colocado no inicio de cada folha
        :param largura_col: largura de cada coluna escrita
        '''
        
        if(cabecalho != None):
            self.ncols = len(cabecalho)
        
        self.Gerar_nome(nome_tabela)
        
        #criando as folhas
        for e in folhas:
            self.sheets.append(self.wb.add_sheet(e))

        #obtendo os estilos da tabela
        estilo_cabecalho = self.Estilo_cabecalho()
        
        
        #criando os cabecalhos para as folhas
        if(cabecalho != None):
            for folha in self.sheets:
                for x, i in enumerate(cabecalho):
                    folha.write(0,x, i, estilo_cabecalho)
                    folha.col(x).width = largura_col
                        
        self.wb.save(self.nome_tabela)

    def Adicionar_Sheet_Linha(self, num_sheet, execucao, valores):
        '''
        metodo para escrever os dados em uma linha
        :param num_sheet: numero da folha que sera escrita
        :param execucao: linha na qual o valor deve ser escrito
        :param valores: lista com os valores que serao escritos por coluna
        '''
        
        
        estilo_texto = self.Estilo_texto()
        
        for x, valor in enumerate(valores):
            self.sheets[num_sheet].write(execucao+1, x, valor, estilo_texto)
        
        self.wb.save(self.nome_tabela)
        #print("Salvou!")
        
    def Adicionar_dado(self, num_sheet, coluna, linha, valor):
        '''
        metodo para escrever um dado especifico em uma determinada posicao
        :param num_sheet: numero da folha que sera escrita
        :param coluna: coluna na qual o valor deve ser escrito
        :param linha: linha na qual o valor deve ser escrito
        :param valor: valor que sera escrevido
        '''
        
        estilo_texto = self.Estilo_texto()
        
        self.sheets[num_sheet].write(coluna, linha, valor, estilo_texto)
        
        self.wb.save(self.nome_tabela)
        #print("Salvou!")
    
    def Calcular_Medias(self, qtd_execucoes):
        '''
        metodo para computar a media das colunas no final do arquivo
        :param qtd_execucoes: linha em que as medias serao escrevidas
        '''
        
        estilo_cabecalho = self.Estilo_cabecalho()
        
        for e in self.sheets:
            e.write(qtd_execucoes+1, 0, Formula('AVERAGE(A2:A'+str(qtd_execucoes+1)+')'), self.estilo_cabecalho)
            e.write(qtd_execucoes+1, 1, Formula('AVERAGE(B2:B'+str(qtd_execucoes+1)+')'), self.estilo_cabecalho)
            e.write(qtd_execucoes+1, 2, Formula('AVERAGE(C2:C'+str(qtd_execucoes+1)+')'), self.estilo_cabecalho)
            e.write(qtd_execucoes+1, 3, Formula('AVERAGE(D2:D'+str(qtd_execucoes+1)+')'), self.estilo_cabecalho)
            e.write(qtd_execucoes+1, 4, Formula('AVERAGE(E2:E'+str(qtd_execucoes+1)+')'), self.estilo_cabecalho)
        
        self.wb.save(self.nome_tabela)
        #print("Salvou a tabela!")
        

def main():
    '''
    tabela = Tabela_excel()
    nome = "Tabelas/teste3.xls"
    folhas = ["sheet1", "sheet2", "sheet3", "sheet4"]
    cabecalho = ["Cab1", "Cab2", "Cab3", "Cab4"]
    largura_col = 5000
    tabela.Criar_tabela(nome, folhas, cabecalho, largura_col)
    
    qtd_execucoes = 100
    
    for execucao in range(qtd_execucoes):
        print(execucao)
        
        for folha in range(len(folhas)):
            tabela.Adicionar_Sheet_Linha(folha, execucao, cabecalho)
            
    tabela.Calcular_Medias(qtd_execucoes)
    '''
    
    tabela = Tabela_excel()
    nome = "Tabelas/teste3.xls"
    folhas = ["sheet1"]
    largura_col = 5000
    
    tabela.Criar_tabela(nome, folhas, largura_col=largura_col)
    
    lista = [0, 1, 2, 3, 4, 5, 6, 7]
    lista[0] = 'Teste'
    lista[1] = [1, 2, 3, 4]
    lista[2] = ['a', 'a', 'a']
    lista[3] = [0, 1, 2, 3, 4, 5, 6, 7]


    contador = 0    
    for i in lista:
        for j in i:
            contador = contador + 1
            tabela.Adicionar_dado(0, 0, contador, j)
            
    
if __name__ == "__main__":
    main()


