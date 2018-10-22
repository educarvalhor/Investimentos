import sqlite3
import datetime as dt
from statistics import mean

import pandas as pd

def dif_mes(d1, d2):
    return d1.date().month - d2.date().month + (d1.date().year - d2.date().year) * 12

def busca_dados_db(data_ref):
    # CONECTA AO BANCO DE DADOS
    c = sqlite3.connect("dados_basicos_pb.db")

    # BUSCA DADOS NO BANCO DE DADOS
    try:
        IPCA12mQ = pd.read_sql("SELECT * FROM IPCA", c)
        IBOV = pd.read_sql("SELECT * FROM IBOV", c)
    except:
        print("Erro na conexão com o Banco de dados ")

    c.close()

    # %% CONVERTE IPCA DE STRING PARA FLOAT
    IPCA12m = IPCA12mQ['valor']
    IPCA12m = IPCA12m.str.replace(',|%', '').astype(float)
    IPCA12m = IPCA12m / 100

    # CRIA LISTA DO IPCA E IBOV
    datasIPCA = list(IPCA12mQ['data'])
    DatasIPCA = [dt.datetime.strptime(date, '%d/%m/%Y') for date in datasIPCA]
    datasIBOV = list(IBOV['Date'])
    DatasIBOV = [dt.datetime.strptime(date, '%Y-%m-%d %H:%M:%S') for date in datasIBOV]

    # ENCONTRA O ÍNDICE IPCA E IBOV REFERENTE À DATA REF


    lista_ind_IPCA = [abs(dif_mes(data, data_ref)) for data in DatasIPCA]
    lista_ind_IBOV = [abs(dif_mes(data, data_ref)) for data in DatasIBOV]

    ind_ref = max(min(lista_ind_IPCA), min(lista_ind_IBOV))

    ind_IPCA = lista_ind_IPCA.index(ind_ref)
    ind_IBOV = lista_ind_IBOV.index(ind_ref)

    IPCA12m = IPCA12m[ind_IPCA - 24:ind_IPCA + 1].reset_index(drop=True)
    IBOV = IBOV[ind_IBOV - 24:ind_IBOV + 1].reset_index(drop=True)

    return IPCA12m, IBOV, min(lista_ind_IPCA), min(lista_ind_IBOV)

def calcula_pb(IPCA12m, IBOV, data_ref, indIPCA, indIBOV):
    data_ref_date = data_ref.date()
    IBOVval = list(IBOV['Close'])

    # %% CÁLCULO VARIAÇÃO MENSAL E MÉDIA IPCA IBOV
    VAR_MEN_IPCA = [((IPCA12m[x + 1] - IPCA12m[x]) / IPCA12m[x]) for x, _ in enumerate(IPCA12m[:-1])]
    VAR_MEN_IBOV = [((IBOVval[x + 1] - IBOVval[x]) / IBOVval[x]) for x, _ in enumerate(IBOVval[:-1])]

    MEDIA_IPCA = [mean(VAR_MEN_IPCA[j:j + 12]) for j, _ in enumerate(VAR_MEN_IPCA[:13])]
    MEDIA_IBOV = [mean(VAR_MEN_IBOV[j:j + 12]) for j, _ in enumerate(VAR_MEN_IPCA[:13])]
    # %% DATAFRAME DOS DADOS IPCA E IBOV
    datasIBOV = IBOV.index.values
    IPCA12mL = list(IPCA12m)

    index = datasIBOV[-12:]
    df = pd.DataFrame(IPCA12mL[-12:], index=index, columns=['IPCA12m'])
    df['Var.IPCA(%)'] = VAR_MEN_IPCA[-12:]
    df['Var.IPCA(%)'] = df['Var.IPCA(%)'] * 100
    df['IBOV'] = IBOVval[-12:]
    df['Var.IBOV(%)'] = VAR_MEN_IBOV[-12:]
    df['Var.IBOV(%)'] = df['Var.IBOV(%)'] * 100
    df.round(2)

    # %% CÁLCULO DESVIOS
    VAR_MEN_IBOV = VAR_MEN_IBOV[-12:]
    VAR_MEN_IPCA = VAR_MEN_IPCA[-12:]
    MEDIA_IPCA = MEDIA_IPCA[-12:]
    MEDIA_IBOV = MEDIA_IBOV[-12:]
    DESVIO_IBOV = [VAR_MEN_IBOV[k] - MEDIA_IBOV[k]
                   if VAR_MEN_IBOV[k] < MEDIA_IBOV[k]
                   else 0
                   for k, _ in enumerate(MEDIA_IBOV)]

    DESVIO_IPCA = [VAR_MEN_IPCA[k] - MEDIA_IPCA[k]
                   if VAR_MEN_IPCA[k] < MEDIA_IPCA[k]
                   else 0
                   for k, _ in enumerate(MEDIA_IPCA)]
    # %% CÁLCULO SEMIVARIÂNCIA E COSSEMIVARIÂNCIA
    IPCA_X_IBOV = [DESVIO_IPCA[x] * DESVIO_IBOV[x] for x, _ in enumerate(DESVIO_IPCA)]

    SEMI_VAR_IPCA = mean([desvio_ipca ** 2 for desvio_ipca in DESVIO_IPCA])
    SEMI_VAR_IBOV = mean([desvio_ibov ** 2 for desvio_ibov in DESVIO_IBOV])
    COSSEMI_IPCA_IBOV = mean(IPCA_X_IBOV)
    # %% COSSEMIVARIANCIA MINIMA DA CARTEIRA
    P_IPCA = [i / 100 for i in range(0, 105, 5)]
    P_IBOV = [i / 100 for i in range(100, -5, -5)]

    COSSEMI_CART = [((P_IPCA[m] ** 2) * SEMI_VAR_IPCA) +
                    ((P_IBOV[m] ** 2) * SEMI_VAR_IBOV) +
                    (2 * P_IPCA[m] * P_IBOV[m] * COSSEMI_IPCA_IBOV)
                    for m, _ in enumerate(P_IPCA)]

    INDEX_MIN = COSSEMI_CART.index(min(COSSEMI_CART))
    RF = INDEX_MIN * 5

    if indIPCA == 0 and indIBOV == 0:
        resultado = "Data = " + str(data_ref_date.month) + "/" + str(data_ref_date.year) + ", RF =" + str(
            RF) + " RV = " + str(100 - RF)
    elif indIPCA > 0 and indIBOV == 0:
        data_IPCA = data_ref - dt.timedelta(days=indIPCA * 30)
        data_IPCA = data_IPCA.date()
        resultado = "Data = " + str(data_ref_date.month) + "/" + str(data_ref_date.year) + ", RF =" + str(
            RF) + " RV = " + str(100 - RF) + \
                    " - Dados de " + str(data_IPCA.month) + "/" + str(data_IPCA.year) + "(IPCA)"
    elif indIPCA == 0 and indIBOV > 0:
        data_IPCA = data_ref - dt.timedelta(days=indIPCA * 30)
        data_IPCA = data_IPCA.date()
        resultado = "Data = " + str(data_ref_date.month) + "/" + str(data_ref_date.year) + ", RF =" + str(
            RF) + " RV = " + str(100 - RF) + \
                    " - Dados de " + str(data_IPCA.month) + "/" + str(data_IPCA.year) + "(IBOV)"
    else:
        resultado = "Data = " + str(data_ref_date.month) + "/" + str(data_ref_date.year) + ". Os dados ainda não estão disponíveis ."

    return resultado , RF

def itera_pb(data_ref, qtd):
    proporcoes = []
    prop_graf = []
    datas = []
    for i in range(qtd):
        data_calculo_pb = data_ref - dt.timedelta(days=i * 31)
        IPCA12m, IBOV, indIPCA, indIBOV = busca_dados_db(data_calculo_pb)
        resultado,RF = calcula_pb(IPCA12m, IBOV, data_calculo_pb, indIPCA, indIBOV)
        proporcoes.append(resultado)
        prop_graf.append(RF)
        datas.append(dt.datetime.strftime(data_calculo_pb, '%m/%Y'),)
    return proporcoes , prop_graf , datas

def le_fundamentus():
    c = sqlite3.connect("dados_basicos_pb.db")
    df_fund = pd.read_sql("SELECT * FROM FUNDAMENTUS", c)
    nomes = pd.read_sql("SELECT * from CODIGOS",
                        c)  # http://www.bmfbovespa.com.br/pt_br/servicos/market-data/consultas/mercado-a-vista/titulos-negociaveis/

    # FAZ A JUNÇÃO DOS DOIS DF´S PARA PLOTAR O NOME DAS EMPRESAS
    # HOUVE A PERDA DE 4 EMPRESAS DEVIDO A NÃO APARECEREM NOS CÓDIGOS
    nomes['index'] = nomes['Cód. de Negociação']
    nomes['Nome'] = nomes['index'] + " - " + nomes['Nome']
    fund = df_fund.merge(nomes, on='index')
    c.close()

    return fund

def grafico_cdi(dt_init,dt_fim):

    # CONECTA AO BANCO DE DADOS
    c = sqlite3.connect("dados_basicos_pb.db")

    # BUSCA DADOS NO BANCO DE DADOS
    cdi = pd.read_sql("SELECT * FROM CDI", c)


