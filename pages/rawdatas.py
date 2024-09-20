import streamlit as st
import requests
import pandas as pd
import time

@st.cache_data

def to_csv(df):
    return df.to_csv(index = False).encode('utf-8')

def success_msg():
    sucesso = st.success('Download sucessful', icon = "✅")
    time.sleep(9)
    sucesso.empty()

st.title('Raw Data')

url = 'https://labdados.com/produtos'

response = requests.get(url)
data = pd.DataFrame.from_dict(response.json())
data['Data da Compra'] = pd.to_datetime(data['Data da Compra'], format = '%d/%m/%Y')

with st.expander('Columns'):
    cols = st.multiselect('Select columns', list(data.columns), list(data.columns))

st.sidebar.title('Filters')
with st.sidebar.expander('Product name'):
    prod = st.multiselect('Select product', data['Produto'].unique(), data['Produto'].unique())
with st.sidebar.expander('Product price'):
    price = st.slider('Select price', 0, 4000, (0,4000))
with st.sidebar.expander('Buy-in data'):
    purchase_date = st.date_input('Select date', (data['Data da Compra'].min(), data['Data da Compra'].max()))

query = '''
Produto in @prod and \
@price[0] <= Preço <= @price[1] and \
@purchase_date[0] <= `Data da Compra` <= @purchase_date[1] 
'''
filter_data = data.query(query)
filter_data = filter_data[cols]

st.dataframe(filter_data)
st.markdown(f'The table has :blue[{filter_data.shape[0]}] rows and :blue[{filter_data.shape[1]}] columns' )
st.markdown('Write a name for archive')

col1, col2 = st.columns(2)
with col1:
    arc_name = st.text_input('',label_visibility='collapsed', value = 'Data')
    arc_name += '.csv'
with col2:
    st.download_button('Download',data = to_csv(filter_data), file_name = arc_name, mime = 'text/to_csv', on_click = success_msg )
# with st.sidebar.expander('Nome do produto'):
#     produtos = st.multiselect('Selecione os produtos', dados['Produto'].unique(), dados['Produto'].unique())
# with st.sidebar.expander('Categoria do produto'):
#     categoria = st.multiselect('Selecione as categorias', dados['Categoria do Produto'].unique(), dados['Categoria do Produto'].unique())
# with st.sidebar.expander('Preço do produto'):
#     preco = st.slider('Selecione o preço', 0, 5000, (0,5000))
# with st.sidebar.expander('Frete da venda'):
#     frete = st.slider('Frete', 0,250, (0,250))
# with st.sidebar.expander('Data da compra'):
#     data_compra = st.date_input('Selecione a data', (dados['Data da Compra'].min(), dados['Data da Compra'].max()))
# with st.sidebar.expander('Vendedor'):
#     vendedores = st.multiselect('Selecione os vendedores', dados['Vendedor'].unique(), dados['Vendedor'].unique())
# with st.sidebar.expander('Local da compra'):
#     local_compra = st.multiselect('Selecione o local da compra', dados['Local da compra'].unique(), dados['Local da compra'].unique())
# with st.sidebar.expander('Avaliação da compra'):
#     avaliacao = st.slider('Selecione a avaliação da compra',1,5, value = (1,5))
# with st.sidebar.expander('Tipo de pagamento'):
#     tipo_pagamento = st.multiselect('Selecione o tipo de pagamento',dados['Tipo de pagamento'].unique(), dados['Tipo de pagamento'].unique())
# with st.sidebar.expander('Quantidade de parcelas'):
#     qtd_parcelas = st.slider('Selecione a quantidade de parcelas', 1, 24, (1,24))

# query = '''
# Produto in @produtos and \
# `Categoria do Produto` in @categoria and \
# @preco[0] <= Preço <= @preco[1] and \
# @frete[0] <= Frete <= @frete[1] and \
# @data_compra[0] <= `Data da Compra` <= @data_compra[1] and \
# Vendedor in @vendedores and \
# `Local da compra` in @local_compra and \
# @avaliacao[0]<= `Avaliação da compra` <= @avaliacao[1] and \
# `Tipo de pagamento` in @tipo_pagamento and \
# @qtd_parcelas[0] <= `Quantidade de parcelas` <= @qtd_parcelas[1]
# '''
