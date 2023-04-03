import pandas as pd
import inflection as inflection
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static
import plotly.express as px

st.set_page_config(
    page_title="Countries",
    layout = "wide",
    page_icon="🌎",
)

#=========================================
#Funções
#=========================================

def clean_code(df1):
    #Removendo dados faltantes
    df1.dropna(subset=['Cuisines'] , inplace=True)

    # Preenchimento do nome dos países  
    COUNTRIES = {
      1: "India",
      14: "Australia",
      30: "Brazil",
      37: "Canada",
      94: "Indonesia",
      148: "New Zeland",
      162: "Philippines",
      166: "Qatar",
      184: "Singapure",
      189: "South Africa",
      191: "Sri Lanka",
      208: "Turkey",
      214: "United Arab Emirates",
      215: "England",
      216: "United States of America",
      }
    def country_name(country_id):
      return COUNTRIES[country_id]
    df1["Country Name"] = df1.loc[:, "Country Code"].apply(country_name)

    # Criação do Tipo de Categoria de Comida
    def create_price_tye(price_range):
      if price_range == 1:
        return "cheap"
      elif price_range == 2:
        return "normal"
      elif price_range == 3:
        return "expensive"
      else:
        return "gourmet"
    df1["Price range Name"] = df1.loc[:, "Price range"].apply(create_price_tye)

    #Criação do nome das Cores
    COLORS = {
    "3F7E00": "darkgreen",
    "5BA829": "green",
    "9ACD32": "lightgreen",
    "CDD614": "orange",
    "FFBA00": "red",
    "CBCBC8": "darkred",
    "FF7800": "darkred",
    }
    def color_name(color_code):
      return COLORS[color_code]
    df1["Rating color name"] = df1.loc[:, "Rating color"].apply(color_name)

    #Renomear as colunas do DataFrame
    def rename_columns(dataframe):
      df = dataframe.copy()
      title = lambda x: inflection.titleize(x)
      snakecase = lambda x: inflection.underscore(x)
      spaces = lambda x: x.replace(" ", "")
      cols_old = list(df.columns)
      cols_old = list(map(title, cols_old))
      cols_old = list(map(spaces, cols_old))
      cols_new = list(map(snakecase, cols_old))
      df.columns = cols_new
      return df
    df1 = rename_columns(df1)

    #Categorizando restaurantes
    df1["cuisines"] = df1.loc[:, "cuisines"].apply(lambda x: x.split(",")[0])
    
    return df1

def country_res(df1):
    colunas = ['country_name', 'restaurant_id']
    df_aux = df1.loc[:, colunas].groupby('country_name').count().sort_values(by='restaurant_id', ascending=False).reset_index()
    fig = px.bar( df_aux, x='country_name', y='restaurant_id', text_auto='.2s',  labels={'country_name':'País', 'restaurant_id':'Quantidade de Restaurantes'})
    fig.update_layout(
    title={
        'text': 'Quantidade de restaurantes registrados por País',
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})
    
    return fig

def country_city(df1): 
    colunas = ['country_name', 'city']
    df_aux = df1.loc[:, colunas].groupby('country_name').nunique().sort_values(by='city', ascending=False).reset_index()
    fig = px.bar( df_aux, x='country_name', y='city', text_auto='.1s',  labels={'country_name':'País', 'city':'Quantidade de Cidades'})
    fig.update_layout(
    title={
        'text': 'Quantidade de Cidades por País',
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})
    return fig

def country_votes(df1): 
    colunas = ['country_name', 'votes']
    df_aux = df1.loc[:, colunas].groupby('country_name').mean().sort_values(by='votes', ascending=False).reset_index()
    fig = px.bar( df_aux, x='country_name', y='votes', text_auto='.2s',  labels={'country_name':'País', 'votes':'Quantidade de avaliações'})
    fig.update_layout(
    title={
        'text': 'Média de Avaliações feitas por País',
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})
    return fig

def country_two(df1): 
    colunas = ['country_name', 'average_cost_for_two']
    df_aux = df1.loc[:, colunas].groupby('country_name').mean().sort_values(by='average_cost_for_two', ascending=False).reset_index()
    fig = px.bar( df_aux, x='country_name', y='average_cost_for_two')
    fig = px.bar( df_aux, x='country_name', y='average_cost_for_two', text_auto='.6s',  labels={'country_name':'País', 'average_cost_for_two':'Preço de prato para duas pessoas'})
    fig.update_layout(
    title={
        'text': 'Média de preço de um prato para duas pessoas por País',
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})
    return fig

#Import Dataset
df = pd.read_csv( 'dataset/zomato.csv')

#Limpando os dados
df1 = clean_code(df)
df2 = df1.copy()

#==========================================
#Barra Lateral no Streamlit
#==========================================


st.sidebar.markdown('### Filtros')
country_options = st.sidebar.multiselect(
    'Escolha os Paises que Deseja visualizar os Restaurantes',
    ['India', 'Australia', 'Brazil', 'Canada', 'Indonesia', 'New Zeland','Philippines','Qatar', 'Singapure','South Africa', 'Sri Lanka','Turkey', 'United Arab Emirates','England', 'United States of America'],
    default = ['Brazil', 'England', 'Qatar', 'South Africa', 'Canada', 'Australia' ])



st.sidebar.markdown('### Power by Marcelo Silva')

#Filtro de Países
linhas_selecionadas = df1['country_name'].isin(country_options)
df1 = df1.loc[linhas_selecionadas, :]

#==========================================
#Layout no Streamlit
#==========================================

st.markdown('# 🌎 Visão Países')

with st.container():
    #Quantidade de restaurantes por países
    fig = country_res(df1)
    st.plotly_chart(fig, use_container_width=True)

with st.container():
    #Quantidade de cidades por países
    fig = country_city(df1)
    st.plotly_chart(fig, use_container_width=True)
    
with st.container():
    col1,col2 = st.columns(2)
    with col1:
        #media de avaliação por país
        fig = country_votes(df1)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        #media de preco de um prato para 2
        fig = country_two(df1)
        st.plotly_chart(fig, use_container_width=True)
