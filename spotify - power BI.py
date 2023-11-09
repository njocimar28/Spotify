import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials

### Obter as músicas ouvidas recentemente
def get_recently_played():

    # Carrega as credenciais do Spotify
    with open('SuasCredenciais.txt', 'r') as file:
        lines = file.readlines()
        for line in lines:
            key, value = line.strip().split(': ')
            if key == 'CLIENT_ID':
                client_id = value
            elif key == 'CLIENT_SECRET':
                client_secret = value
            elif key == 'REDIRECT_URI':
                redirect_uri = value

    # Crie um objeto SpotifyOAuth
    auth = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope='user-library-read user-read-recently-played user-top-read'
    )

    # Obtenha token de acesso
    token_info = auth.get_access_token()
    token = token_info['access_token']

    # Crie um objeto Spotify
    sp = spotipy.Spotify(auth=token)

    # Obter as músicas ouvidas recentemente
    recently_played = sp.current_user_recently_played()

    # Extrair os dados relevantes
    tracks_data = []

    for track in recently_played['items']:
        track_info = {
            'Nome da Música': track['track']['name'],
            'Artista': track['track']['artists'][0]['name']
        }
        tracks_data.append(track_info)

    # Criar DataFrame
    df_recently_played = pd.DataFrame(tracks_data)
    
    # Obter as músicas mais ouvidas
    top_tracks = sp.current_user_top_tracks(limit=50, offset=0, time_range='short_term')

    # Obter os artistas mais ouvidos
    top_artists = sp.current_user_top_artists(limit=50, offset=0, time_range='short_term')

    # Criar DataFrames para as músicas e artistas mais ouvidos
    df_top_tracks = pd.DataFrame(top_tracks['items'])
    df_top_artists = pd.DataFrame(top_artists['items'])

    # Retornar os DataFrames para o Power BI
    return df_recently_played, df_top_tracks, df_top_artists

# Chamar a função get_recently_played() e retornar os DataFrames
df_recently_played, df_top_tracks, df_top_artists = get_recently_played()

### Processar df_top_tracks
def processar_df(df):
    # Lista de colunas para expandir
    colunas_para_expandir = ['album', 'external_ids', 'external_urls']

    for coluna in colunas_para_expandir:
        df = pd.concat([df, df[coluna].apply(pd.Series).add_suffix(f'_{coluna}')], axis=1)

    # Obter o primeiro artista da lista
    df['first_artist_name'] = df['artists'].apply(lambda x: x[0]['name'])

    # Lista de colunas para expandir após o primeiro tratamento
    colunas_album_para_expandir = ['artists_album', 'external_urls_album', 'images_album']

    for coluna in colunas_album_para_expandir:
        df = pd.concat([df, df[coluna].apply(pd.Series).add_suffix(f'_{coluna}')], axis=1)

    # Expandir a coluna "images_album" em colunas individuais e adicionar sufixo "_image"
    df = pd.concat([df, df['0_images_album'].apply(pd.Series).add_suffix('_image')], axis=1)

    # Lista de colunas para excluir
    colunas_para_excluir = [
        'album',
        'external_ids',
        'external_urls',
        'artists',
        'artists_album',
        'external_urls_album',
        'images_album',
        'available_markets', 
        'explicit', 
        'href', 
        'is_local', 
        'album_type_album', 
        'available_markets_album', 
        'href_album', 
        'release_date_precision_album', 
        'type_album', 
        '0_images_album', 
        '1_images_album', 
        '2_images_album', 
        'height_image',
        '0_artists_album', 
        'width_image'
    ]

    # Excluir colunas que não serão utilizadas
    df = df.drop(columns=colunas_para_excluir)

    return df

# Usar a função com o DataFrame df_top_tracks
df_top_tracks = processar_df(df_top_tracks)

### Processar df_top_artists
def processar_top_artists(df_top_artists):
    # Lista de colunas para expandir
    colunas_para_expandir = ['images', 'external_urls']

    for coluna in colunas_para_expandir:
        df_top_artists = pd.concat([df_top_artists, df_top_artists[coluna].apply(pd.Series).add_suffix(f'_{coluna}')], axis=1)

    # Expandir a coluna com as imagens
    df_top_artists = pd.concat([df_top_artists, df_top_artists['0_images'].apply(pd.Series).add_suffix('_image')], axis=1)

    # Lista de colunas para excluir
    colunas_para_excluir = [
        'external_urls',
        'genres',
        'followers',
        'images',
        '0_images',
        '1_images',
        '2_images', 
        'height_image',
        'width_image'
    ]

    # Excluir colunas que não serão utilizadas
    df_top_artists = df_top_artists.drop(columns=colunas_para_excluir)

    return df_top_artists

# Usar a função com o DataFrame df_top_artists
df_top_artists = processar_top_artists(df_top_artists)

