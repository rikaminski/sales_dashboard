import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(layout = 'wide')

def num_format(value, prefix = ''):
    for unit in ['','th']:
        if value < 1000:
            return f'{prefix} {value:.2f} {unit}'
        value /= 1000
    return f'{prefix} {value:.2f} milion'   

st.title('Sales Dash :shopping_trolley:')

url = 'https://labdados.com/produtos'

regions = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste','Sul']

st.sidebar.title('Filters')
region = st.sidebar.selectbox('Region', regions)

if region == 'Brasil':
    region = ''

all_years = st.sidebar.checkbox('All years data', value = True)
if all_years:
    ano = ''
else:
    ano = st.sidebar.slider('Year', 2020, 2023)


query_string = {'regiao' : region.lower(),
                'ano' : ano}

response = requests.get(url, params = query_string)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')
sellers_filter = st.sidebar.multiselect('Sellers', dados['Vendedor'].unique())
if sellers_filter:
    dados = dados[dados['Vendedor'].isin(sellers_filter)]

## Tables of Sales

states_revenue = dados.groupby('Local da compra')[['Preço']].sum() # [[]] Mantém em dataframe
states_revenue = dados.drop_duplicates(subset= 'Local da compra')[['Local da compra', 'lat','lon']].merge(states_revenue, left_on = 'Local da compra', right_index=True).sort_values('Preço', ascending=False)

mon_sales = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Preço'].sum().reset_index()
mon_sales['Ano'] = mon_sales['Data da Compra'].dt.year
mon_sales['Mês'] = mon_sales['Data da Compra'].dt.month_name()

mon_sales_cat = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)

#sales_qnt = dados.groupby()

## Tables of Sellers

sellers = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum','count']))

## Graph

fig_rev_states = px.bar(states_revenue.head(),
                        x = 'Local da compra',
                        y = 'Preço',
                        text_auto = True,
                        title = 'Top estados (receita)')

fig_rev_states.update_layout(yaxis_title = 'Revenue')

fig_rev_cat = px.bar(mon_sales_cat,
                     text_auto = True,
                     title = 'Receita por categoria')

fig_rev_cat.update_layout(yaxis_title = 'Revenue')

fig_map_rev = px.scatter_geo(states_revenue,
                            lat = 'lat', 
                            lon = 'lon', 
                            scope = 'south america',
                            size = 'Preço',
                            template = 'seaborn',
                            hover_name = 'Local da compra',
                            hover_data = {'lat': False, 'lon': False},
                            title = 'States Revenue')

fig_rev_month = px.line(mon_sales, 
                        x = 'Mês',
                        y = 'Preço',
                        markers = True,
                        range_y = (0, mon_sales.max()),
                        color = 'Ano',
                        line_dash = 'Ano',
                        title = 'Revenue Month')

fig_rev_month.update_layout(yaxis_title = 'Revenue')


## Streamlit visualization


tab1, tab2, tab3 = st.tabs(['Revenue','Sales Quantity','Sales'])

with tab1:
    col1,col2 = st.columns(2)
    with col1:
        st.metric('Revenue', num_format(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_map_rev, use_container_width = True)
        st.plotly_chart(fig_rev_states, use_container_width= True)
    with col2:
        st.metric('Sales Quantity', num_format(dados.shape[0]))
        st.plotly_chart(fig_rev_month, use_container_width = True)
        st.plotly_chart(fig_rev_cat, use_container_width = True)

with tab2:
    col1,col2 = st.columns(2)
    with col1:
        st.metric('Revenue', num_format(dados['Preço'].sum(), 'R$'))
    with col2:
        st.metric('Sales Quantity', num_format(dados.shape[0]))

with tab3:
    qnt_sellers = st.number_input('Sellers Quantity', 2, 10, 5)
    col1,col2 = st.columns(2)
    with col1:
        st.metric('Revenue', num_format(dados['Preço'].sum(), 'R$'))
        fig_rev_seller = px.bar(sellers[['sum']].sort_values('sum', ascending = False).head(qnt_sellers),
                                x = 'sum',
                                y = sellers[['sum']].sort_values('sum', ascending = False).head(qnt_sellers).index,
                                text_auto = True,
                                title = f'Top {qnt_sellers} vendedores (receita)')
        st.plotly_chart(fig_rev_seller)

    with col2:
        st.metric('Sales Quantity', num_format(dados.shape[0]))
        fig_sal_seller = px.bar(sellers[['count']].sort_values('count', ascending = False).head(qnt_sellers),
                                x = 'count',
                                y = sellers[['count']].sort_values('count', ascending = False).head(qnt_sellers).index,
                                text_auto = True,
                                title = f'Top {qnt_sellers} vendedores (volume)')
        st.plotly_chart(fig_sal_seller)




