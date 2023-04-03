import pandas as pd
import inflection as inflection
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static
import plotly.express as px

st.set_page_config(
    page_title="Cities",
    layout = "wide",
    page_icon=":cityscape:",
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

def city_res(df1):
    colunas = ['city', 'restaurant_id', 'country_name']
    df_aux = df1.loc[:, colunas].groupby(['city', 'country_name']).count().sort_values(by='restaurant_id', ascending=False).reset_index()
    df_aux = df_aux.head(10)
    fig = px.bar( df_aux, x='city', y='restaurant_id', text_auto='.4s', color="country_name",  labels={'city':'Cidade', 'restaurant_id':'Quantidade de Restaurantes' , 'country_name':'País'})
    fig.update_layout(
    title={
        'text': 'Top 10 Cidades com mais restaurantes na base de dados',
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})
    return fig

def city_cus(df1): 
    colunas = ['cuisines', 'city', 'country_name']
    df_aux = df1.loc[:, colunas].groupby(['city', 'country_name']).nunique().sort_values(by='cuisines', ascending=False).reset_index()
    df_aux = df_aux.head(10)
    fig = px.bar( df_aux, x='city', y='cuisines', text_auto='.2s', color="country_name",  labels={'city':'Cidade', 'cuisines':'Quantidade de Tipos Culinários' , 'country_name':'País'})
    fig.update_layout(
    title={
        'text': 'Top 10 Cidades com mais restaurantes com Tipos Culinários distintos',
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})
    return fig

def city_rat(df1): 
    colunas = ['city', 'restaurant_id', 'aggregate_rating', 'country_name']
    linhas_selecionadas = df1['aggregate_rating'] > 4
    df_aux = df1.loc[linhas_selecionadas, colunas].groupby(['city', 'country_name']).count().sort_values(by='restaurant_id',ascending=False).reset_index()
    df_aux = df_aux.head(7)
    fig = px.bar( df_aux, x='city', y='aggregate_rating', text_auto='.4s', color="country_name",  labels={'city':'Cidade', 'aggregate_rating':'Quantidade de Avaliações', 'country_name':'País' })
    fig.update_layout(
    title={
        'text': 'Top 7 Cidades com Restaurantes com média de avaliação acima de 4',
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})
    return fig

def city_rat2(df1): 
    colunas = ['city', 'restaurant_id', 'aggregate_rating', 'country_name']
    linhas_selecionadas = df1['aggregate_rating'] < 2.5
    df_aux = df1.loc[linhas_selecionadas, colunas].groupby(['city', 'country_name']).count().sort_values(by='restaurant_id',ascending=False).reset_index()
    df_aux = df_aux.head(7)
    fig = px.bar( df_aux, x='city', y='aggregate_rating', text_auto='.4s', color="country_name",  labels={'city':'Cidade', 'aggregate_rating':'Quantidade de Avaliações', 'country_name':'País' })
    fig.update_layout(
    title={
        'text': 'Top 7 Cidades com Restaurantes com média de avaliação abaixo de 2.5',
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

image = Image.open( 'logo.png' )
st.sidebar.image( image, width=60)
st.sidebar.markdown('# Fome zero')

st.sidebar.markdown('### Filtros')
country_options = st.sidebar.multiselect(
    'Escolha os Paises que Deseja visualizar os Restaurantes',
    ['India', 'Australia', 'Brazil', 'Canada', 'Indonesia', 'New Zeland','Philippines','Qatar', 'Singapure','South Africa', 'Sri Lanka','Turkey', 'United Arab Emirates','England', 'United States of America'],
    default = ['Brazil', 'England', 'Qatar', 'South Africa', 'Canada', 'Australia' ])

st.sidebar.markdown('### Power by Marcelo Silva')

#Filtro de Trânsito
linhas_selecionadas = df1['country_name'].isin(country_options)
df1 = df1.loc[linhas_selecionadas, :]

#==========================================
#Layout no Streamlit
#==========================================

st.markdown('# :cityscape: Visão Cidades')

with st.container():
    #Quantidade de restaurantes por cidades
    fig = city_res(df1)
    st.plotly_chart(fig, use_container_width=True)

with st.container():
    col1,col2 = st.columns(2)
    with col1:
        #media de avaliação por cidades > 4
        fig = city_rat(df1)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        #media de avaliação por cidades < 2.5
        fig = city_rat2(df1)
        st.plotly_chart(fig, use_container_width=True)
        
with st.container():
    #Quantidade de restaurantes por cidades
    fig = city_cus(df1)
    st.plotly_chart(fig, use_container_width=True)