import pandas as pd
import inflection as inflection
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static
import plotly.express as px

st.set_page_config(
    page_title="Cuisines",
    layout = "wide",
    page_icon="🍽️",
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

def res_aggr(df1, number):
    colunas = ['restaurant_name','cuisines', 'aggregate_rating', 'country_name', 'city','currency', 'average_cost_for_two']
    linhas_selecionadas = df1['cuisines'] == 'Italian'
    df_aux = df1.loc[linhas_selecionadas, colunas].groupby(['restaurant_name', 'country_name', 'city', 'currency']).mean().sort_values(by='aggregate_rating',ascending=False).reset_index()
    restaurant_name = df_aux.iloc[number,0]
    restaurant_country = df_aux.iloc[number,1]
    restaurant_city = df_aux.iloc[number,2]
    restaurant_currency = df_aux.iloc[number,3]
    restaurant_aggr = df_aux.iloc[number,4]
    restaurant_two = df_aux.iloc[number,5]
    print(df_aux)
    return restaurant_name, restaurant_country, restaurant_city, restaurant_currency, restaurant_aggr, restaurant_two

def res_top(df1, qt_slider):
    colunas = ['restaurant_id', 'restaurant_name', 'country_name', 'city', 'cuisines', 'average_cost_for_two', 'aggregate_rating', 'votes']    
    df_aux = df1.loc[:, colunas].groupby(['restaurant_id','restaurant_name', 'country_name', 'city',  'cuisines']).mean().sort_values(by='aggregate_rating',ascending=False).reset_index()
    df_aux = df_aux.head(qt_slider)
    return df_aux

def cus_aggr(df1, qt_slider, option):
    colunas = ['cuisines', 'aggregate_rating']
    df_aux = df1.loc[: , colunas].groupby('cuisines').mean().sort_values(by='aggregate_rating', ascending=option).reset_index()
    df_aux = df_aux.head(qt_slider)
    if option == False:
        fig = px.bar( df_aux, x='cuisines', y='aggregate_rating', text_auto='.2s',  labels={'cuisines':'Tipo de Culinária', 'aggregate_rating':'Média da Avaliação Média'})
        fig.update_layout(
        title={
            'text': 'Top 10 Melhores tipos de Culinária',
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
    else:
        fig = px.bar( df_aux, x='cuisines', y='aggregate_rating', text_auto='.3s',  labels={'cuisines':'Tipo de Culinária', 'aggregate_rating':'Média da Avaliação Média'})
        fig.update_layout(
        title={
            'text': 'Top 10 Piores tipos de Culinária',
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
    
    return fig

    return fig

#Import Dataset
df = pd.read_csv( 'dataset/zomato.csv')

#Limpando os dados
df1 = clean_code(df)
df2 = df1.copy()
df4 = df1.copy()

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

qt_slider = st.sidebar.slider(
    'Selecione a quantidade de Restaurantes que deseja visualizar',
    value = 8,
    min_value = 1,
    max_value = 20)

cuisines_options = st.sidebar.multiselect(
    'Escolha os Tipos de culinária',
    ['Italian', 'European', 'Filipino', 'American', 'Korean', 'Pizza',
       'Taiwanese', 'Japanese', 'Coffee', 'Chinese', 'Seafood',
       'Singaporean', 'Vietnamese', 'Latin American', 'Healthy Food',
       'Cafe', 'Fast Food', 'Brazilian', 'Argentine', 'Arabian', 'Bakery',
       'Tex-Mex', 'Bar Food', 'International', 'French', 'Steak',
       'German', 'Sushi', 'Grill', 'Peruvian', 'North Eastern',
       'Ice Cream', 'Burger', 'Mexican', 'Vegetarian', 'Contemporary',
       'Desserts', 'Juices', 'Beverages', 'Spanish', 'Thai', 'Indian',
       'Mineira', 'BBQ', 'Mongolian', 'Portuguese', 'Greek', 'Asian',
       'Author', 'Gourmet Fast Food', 'Lebanese', 'Modern Australian',
       'African', 'Coffee and Tea', 'Australian', 'Middle Eastern',
       'Malaysian', 'Tapas', 'New American', 'Pub Food', 'Southern',
       'Diner', 'Donuts', 'Southwestern', 'Sandwich', 'Irish',
       'Mediterranean', 'Cafe Food', 'Korean BBQ', 'Fusion', 'Canadian',
       'Breakfast', 'Cajun', 'New Mexican', 'Belgian', 'Cuban', 'Taco',
       'Caribbean', 'Polish', 'Deli', 'British', 'California', 'Others',
       'Eastern European', 'Creole', 'Ramen', 'Ukrainian', 'Hawaiian',
       'Patisserie', 'Yum Cha', 'Pacific Northwest', 'Tea', 'Moroccan',
       'Burmese', 'Dim Sum', 'Crepes', 'Fish and Chips', 'Russian',
       'Continental', 'South Indian', 'North Indian', 'Salad',
       'Finger Food', 'Mandi', 'Turkish', 'Kerala', 'Pakistani',
       'Biryani', 'Street Food', 'Nepalese', 'Goan', 'Iranian', 'Mughlai',
       'Rajasthani', 'Mithai', 'Maharashtrian', 'Gujarati', 'Rolls',
       'Momos', 'Parsi', 'Modern Indian', 'Andhra', 'Tibetan', 'Kebab',
       'Chettinad', 'Bengali', 'Assamese', 'Naga', 'Hyderabadi', 'Awadhi',
       'Afghan', 'Lucknowi', 'Charcoal Chicken', 'Mangalorean',
       'Egyptian', 'Malwani', 'Armenian', 'Roast Chicken', 'Indonesian',
       'Western', 'Dimsum', 'Sunda', 'Kiwi', 'Asian Fusion', 'Pan Asian',
       'Balti', 'Scottish', 'Cantonese', 'Sri Lankan', 'Khaleeji',
       'South African', 'Drinks Only', 'Durban', 'World Cuisine',
       'Izgara', 'Home-made', 'Giblets', 'Fresh Fish', 'Restaurant Cafe',
       'Kumpir', 'Döner', 'Turkish Pizza', 'Ottoman', 'Old Turkish Bars',
       'Kokoreç'],
    default = ['Home-made', 'BBQ', 'Japanese', 'Brazilian', 'Arabian', 'American', 'Italian' ])

st.sidebar.markdown('### Power by Marcelo Silva')

#Filtro de países
linhas_selecionadas = df1['country_name'].isin(country_options)
df1 = df1.loc[linhas_selecionadas, :]

#Filtro Quantidade
#df1 = df1.head(qt_slider)

#Filtro de culinárias
linhas_selecionadas2 = df1['cuisines'].isin(cuisines_options)
df1 = df1.loc[linhas_selecionadas2, :]


#==========================================
#Layout no Streamlit
#==========================================

st.markdown('# 🍽️ Visão Tipos de Culinária')

with st.container():
    st.markdown('### Melhores Restaurantes dos Principais tipos Culinários')
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        restaurant_name, restaurant_country, restaurant_city, restaurant_currency, restaurant_aggr, restaurant_two = res_aggr(df2,0)
        st.metric(f'Italiana: {restaurant_name}', f'{restaurant_aggr}/5.0', help = f'País: {restaurant_country}  \n Cidade: {restaurant_city}    \n Preço para dois: {restaurant_two} {restaurant_currency}')

    with col2:
        restaurant_name, restaurant_country, restaurant_city, restaurant_currency, restaurant_aggr, restaurant_two = res_aggr(df2,1)
        st.metric(f'Italiana: {restaurant_name}', f'{restaurant_aggr}/5.0', help = f'País: {restaurant_country}  \n Cidade: {restaurant_city}    \n Preço para dois: {restaurant_two} {restaurant_currency}')
        
    with col3:
        restaurant_name, restaurant_country, restaurant_city, restaurant_currency, restaurant_aggr, restaurant_two = res_aggr(df2,2)
        st.metric(f'Italiana: {restaurant_name}', f'{restaurant_aggr}/5.0', help = f'País: {restaurant_country}  \n Cidade: {restaurant_city}    \n Preço para dois: {restaurant_two} {restaurant_currency}')
        
    with col4:
        restaurant_name, restaurant_country, restaurant_city, restaurant_currency, restaurant_aggr, restaurant_two = res_aggr(df2,3)
        st.metric(f'Italiana: {restaurant_name}', f'{restaurant_aggr}/5.0', help = f'País: {restaurant_country}  \n Cidade: {restaurant_city}    \n Preço para dois: {restaurant_two} {restaurant_currency}')
        
    with col5:
        restaurant_name, restaurant_country, restaurant_city, restaurant_currency, restaurant_aggr, restaurant_two = res_aggr(df2,4)
        st.metric(f'Italiana: {restaurant_name}', f'{restaurant_aggr}/5.0', help = f'País: {restaurant_country}  \n Cidade: {restaurant_city}    \n Preço para dois: {restaurant_two} {restaurant_currency}')
        
with st.container():
    st.markdown(f'## Top {qt_slider} Restaurantes')
    df3 = res_top(df1, qt_slider)
    st.dataframe(df3)
    
with st.container():
    col1,col2 = st.columns(2)
    with col1:
        fig = cus_aggr(df4, qt_slider, option=False)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = cus_aggr(df4, qt_slider, option=True)
        st.plotly_chart(fig, use_container_width=True)

