import pandas as pd
import inflection as inflection
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static
import locale
from folium.plugins import MarkerCluster

st.set_page_config(
    page_title="Main page",
    layout = "wide",
    page_icon="📊",
)
print('inflection',inflection.__version__)
#print('locale',locale.__version__)


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

def country_maps(df1):
    colunas = ['restaurant_name','latitude','longitude', 'average_cost_for_two', 'cuisines','currency', 'aggregate_rating', 'rating_color_name']
    data_plot = df1.loc[:, colunas].groupby( ['restaurant_name', 'cuisines', 'rating_color_name' ,'currency']).mean().reset_index()
    map_ = folium.Map( zoom_start=11 )
    marker_cluster = MarkerCluster().add_to(map_)
    for index, location_info in data_plot.iterrows():
        html = f''' <b> {location_info['restaurant_name']} </b>
        <br><br> 
                Price for two: {location_info['currency']} {location_info['average_cost_for_two']} <br>
                Type: {location_info['cuisines']} <br>
                Aggragate Rating: {location_info['aggregate_rating']}/5.0 '''
        iframe = folium.IFrame(html,width=400,height=100)
        popup = folium.Popup(iframe,max_width=300)
        
        folium.Marker( [location_info['latitude'],
                      location_info['longitude']],
                      popup=popup,
                    icon=folium.Icon(color = location_info['rating_color_name'], icon="home")).add_to(marker_cluster)
    #st.dataframe(data_plot.head(5))
    folium_static(map_, width=1024 , height=600)


#Import Dataset
df = pd.read_csv( 'dataset/zomato.csv')

#Limpando os dados
df1 = clean_code(df)
df2 = df1.copy()

#==========================================
#Barra Lateral no Streamlit
#==========================================

st.sidebar.markdown('# Fome Zero')
image = Image.open( 'logo.png' )
st.sidebar.image( image, width=60)


st.sidebar.markdown('### Filtros')
country_options = st.sidebar.multiselect(
    'Escolha os Paises que Deseja visualizar os Restaurantes',
    ['India', 'Australia', 'Brazil', 'Canada', 'Indonesia', 'New Zeland','Philippines','Qatar', 'Singapure','South Africa', 'Sri Lanka','Turkey', 'United Arab Emirates','England', 'United States of America'],
    default = ['Brazil', 'England', 'Qatar', 'South Africa', 'Canada', 'Australia' ])

st.sidebar.markdown('### Dados Tratados')
def convert_df(df):
    return df.to_csv().encode('utf-8')
csv = convert_df(df1)
st.sidebar.download_button(
    label="Download",
    data=csv,
    file_name='zomato.csv',
    mime='text/csv',
)

st.sidebar.markdown('### Power by Marcelo Silva')

#Filtro de Trânsito
linhas_selecionadas = df1['country_name'].isin(country_options)
df2 = df2.loc[linhas_selecionadas, :]


#==========================================
#Layout no Streamlit
#==========================================


with st.container():
    st.markdown('# Fome Zero!')
    st.markdown('### O Melhor lugar para encontrar seu mais novo restaurante favorito!')
    st.markdown('##### Temos as seguintes marcas dentro da nossa plataforma: ')
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        #Quantidade de restaurantes
        qt_restaurantes = df1['restaurant_id'].nunique()
        st.metric('Restaurantes cadastrados',qt_restaurantes)

    with col2:
        #Quantidade de paises
        qt_paises = df1['country_code'].nunique()
        st.metric('Países cadastrados',qt_paises)

    with col3:
        #Quantidade de cidades
        qt_cidades = df1['city'].nunique()
        st.metric('Cidades cadastradas',qt_cidades)

    with col4:
        locale.setlocale(locale.LC_ALL, '')
        #Avaliações feitas na plataforma
        qt_aval = df1['votes'].sum()
        qt_aval = '{:n}'.format(qt_aval).replace(',', '.')
        st.metric('Avaliações feitas na plataforma',qt_aval)

    with col5:
        #Tipos de culinária
        qt_cul = df1['cuisines'].nunique()
        st.metric('Tipos de culinária',qt_cul)
        
with st.container():
    #A localização central de cada cidade por tipo de tráfego.
    country_maps(df2)
