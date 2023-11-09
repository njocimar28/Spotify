import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth

def obter_discografia(id_artist):
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

    auth = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope='playlist-read-private'
    )

    token_info = auth.get_access_token()
    token = token_info['access_token']

    sp = spotipy.Spotify(auth=token)

    # Obter o artista
    artist = sp.artist(artist_id=id_artist)

    # Obter a imagem do artista
    df_imagem_artist = pd.DataFrame(artist['images'])
    df_imagem_artist = df_imagem_artist.query("height == 640")

    df_imagem_artist.rename(columns={'url': 'Imagem do artista'}, inplace=True)

    # Criar o DataFrame do artista
    df_artist = pd.DataFrame({'Artista': [artist['name']], 'id_artista': [artist['id']]})

    # Concatenar os DataFrames
    df_concat_artist = pd.concat([df_artist, df_imagem_artist['Imagem do artista']], axis=1)

    ### Obter os dados dos Albuns
    album = sp.artist_albums(artist_id=id_artist)

    df_album_items = pd.DataFrame(album['items'])
    df_album = df_album_items[['id', 'name', 'release_date', 'total_tracks']]

    lista_album = df_album['id'].to_list()

    df_imagem_album = pd.DataFrame(df_album_items['images'].apply(pd.Series).add_suffix('_album'))
    df_imagem_album = pd.DataFrame(df_imagem_album['0_album'].apply(pd.Series))

    df_album_final = pd.concat([df_album, df_imagem_album['url']], axis=1)
    df_album_final = df_album_final.add_suffix('_Album')

    df_intermediario = df_album_final.assign(**df_concat_artist.iloc[0])

    lista_musica_final = []
    df_tracks = pd.DataFrame()

    for album_id in lista_album:
        tracks = sp.album_tracks(album_id=album_id)

        df_tracks_items = pd.DataFrame(tracks['items'])
        df_tracks_items = df_tracks_items.add_suffix('_tracks')
    
        df_tracks_items['id_Album'] = album_id

        df_tracks = pd.concat([df_tracks, df_tracks_items])

    colunas_tracks = ['duration_ms_tracks',
                      'id_tracks',
                      'name_tracks',
                      'id_Album'
    ]

    df_tracks_final = df_tracks[colunas_tracks]

    df_discografia = pd.merge(df_intermediario, df_tracks_final, on='id_Album', how='inner')
    
    df_discografia['duração da Música'] = df_discografia['duration_ms_tracks'] / 60000
    
    # Extrair os primeiros 4 caracteres (o ano) da coluna 'release_date_Album'
    df_discografia['ano_lancamento'] = df_discografia['release_date_Album'].str[:4]

    # Converta a coluna para tipo inteiro (int)
    df_discografia['ano_lancamento'] = df_discografia['ano_lancamento'].astype(int)

    
    return df_discografia

lista_artista = [
    '16oZKvXb6WkQlVAjwo2Wbg',
    '0L8ExT028jH3ddEcZwqJJ5',
    '7jdFEYD2LTYjfwxOdlVjmc',
    '7Ln80lUS6He07XvHI8qqHH',
    '1WgXqy2Dd70QQOU7Ay074N'   
]

df_discografia = pd.DataFrame()

for artista in lista_artista:
    df_artista = obter_discografia(artista)
    df_discografia = pd.concat([df_discografia, df_artista])