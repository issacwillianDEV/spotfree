import base64
import json
import functools
import io
import itertools
import json
import re
import time
import os
from kivy.properties import DictProperty
from kivy.utils import platform, get_color_from_hex
import threading
import pygame
from kivy.uix.image import AsyncImage
from kivy.clock import Clock
from kivy.app import App
from kivy.clock import mainthread
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.button import MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen

import random
import asyncio

from kivymd.utils.fitimage import FitImage
from pytube import YouTube
from youtubesearchpython import SearchVideos

from media_player import player2, Uri2, PythonActivity2, MediaPlayer2

from pydub import AudioSegment

import requests
from bs4 import BeautifulSoup

import dns.resolver

dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = ['8.8.8.8']

import os, ssl

if platform == 'android':
    from android.runnable import run_on_ui_thread
    from jnius import autoclass

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context


class Carregamento(MDScreen):
    pass


class Musicas(MDScreen):
    mudanca_faixa_musica = False
    stop_threads = False
    tempo_musica = None
    numero_musica = None

    @mainthread
    def play_modify(self, n_audio, length):
        print(f'numero do audio: {n_audio}')
        if int(n_audio) < int(length):
            print('entrou aqui!!')
            self.manager.get_screen("musicas").ids.nome_musica.text = self.dynamic_ids[f"titulo{int(n_audio) + 1}"].text
            self.manager.get_screen("musicas").ids.nome_artista.text = self.dynamic_ids[
                f"artista{int(n_audio) + 1}"].text
            self.manager.get_screen("musicas").ids.image_musica.source = self.dynamic_ids[
                f"imagem{int(n_audio) + 1}"].source
        elif int(n_audio) == int(length):
            self.manager.get_screen("musicas").ids.nome_musica.text = self.dynamic_ids[f"titulo{1}"].text
            self.manager.get_screen("musicas").ids.nome_artista.text = self.dynamic_ids[f"artista{1}"].text
            self.manager.get_screen("musicas").ids.image_musica.source = self.dynamic_ids[f"imagem{1}"].source

        self.dynamic_ids[f"botaoplay{int(n_audio)}"].icon = "play"
        self.dynamic_ids[f"botaoplay{int(n_audio) + 1}"].icon = "equalizer"

        Inicio.numero_musica = f"{int(n_audio) + 1}"

    def thd_play(self, titulo, artista, n_audio, source, length):
        Inicio.position = 0
        progress_bar_valor_novo = 0
        Inicio.contadorplay = 1
        pygame.mixer.music.unload()  # descarrega o arquivo de som
        print(Inicio.url_videos)
        Inicio.lista_arrastar = []
        print(f'Tamanho da lista: {Inicio.lista_arrastar}')

        texto = f"{titulo} {artista}"
        titulo_formatado = re.sub(r'[^a-zA-Z0-9_]', '_', texto)

        print(titulo_formatado)

        if os.path.exists(f"som/{titulo_formatado}.ogg") and os.path.isfile(f"som/{titulo_formatado}.ogg"):
            self.manager.get_screen("inicio").ids.scroll.pos_hint = {'center_x': 0.53, 'top': 0.23}

            self.manager.get_screen("carregamento").ids.progress_carregamento.value = 30
            self.manager.get_screen("carregamento").ids.label_progress.text = f'30%'

            self.manager.get_screen("carregamento").ids.progress_carregamento.value = 60
            self.manager.get_screen("carregamento").ids.label_progress.text = f'60%'

            self.manager.get_screen("carregamento").ids.progress_carregamento.value = 80
            self.manager.get_screen("carregamento").ids.label_progress.text = f'80%'

            self.manager.get_screen("inicio").ids.play.icon = 'pause'
            self.manager.get_screen("musicas").ids.play.icon = 'pause'
            self.manager.get_screen("pesquisar").ids.play.icon = 'pause'
            self.manager.get_screen("playlist").ids.play.icon = 'pause'

            # obtém o caminho do diretório atual
            sourceFileDir = os.path.dirname(os.path.abspath(__file__))

            # obtém o caminho da pasta "som"
            somDir = os.path.join(sourceFileDir, "som")

            # obtém o caminho do arquivo "play1.ogg"
            playFile = os.path.join(somDir, f"{titulo_formatado}.ogg")

            Uri = Uri2
            PythonActivity = PythonActivity2
            player = player2

            if platform == 'android':
                if player.isPlaying():
                    player.stop()
                    player.reset()

                uri = Uri.parse('file://' + playFile)
                player.reset()
                player.setDataSource(PythonActivity.mActivity, uri)

                # Prepara o MediaPlayer para reprodução
                player.prepare()
                # Inicia a reprodução do áudio
                """position_ms = 50 * 1000
                player.seekTo(position_ms)"""

                # Obtém a duração do arquivo de áudio em milissegundos
                duration_ms = player.getDuration()

                # Converte a duração para segundos
                duration = duration_ms / 1000
                Inicio.tempo_musica = duration

                print(f"duração {duration}")


            else:
                self.sound = pygame.mixer.music.load(playFile)
                duration = pygame.mixer.Sound(playFile).get_length()
                Inicio.tempo_musica = duration

            if Inicio.position == 0:
                self.manager.get_screen("carregamento").ids.progress_carregamento.value = 100
                self.manager.get_screen("carregamento").ids.label_progress.text = f'100%'
                self.voltar_inicio()

                if platform == 'android':
                    player.start()
                else:
                    pygame.mixer.music.play()

            else:
                self.manager.get_screen("carregamento").ids.progress_carregamento.value = 100
                self.manager.get_screen("carregamento").ids.label_progress.text = f'100%'
                self.voltar_inicio()
                if platform == 'android':
                    player.seekTo(Inicio.position)
                    player.start()
                else:
                    pygame.mixer.music.play()
                    pygame.mixer.music.set_pos(Inicio.position)
                    print(Inicio.position)

            # print(duration)

            try:
                self.progress_bar_update.cancel()
            except:
                pass

            Inicio.position = -1
            Inicio.numero_musica = n_audio
            Inicio.contador_lenght = length

            def update_progress():
                while True:
                    if Musicas.mudanca_faixa_musica:
                        break
                    print(Inicio.numero_musica)
                    time.sleep(1)
                    if Inicio.position >= int(Inicio.tempo_musica):
                        numero = int(Inicio.numero_musica)

                        if int(Inicio.numero_musica) < int(Inicio.contador_lenght):
                            titulo1 = self.dynamic_ids[f"titulo{int(Inicio.numero_musica) + 1}"].text
                            artista1 = self.dynamic_ids[f"artista{int(Inicio.numero_musica) + 1}"].text
                            imagem = self.dynamic_ids[f"imagem{int(Inicio.numero_musica) + 1}"].source
                        else:
                            titulo1 = self.dynamic_ids[f"titulo1"].text
                            artista1 = self.dynamic_ids[f"artista1"].text
                            imagem = self.dynamic_ids[f"imagem1"].source

                        Musicas.play(self, titulo1, artista1, f"{int(Inicio.numero_musica) + 1}", imagem,
                                     Inicio.contador_lenght)
                        Musicas.play_modify(self, Inicio.numero_musica, Inicio.contador_lenght)

            if Inicio.stop_threads == False:
                Inicio.progress_bar_update = threading.Thread(target=update_progress).start()
            if Inicio.stop_threads == False:
                Inicio.progress_bar_update = threading.Thread(target=Musicas.update_progress, args=(self, None)).start()



        else:
            print("O arquivo não existe na pasta raiz do projeto.")

            self.manager.get_screen("inicio").ids.scroll.pos_hint = {'center_x': 0.53, 'top': 0.23}

            self.manager.get_screen("carregamento").ids.progress_carregamento.value = 30
            self.manager.get_screen("carregamento").ids.label_progress.text = f'30%'

            def download_youtube_video(video_url, titulo='playwebm'):
                while True:
                    try:
                        # Cria uma instância do objeto YouTube
                        video = YouTube(video_url)

                        # Seleciona o formato de áudio desejado (webm ou m4a)
                        audio_format = "webm"  # ou "m4a"

                        # Seleciona a faixa de áudio com a maior qualidade disponível
                        audio = video.streams.filter(only_audio=True, file_extension=audio_format).order_by(
                            'abr').desc().first()

                        # Baixa o arquivo de áudio como bytes
                        audio_bytes = io.BytesIO()
                        audio.stream_to_buffer(audio_bytes)

                        # Decodifica a representação em base64 para obter os dados binários do arquivo de áudio
                        audio_data = audio_bytes.getvalue()

                        # Cria o diretório 'som' se ele não existir
                        if not os.path.exists('som'):
                            os.makedirs('som')

                        # Salva o arquivo de áudio decodificado em formato webm na pasta 'som'
                        with open(f"som/{titulo}.webm", "wb") as f:
                            f.write(audio_data)

                        # Imprime a mensagem de conclusão
                        print("Download concluído e arquivo salvo em som/")
                        break
                    except:
                        print('Ocorreu uma excessão ao fazer Download, iniciando novamente!')

            def buscar_video(busca):
                results = SearchVideos(busca, offset=1, mode="json", max_results=1)
                info = json.loads(results.result())["search_result"][0]
                video_url = info["link"]
                thumbnail_url = info['thumbnails'][2]
                title = info["title"]
                return video_url

            urlvideo = buscar_video(f"{titulo} - {artista}")
            download_youtube_video(urlvideo, f'playwebm')
            print('FEZ O DOWNLOAD')

            self.manager.get_screen("carregamento").ids.progress_carregamento.value = 60
            self.manager.get_screen("carregamento").ids.label_progress.text = f'60%'

            def converter_audio_webm_para_ogg(arquivo_webm, arquivo_ogg):
                if platform == 'android':
                    # Define o comando de conversão
                    comando = f"-i {arquivo_webm} -c:v libx264 -c:a vorbis -strict -2 -q:a 4 -y {arquivo_ogg}"

                    # Executa o comando ffmpeg para converter o arquivo
                    Inicio.FFMPEG.Run(comando)

                else:
                    import subprocess
                    comando = f'ffmpeg -i {arquivo_webm} -c:v libx264 -c:a vorbis -strict -2 -q:a 4 -y {arquivo_ogg}'
                    subprocess.run(comando, shell=True)

            # Exemplo de uso da função
            sourceFileDir = os.path.dirname(os.path.abspath(__file__))
            somDir = os.path.join(sourceFileDir, "som")

            arquivo_webm = f'som/playwebm.webm'
            arquivo_ogg = f'som/{titulo_formatado}.ogg'
            converter_audio_webm_para_ogg(arquivo_webm, arquivo_ogg)

            self.manager.get_screen("carregamento").ids.progress_carregamento.value = 80
            self.manager.get_screen("carregamento").ids.label_progress.text = f'80%'

            self.manager.get_screen("inicio").ids.play.icon = 'pause'
            self.manager.get_screen("musicas").ids.play.icon = 'pause'
            self.manager.get_screen("pesquisar").ids.play.icon = 'pause'
            self.manager.get_screen("playlist").ids.play.icon = 'pause'

            # obtém o caminho do diretório atual
            sourceFileDir = os.path.dirname(os.path.abspath(__file__))

            # obtém o caminho da pasta "som"
            somDir = os.path.join(sourceFileDir, "som")

            # obtém o caminho do arquivo "play1.ogg"
            playFile = os.path.join(somDir, f"{titulo_formatado}.ogg")

            Uri = Uri2
            PythonActivity = PythonActivity2
            player = player2

            if platform == 'android':
                if player.isPlaying():
                    player.stop()
                    player.reset()

                uri = Uri.parse('file://' + playFile)
                player.reset()
                player.setDataSource(PythonActivity.mActivity, uri)

                # Prepara o MediaPlayer para reprodução
                player.prepare()
                # Inicia a reprodução do áudio
                """position_ms = 50 * 1000
                player.seekTo(position_ms)"""

                # Obtém a duração do arquivo de áudio em milissegundos
                duration_ms = player.getDuration()

                # Converte a duração para segundos
                duration = duration_ms / 1000
                Inicio.tempo_musica = duration

                print(f"duração {duration}")


            else:
                self.sound = pygame.mixer.music.load(playFile)
                duration = pygame.mixer.Sound(playFile).get_length()
                Inicio.tempo_musica = duration

            if Inicio.position == 0:
                self.manager.get_screen("carregamento").ids.progress_carregamento.value = 100
                self.manager.get_screen("carregamento").ids.label_progress.text = f'100%'
                self.voltar_inicio()

                if platform == 'android':
                    player.start()
                else:
                    pygame.mixer.music.play()

            else:
                self.manager.get_screen("carregamento").ids.progress_carregamento.value = 100
                self.manager.get_screen("carregamento").ids.label_progress.text = f'100%'
                self.voltar_inicio()
                if platform == 'android':
                    player.seekTo(Inicio.position)
                    player.start()
                else:
                    pygame.mixer.music.play()
                    pygame.mixer.music.set_pos(Inicio.position)
                    print(Inicio.position)

            try:
                self.progress_bar_update.cancel()
            except:
                pass

            Inicio.position = -1
            stop_threads = False
            print(f'DURAÇÃO TOTALLLLLLL : {Inicio.tempo_musica}')

            Inicio.position = -1
            Inicio.numero_musica = n_audio

            def update_progress():
                while True:
                    if Musicas.mudanca_faixa_musica:
                        break
                    print(Inicio.numero_musica)
                    time.sleep(1)
                    if Inicio.position >= int(Inicio.tempo_musica):
                        numero = int(Inicio.numero_musica)
                        if numero <= 5:
                            if int(numero) < 5:
                                numero += 1
                            elif numero == 5:
                                numero = 1
                            if numero == 1:
                                titulo1 = self.manager.get_screen("inicio").ids.titulo_brasil1.text
                                artista1 = self.manager.get_screen("inicio").ids.artista_brasil1.text
                                image1 = self.manager.get_screen("inicio").ids.source_brasil1.source

                                self.play_modify(titulo1, artista1, f'{numero}', image1)
                                self.play(titulo1, artista1, f'{numero}', image1)
                            if numero == 2:
                                titulo1 = self.manager.get_screen("inicio").ids.titulo_brasil2.text
                                artista1 = self.manager.get_screen("inicio").ids.artista_brasil2.text
                                image1 = self.manager.get_screen("inicio").ids.source_brasil2.source
                                print(artista1)

                                self.play_modify(titulo1, artista1, f'{numero}', image1)
                                self.play(titulo1, artista1, f'{numero}', image1)
                            elif numero == 3:
                                titulo1 = self.manager.get_screen("inicio").ids.titulo_brasil3.text
                                artista1 = self.manager.get_screen("inicio").ids.artista_brasil3.text
                                image1 = self.manager.get_screen("inicio").ids.source_brasil3.source

                                self.play_modify(titulo1, artista1, f'{numero}', image1)
                                self.play(titulo1, artista1, f'{numero}', image1)
                            elif numero == 4:
                                titulo1 = self.manager.get_screen("inicio").ids.titulo_brasil4.text
                                artista1 = self.manager.get_screen("inicio").ids.artista_brasil4.text
                                image1 = self.manager.get_screen("inicio").ids.source_brasil4.source

                                self.play_modify(titulo1, artista1, f'{numero}', image1)
                                self.play(titulo1, artista1, f'{numero}', image1)


                            elif numero == 5:
                                titulo1 = self.manager.get_screen("inicio").ids.titulo_brasil5.text
                                artista1 = self.manager.get_screen("inicio").ids.artista_brasil5.text
                                image1 = self.manager.get_screen("inicio").ids.source_brasil5.source

                                self.play_modify(titulo1, artista1, f'{numero}', image1)
                                self.play(titulo1, artista1, f'{numero}', image1)

                        elif numero > 5:
                            numero = int(Inicio.numero_musica)
                            if int(numero) < 10:
                                numero += 1

                            elif int(numero) == 10:
                                numero = 6
                            self.manager.get_screen("inicio").ids.n_audio.text = titulo_formatado
                            if numero == 6:
                                titulo1 = self.manager.get_screen("inicio").ids.titulo_mundo1.text
                                artista1 = self.manager.get_screen("inicio").ids.artista_mundo1.text
                                image1 = self.manager.get_screen("inicio").ids.source_mundo1.source

                                self.play_modify(titulo1, artista1, f'{numero}', image1)
                                self.play(titulo1, artista1, f'{numero}', image1)

                            elif numero == 7:
                                titulo1 = self.manager.get_screen("inicio").ids.titulo_mundo2.text
                                artista1 = self.manager.get_screen("inicio").ids.artista_mundo2.text
                                image1 = self.manager.get_screen("inicio").ids.source_mundo2.source

                                self.play_modify(titulo1, artista1, f'{numero}', image1)
                                self.play(titulo1, artista1, f'{numero}', image1)
                            elif numero == 8:
                                titulo1 = self.manager.get_screen("inicio").ids.titulo_mundo3.text
                                artista1 = self.manager.get_screen("inicio").ids.artista_mundo3.text
                                image1 = self.manager.get_screen("inicio").ids.source_mundo3.source

                                self.play_modify(titulo1, artista1, f'{numero}', image1)
                                self.play(titulo1, artista1, f'{numero}', image1)
                            elif numero == 9:
                                titulo1 = self.manager.get_screen("inicio").ids.titulo_mundo4.text
                                artista1 = self.manager.get_screen("inicio").ids.artista_mundo4.text
                                image1 = self.manager.get_screen("inicio").ids.source_mundo4.source

                                self.play_modify(titulo1, artista1, f'{numero}', image1)
                                self.play(titulo1, artista1, f'{numero}', image1)
                            elif numero == 10:
                                titulo1 = self.manager.get_screen("inicio").ids.titulo_mundo5.text
                                artista1 = self.manager.get_screen("inicio").ids.artista_mundo5.text
                                image1 = self.manager.get_screen("inicio").ids.source_mundo5.source

                                self.play_modify(titulo1, artista1, f'{numero}', image1)
                                self.play(titulo1, artista1, f'{numero}', image1)

                    else:
                        pass

            if Inicio.stop_threads == False:
                Inicio.progress_bar_update = threading.Thread(target=update_progress).start()
            if Inicio.stop_threads == False:
                Inicio.progress_bar_update = threading.Thread(target=self.update_progress).start()

    def update_progress(self, id):
        try:
            while True:
                if Musicas.mudanca_faixa_musica:
                    Inicio.stop_threads = False
                    break
                self.manager.get_screen("inicio").ids.progress_bar.max = Inicio.tempo_musica
                self.manager.get_screen("musicas").ids.progress_bar.max = Inicio.tempo_musica
                self.manager.get_screen("pesquisar").ids.progress_bar.max = Inicio.tempo_musica
                self.manager.get_screen("playlist").ids.progress_bar.max = Inicio.tempo_musica
                print('TA AQUI DENTRO!')
                Inicio.stop_threads = True
                time.sleep(1)
                Inicio.position += 1
                if Inicio.progress_bar_valor_novo != 0:
                    if self.manager.current == 'inicio':
                        self.manager.get_screen("inicio").ids.progress_bar.value = Inicio.progress_bar_valor_novo
                    elif self.manager.current == 'musicas':
                        self.manager.get_screen("musicas").ids.progress_bar.value = Inicio.progress_bar_valor_novo
                    elif self.manager.current == 'pesquisar':
                        self.manager.get_screen("pesquisar").ids.progress_bar.value = Inicio.progress_bar_valor_novo
                    elif self.manager.current == 'playlist':
                        self.manager.get_screen("playlist").ids.progress_bar.value = Inicio.progress_bar_valor_novo

                    Inicio.position = Inicio.progress_bar_valor_novo
                    if platform == 'android':
                        player2.seekTo(Inicio.progress_bar_valor_novo * 1000)

                    else:
                        pygame.mixer.music.set_pos(Inicio.progress_bar_valor_novo)

                    Inicio.progress_bar_valor_novo = 0

                if Inicio.position >= int(Inicio.tempo_musica):
                    self.manager.get_screen("inicio").ids.progress_bar.value = 0
                    self.manager.get_screen("musicas").ids.progress_bar.value = 0
                    self.manager.get_screen("pesquisar").ids.progress_bar.value = 0
                    self.manager.get_screen("playlist").ids.progress_bar.value = 0
                else:
                    self.manager.get_screen("inicio").ids.progress_bar.value = Inicio.position
                    self.manager.get_screen("musicas").ids.progress_bar.value = Inicio.position
                    self.manager.get_screen("pesquisar").ids.progress_bar.value = Inicio.position
                    self.manager.get_screen("playlist").ids.progress_bar.value = Inicio.position
        except BaseException as e:
            print(f'ERROR NO UPDATE PROGRESS {e}')

    @mainthread
    def play(self, titulo, artista, n_audio, source, lenght):
        Musicas.mudanca_faixa_musica = False
        Inicio.mudanca_faixa_inicio = True
        self.manager.get_screen("inicio").ids.scroll.pos_hint = {'center_x': 0.53, 'top': 0.23}
        self.manager.get_screen("pesquisar").ids.scroll.pos_hint = {'center_x': 0.53, 'top': 0.23}
        self.manager.get_screen("playlist").ids.scroll.pos_hint = {'center_x': 0.53, 'top': 0.23}
        self.manager.get_screen("musicas").ids.scroll.pos_hint = {'center_x': 0.53, 'top': 0.23}
        self.manager.get_screen("search").ids.scroll.pos_hint = {'center_x': 0.53, 'top': 0.23}

        if Inicio.numero_musica != None:
            self.dynamic_ids[f"botaoplay{Inicio.numero_musica}"].icon = "play"
            self.dynamic_ids[f"botaoplay{int(n_audio)}"].icon = "equalizer"
        else:
            self.dynamic_ids[f"botaoplay{int(n_audio)}"].icon = 'equalizer'

        Inicio.ultimo_audio = n_audio
        self.manager.get_screen("carregamento").ids.progress_carregamento.value = 0
        self.manager.get_screen("carregamento").ids.progress_carregamento.max = 100
        self.manager.get_screen(
            "carregamento").ids.label_progress_info.text = f'Carregando música aguarde, nosso servidor é limitado!'
        self.manager.get_screen("carregamento").ids.label_progress.text = f'10%'
        self.manager.current = 'carregamento'
        self.manager.transition.direction = 'left'

        self.manager.get_screen("inicio").ids.nome_musica.text = titulo
        self.manager.get_screen("inicio").ids.nome_artista.text = artista
        self.manager.get_screen("inicio").ids.image_musica.source = source

        self.manager.get_screen("musicas").ids.nome_musica.text = titulo
        self.manager.get_screen("musicas").ids.nome_artista.text = artista
        self.manager.get_screen("musicas").ids.image_musica.source = source

        self.manager.get_screen("pesquisar").ids.nome_musica.text = titulo
        self.manager.get_screen("pesquisar").ids.nome_artista.text = artista
        self.manager.get_screen("pesquisar").ids.image_musica.source = source

        self.manager.get_screen("playlist").ids.nome_musica.text = titulo
        self.manager.get_screen("playlist").ids.nome_artista.text = artista
        self.manager.get_screen("playlist").ids.image_musica.source = source

        self.manager.get_screen("search").ids.nome_musica.text = titulo
        self.manager.get_screen("search").ids.nome_artista.text = artista
        self.manager.get_screen("search").ids.image_musica.source = source

        threading.Thread(target=Musicas.thd_play, args=(self, titulo, artista, n_audio, source, lenght)).start()

    def tocar_musica(self, titulo, artista, n_audio, source, length):

        print(length)
        if f'botaoplay{n_audio}' in self.dynamic_ids:

            # self.dynamic_ids[n_audio].icon = 'equalizer'
            print(self.dynamic_ids[f"imagem{n_audio}"].source)
            print(self.dynamic_ids[f"titulo{n_audio}"].text)
            print(self.dynamic_ids[f"artista{n_audio}"].text)

            Musicas.play(self, titulo, artista, n_audio, source, length)
        else:
            print("ID do widget não encontrado")

    def salvar_musica(self, titulo, artista, n_audio, source, length, url_playlist):
        if f'botaoheart{n_audio}' in self.dynamic_ids:
            if self.dynamic_ids[f"botaoheart{n_audio}"].icon != "heart":
                self.dynamic_ids[f"botaoheart{n_audio}"].icon = "heart"
                print(url_playlist)

                dados_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "dados"))
                with open(os.path.join(dados_path, "escutadas.txt"), "r", encoding="utf-8") as r:
                    salvas = eval(r.read())

                    nova_musica = {
                        "nome_da_musica": f"{titulo}",
                        "nome_do_artista": f"{artista}",
                        "imagem": f"{source}",
                        "playlist": f"{url_playlist}"
                    }
                    # Verifica se a música já está na lista de músicas salvas
                    if nova_musica not in salvas:
                        salvas.append(nova_musica)

                    with open(os.path.join(dados_path, "escutadas.txt"), "w", encoding="utf-8") as w:
                        w.write(str(salvas))
            else:
                self.dynamic_ids[f"botaoheart{n_audio}"].icon = "heart-outline"

                dados_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "dados"))
                with open(os.path.join(dados_path, "escutadas.txt"), "r", encoding="utf-8") as r:
                    salvas = eval(r.read())

                for musica in salvas:
                    if musica["nome_da_musica"] == titulo and musica["nome_do_artista"] == artista:
                        salvas.remove(musica)

                with open(os.path.join(dados_path, "escutadas.txt"), "w", encoding="utf-8") as w:
                    w.write(str(salvas))

                print(salvas)

            print(n_audio)

    def abrir_musica(self, id):
        self.manager.get_screen("musicas").ids.musicas.clear_widgets()
        url = f"https://api.deezer.com/playlist/{id}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            print(f"Lista de músicas da playlist '{data['title']}':")

            # Iterar sobre as músicas em lotes
            tracks = iter(itertools.islice(data["tracks"]["data"], 50))
            musicas_len = len(data["tracks"]["data"])

            if musicas_len >= 50:
                musicas_len = 50
            else:
                musicas_len = len(data["tracks"]["data"])

            # Configurar a barra de progresso
            self.manager.get_screen("carregamento").ids.progress_carregamento.value = 0
            self.manager.get_screen("carregamento").ids.progress_carregamento.max = musicas_len
            self.manager.get_screen(
                "carregamento").ids.label_progress_info.text = f'Carregando músicas aguarde, nosso servidor é limitado!'
            self.manager.get_screen("carregamento").ids.label_progress.text = f'10%'
            self.manager.current = 'carregamento'
            self.manager.transition.direction = 'left'
            self.contador = 0
            self.contador_musicas = 0

            def process_chunk(dt):
                try:
                    track = next(tracks)
                except StopIteration:
                    # Todos os itens foram processados, cancele o agendamento
                    Clock.unschedule(process_chunk)
                    album_name = data["title"]
                    self.manager.get_screen("musicas").ids.nomeplay.text = album_name
                    self.manager.get_screen("musicas").ids.scrollplaylist.scroll_y = 1  # SETAR PARA O TOPO
                    self.manager.current = 'musicas'
                    self.manager.transition.direction = 'left'
                    return
                try:
                    track_name = track["title"]
                    artist_name = track["artist"]["name"]
                    image_url = track["album"]["cover_medium"]
                    album_name = data["title"]
                    self.contador += 1
                    self.contador_musicas += 1

                    # Atualize o texto do rótulo com a nova porcentagem
                    porcentagem_atual = (self.contador / musicas_len) * 100
                    self.manager.get_screen("carregamento").ids.label_progress.text = f"{int(porcentagem_atual)}%"
                    self.manager.get_screen("carregamento").ids.progress_carregamento.value += 1

                    card = MDCard(size_hint_y=None,
                                  height='65dp',
                                  md_bg_color=get_color_from_hex('#121212'))

                    floatlayout = MDFloatLayout()

                    card.add_widget(floatlayout)

                    imageasync = AsyncImage(source=f"{image_url}",
                                            size_hint_y=None,
                                            height='65dp',
                                            pos_hint={'center_y': .5, 'center_x': .1})

                    self.dynamic_ids[f'imagem{self.contador_musicas}'] = imageasync
                    floatlayout.add_widget(imageasync)

                    labeltrack = MDLabel(text=F'{track_name}',
                                         halign='left',
                                         bold=True,
                                         size_hint_x=.55,
                                         font_style='Caption',
                                         pos_hint={'center_y': .64, 'center_x': .57},
                                         theme_text_color="Custom",
                                         text_color=get_color_from_hex('#ffffff'))

                    self.dynamic_ids[f'titulo{self.contador_musicas}'] = labeltrack

                    floatlayout.add_widget(labeltrack)

                    labelartist = MDLabel(text=f'{artist_name}',
                                          halign='left',
                                          font_style='Caption',
                                          pos_hint={'center_y': .3, 'center_x': .795},
                                          theme_text_color="Custom",
                                          text_color=get_color_from_hex('#ffffff'))

                    self.dynamic_ids[f'artista{self.contador_musicas}'] = labelartist

                    floatlayout.add_widget(labelartist)

                    texto = f"{track_name} {artist_name}"
                    titulo_formatado = re.sub(r'[^a-zA-Z0-9_]', '_', texto)

                    dados_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "dados"))
                    with open(os.path.join(dados_path, "escutadas.txt"), "r", encoding="utf-8") as r:
                        salvas = eval(r.read())

                    if any(f'{track_name}' in musica.values() for musica in salvas):
                        botaoheart = MDIconButton(icon="heart",
                                                  pos_hint={'center_x': .25, 'center_y': .5},
                                                  theme_text_color="Custom",
                                                  text_color=get_color_from_hex('#F70707'),
                                                  on_release=lambda a, titulo=track_name, artista=artist_name,
                                                                    id=str(self.contador_musicas),
                                                                    source=image_url, lenght=musicas_len,
                                                                    url=url: Musicas.salvar_musica(self,
                                                                                                   titulo, artista, id,
                                                                                                   source, lenght, url))

                        self.dynamic_ids[f"botaoheart{self.contador_musicas}"] = botaoheart
                        floatlayout.add_widget(botaoheart)
                    else:
                        botaoheart = MDIconButton(icon="heart-outline",
                                                  pos_hint={'center_x': .25, 'center_y': .5},
                                                  theme_text_color="Custom",
                                                  text_color=get_color_from_hex('#F70707'),
                                                  on_release=lambda a, titulo=track_name, artista=artist_name,
                                                                    id=str(self.contador_musicas),
                                                                    source=image_url, lenght=musicas_len,
                                                                    url=url: Musicas.salvar_musica(self,
                                                                                                   titulo, artista, id,
                                                                                                   source, lenght, url))

                        self.dynamic_ids[f"botaoheart{self.contador_musicas}"] = botaoheart
                        floatlayout.add_widget(botaoheart)

                    if os.path.exists(f"som/{titulo_formatado}.ogg") and os.path.isfile(f"som/{titulo_formatado}.ogg"):
                        botaoplay = MDIconButton(icon="play",
                                                 pos_hint={'center_x': .9, 'center_y': .5},
                                                 theme_text_color="Custom",
                                                 text_color=get_color_from_hex('#FFFFFF'),
                                                 on_release=lambda a, titulo=track_name, artista=artist_name,
                                                                   id=str(self.contador_musicas),
                                                                   source=image_url,
                                                                   lenght=musicas_len: Musicas.tocar_musica(self,
                                                                                                            titulo,
                                                                                                            artista, id,
                                                                                                            source,
                                                                                                            lenght))

                    else:
                        botaoplay = MDIconButton(icon="download",
                                                 pos_hint={'center_x': .9, 'center_y': .5},
                                                 theme_text_color="Custom",
                                                 text_color=get_color_from_hex('#FFFFFF'),
                                                 on_release=lambda a, titulo=track_name, artista=artist_name,
                                                                   id=str(self.contador_musicas),
                                                                   source=image_url,
                                                                   lenght=musicas_len: Musicas.tocar_musica(self,
                                                                                                            titulo,
                                                                                                            artista, id,
                                                                                                            source,
                                                                                                            lenght))

                    self.dynamic_ids[f"botaoplay{self.contador_musicas}"] = botaoplay

                    floatlayout.add_widget(botaoplay)

                    self.manager.get_screen("musicas").ids.musicas.add_widget(card)

                except BaseException as e:
                    print(f'error! {e}')
                    pass

            Clock.schedule_interval(process_chunk, 0.01)


        else:
            pass

    def play_stop(self):
        if platform == 'android':
            if player2.isPlaying():
                player2.pause()
                self.manager.get_screen("inicio").ids.play.icon = 'play'
                self.manager.get_screen("musicas").ids.play.icon = 'play'
                self.manager.get_screen("pesquisar").ids.play.icon = 'play'
                self.manager.get_screen("playlist").ids.play.icon = 'play'
                self.manager.get_screen("search").ids.play.icon = 'play'
            else:
                player2.start()
                self.manager.get_screen("inicio").ids.play.icon = 'pause'
                self.manager.get_screen("musicas").ids.play.icon = 'pause'
                self.manager.get_screen("pesquisar").ids.play.icon = 'pause'
                self.manager.get_screen("playlist").ids.play.icon = 'pause'
                self.manager.get_screen("search").ids.play.icon = 'pause'
        else:
            print('FUNCIONA APENAS NO ANDROID!')

    def click_barra(self, instance, touch):
        if instance.collide_point(touch.pos[0], touch.pos[1]):
            # calcula a posição da barra de progresso
            bar_x = instance.x
            bar_width = instance.width
            bar_pos = (touch.pos[0] - bar_x) / bar_width

            # verifica se a posição do toque está dentro dos limites da barra de progresso
            if 0 <= bar_pos <= 1:
                # a posição do toque está dentro dos limites da barra de progresso
                touch_pos = bar_pos * instance.max, touch.pos[1]
                print("Clicado na posição:", touch_pos)
                Inicio.progress_bar_valor_novo = (int(touch_pos[0]))

                self.manager.get_screen("inicio").ids.progress_bar.value = Inicio.progress_bar_valor_novo
                self.manager.get_screen("musicas").ids.progress_bar.value = Inicio.progress_bar_valor_novo
                self.manager.get_screen("pesquisar").ids.progress_bar.value = Inicio.progress_bar_valor_novo
                self.manager.get_screen("playlist").ids.progress_bar.value = Inicio.progress_bar_valor_novo

                Inicio.position = Inicio.progress_bar_valor_novo

    def stop(self):
        self.manager.get_screen("inicio").ids.scroll.pos_hint = {'center_x': 0.53, 'top': 0.0}
        self.manager.get_screen("musicas").ids.scroll.pos_hint = {'center_x': 0.53, 'top': 0.0}
        self.manager.get_screen("pesquisar").ids.scroll.pos_hint = {'center_x': 0.53, 'top': 0.0}
        self.manager.get_screen("playlist").ids.scroll.pos_hint = {'center_x': 0.53, 'top': 0.0}
        self.manager.get_screen("search").ids.scroll.pos_hint = {'center_x': 0.53, 'top': 0.0}
        if platform == 'android':
            if player2.isPlaying():
                player2.stop()
                player2.reset()
        else:
            pygame.mixer.music.unload()  # descarrega o arquivo de som

    def voltar(self):
        if Inicio.vermaiscount:
            self.manager.current = 'inicio'
            self.manager.transition.direction = 'right'
            Inicio.vermaiscount = False
        else:
            self.manager.current = 'playlist'
            self.manager.transition.direction = 'right'


class Search(MDScreen):
    mudanca_faixa_search = False
    dynamic_ids = DictProperty({})
    pesquisado = False
    contador_musicas = 0
    contador = 0
    stop_threads3 = False
    ultimo_audio = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        def detectar_pesquisa(dt):
            if self.manager.current == 'search':
                textfield = self.manager.get_screen("search").ids.textfield.text

                if len(textfield) > 0:
                    self.manager.get_screen("search").ids.label_quer_ouvir.text = ''
                    self.manager.get_screen("search").ids.pesquisa_label.text = f"Pesquisa: {textfield}"
                elif len(textfield) == 0 or Search.pesquisado:
                    self.manager.get_screen("search").ids.label_quer_ouvir.text = 'O que você quer ouvir?'
                    self.manager.get_screen("search").ids.pesquisa_label.text = ''

        Clock.schedule_interval(detectar_pesquisa, 0)


    def click_barra(self, instance, touch):

        try:
            if instance.collide_point(touch.pos[0], touch.pos[1]):
                # calcula a posição da barra de progresso
                bar_x = instance.x
                bar_width = instance.width
                bar_pos = (touch.pos[0] - bar_x) / bar_width

                # verifica se a posição do toque está dentro dos limites da barra de progresso
                if 0 <= bar_pos <= 1:
                    # a posição do toque está dentro dos limites da barra de progresso
                    touch_pos = bar_pos * instance.max, touch.pos[1]
                    print("Clicado na posição:", touch_pos)
                    Inicio.progress_bar_valor_novo = (int(touch_pos[0]))

                    self.manager.get_screen("inicio").ids.progress_bar.value = Inicio.progress_bar_valor_novo
                    self.manager.get_screen("musicas").ids.progress_bar.value = Inicio.progress_bar_valor_novo
                    self.manager.get_screen("pesquisar").ids.progress_bar.value = Inicio.progress_bar_valor_novo
                    self.manager.get_screen("playlist").ids.progress_bar.value = Inicio.progress_bar_valor_novo
                    self.manager.get_screen("search").ids.progress_bar.value = Inicio.progress_bar_valor_novo

                    Inicio.position = Inicio.progress_bar_valor_novo
        except BaseException as e:
            print(f'Error no click_barra {e} ')

    def play_stop(self):
        if platform == 'android':
            if player2.isPlaying():
                player2.pause()
                self.manager.get_screen("inicio").ids.play.icon = 'play'
                self.manager.get_screen("musicas").ids.play.icon = 'play'
                self.manager.get_screen("pesquisar").ids.play.icon = 'play'
                self.manager.get_screen("playlist").ids.play.icon = 'play'
            else:
                player2.start()
                self.manager.get_screen("inicio").ids.play.icon = 'pause'
                self.manager.get_screen("musicas").ids.play.icon = 'pause'
                self.manager.get_screen("pesquisar").ids.play.icon = 'pause'
                self.manager.get_screen("playlist").ids.play.icon = 'pause'
        else:
            print('FUNCIONA APENAS NO ANDROID!')

    def stop(self):
        self.manager.get_screen("inicio").ids.scroll.pos_hint = {'center_x': 0.53, 'top': 0.0}
        if platform == 'android':
            if player2.isPlaying():
                player2.stop()
                player2.reset()
        else:
            pygame.mixer.music.unload()  # descarrega o arquivo de som

    def voltar(self):
        self.manager.current = 'pesquisar'
        self.manager.transition.direction = 'right'

    def thd_pesquisar(self, busca):
        contador = 0
        contador2 = 0
        verificador = []

        for x in range(6):
            print('entrou!')
            imagem = "imagem" + str(contador)
            titulo = "titulo" + str(contador)
            favoritar = "favoritar" + str(contador)
            card = "card" + str(contador)
            icone = "icone" + str(contador)

            print(titulo)
            while True:
                try:
                    results = SearchVideos(busca, offset=0, mode="json", max_results=200)
                    info = json.loads(results.result())["search_result"][contador2]
                    video_url = info["link"]
                    thumbnail_url = info['thumbnails'][2]
                    title = info["title"]

                    contador2 += 1
                    tamanho = YouTube(video_url).length

                    if tamanho <= 360 and not title in verificador:
                        verificador.append(title)
                        self.manager.get_screen("search").ids[icone].pos_hint = {'center_x': .9, 'center_y': .5}
                        self.manager.get_screen("search").ids[card].opacity = 1
                        self.manager.get_screen("search").ids.spinner.active = False
                        break
                    else:
                        self.manager.get_screen("search").ids[icone].pos_hint = {'center_x': 9, 'center_y': .5}
                        self.manager.get_screen("search").ids[titulo].text = f'Procurando música'
                        self.manager.get_screen("search").ids[card].opacity = 1
                except BaseException as e:
                    print(e)
                    if isinstance(e, IndexError) and str(e) == 'list index out of range':
                        self.manager.get_screen("search").ids[card].opacity = 0
                        break

            contador += 1
            print(tamanho)

            if tamanho < 360:
                self.manager.get_screen("search").ids[imagem].source = thumbnail_url
                self.manager.get_screen("search").ids[titulo].text = title
                # self.manager.get_screen("search").ids[favoritar].icon = 'heart'

                '''self.manager.get_screen("search").ids.artista.text = ''
                self.manager.get_screen("search").ids.icone.text = ''
                self.manager.get_screen("search").ids.favoritar.text = '''''
            else:
                self.manager.get_screen("search").ids[titulo].pos_hint = {}

    def pesquisar(self, busca):

        self.manager.get_screen("search").ids.spinner.active = True
        self.manager.get_screen("search").ids.info_1.opacity = 0
        self.manager.get_screen("search").ids.info_2.opacity = 0

        self.manager.get_screen("search").ids.card0.opacity = 0
        self.manager.get_screen("search").ids.card1.opacity = 0
        self.manager.get_screen("search").ids.card2.opacity = 0
        self.manager.get_screen("search").ids.card3.opacity = 0
        self.manager.get_screen("search").ids.card4.opacity = 0
        self.manager.get_screen("search").ids.card5.opacity = 0

        self.manager.get_screen("search").ids.imagem0.source = 'imagens/carregando.png'
        self.manager.get_screen("search").ids.imagem1.source = 'imagens/carregando.png'
        self.manager.get_screen("search").ids.imagem2.source = 'imagens/carregando.png'
        self.manager.get_screen("search").ids.imagem3.source = 'imagens/carregando.png'
        self.manager.get_screen("search").ids.imagem4.source = 'imagens/carregando.png'
        self.manager.get_screen("search").ids.imagem5.source = 'imagens/carregando.png'

        threading.Thread(target=Search.thd_pesquisar, args=(self, busca)).start()


    def tocar(self,titulo,artista,n_audio,source ):
        self.play(titulo,artista,n_audio,source)

        icone = "icone" + str(n_audio-1)
        if Search.ultimo_audio != None:
            icone2 = "icone" + str(Search.ultimo_audio)
            self.manager.get_screen("search").ids[icone2].icon = "play"
            self.manager.get_screen("search").ids[icone].icon = "equalizer"
        else:
            self.manager.get_screen("search").ids[icone].icon = "equalizer"

        Search.ultimo_audio = n_audio - 1


    def thd_play(self, titulo, artista, n_audio, source=None):
        Inicio.position = 0
        progress_bar_valor_novo = 0
        Inicio.contadorplay = 1
        pygame.mixer.music.unload()  # descarrega o arquivo de som
        print(Inicio.url_videos)
        Inicio.lista_arrastar = []
        print(f'Tamanho da lista: {Inicio.lista_arrastar}')

        texto = f"{titulo} {artista}"
        titulo_formatado = re.sub(r'[^a-zA-Z0-9_]', '_', texto)

        print(titulo_formatado)

        if os.path.exists(f"som/{titulo_formatado}.ogg") and os.path.isfile(f"som/{titulo_formatado}.ogg"):
            self.manager.get_screen("inicio").ids.scroll.pos_hint = {'center_x': 0.53, 'top': 0.23}

            self.manager.get_screen("carregamento").ids.progress_carregamento.value = 30
            self.manager.get_screen("carregamento").ids.label_progress.text = f'30%'

            self.manager.get_screen("carregamento").ids.progress_carregamento.value = 60
            self.manager.get_screen("carregamento").ids.label_progress.text = f'60%'

            self.manager.get_screen("carregamento").ids.progress_carregamento.value = 80
            self.manager.get_screen("carregamento").ids.label_progress.text = f'80%'

            self.manager.get_screen("inicio").ids.play.icon = 'pause'
            self.manager.get_screen("musicas").ids.play.icon = 'pause'
            self.manager.get_screen("pesquisar").ids.play.icon = 'pause'
            self.manager.get_screen("playlist").ids.play.icon = 'pause'
            self.manager.get_screen("search").ids.play.icon = 'pause'

            # obtém o caminho do diretório atual
            sourceFileDir = os.path.dirname(os.path.abspath(__file__))

            # obtém o caminho da pasta "som"
            somDir = os.path.join(sourceFileDir, "som")

            # obtém o caminho do arquivo "play1.ogg"
            playFile = os.path.join(somDir, f"{titulo_formatado}.ogg")

            Uri = Uri2
            PythonActivity = PythonActivity2
            player = player2

            if platform == 'android':
                if player.isPlaying():
                    player.stop()
                    player.reset()

                uri = Uri.parse('file://' + playFile)
                player.reset()
                player.setDataSource(PythonActivity.mActivity, uri)

                # Prepara o MediaPlayer para reprodução
                player.prepare()
                # Inicia a reprodução do áudio
                """position_ms = 50 * 1000
                player.seekTo(position_ms)"""

                # Obtém a duração do arquivo de áudio em milissegundos
                duration_ms = player.getDuration()

                # Converte a duração para segundos
                duration = duration_ms / 1000
                Inicio.tempo_musica = duration

                print(f"duração {duration}")


            else:
                self.sound = pygame.mixer.music.load(playFile)
                duration = pygame.mixer.Sound(playFile).get_length()
                Inicio.tempo_musica = duration

            if Inicio.position == 0:
                self.manager.get_screen("carregamento").ids.progress_carregamento.value = 100
                self.manager.get_screen("carregamento").ids.label_progress.text = f'100%'
                self.voltar_inicio()

                if platform == 'android':
                    player.start()
                else:
                    pygame.mixer.music.play()

            else:
                self.manager.get_screen("carregamento").ids.progress_carregamento.value = 100
                self.manager.get_screen("carregamento").ids.label_progress.text = f'100%'
                self.voltar_inicio()
                if platform == 'android':
                    player.seekTo(Inicio.position)
                    player.start()
                else:
                    pygame.mixer.music.play()
                    pygame.mixer.music.set_pos(Inicio.position)
                    print(Inicio.position)

            # print(duration)

            try:
                self.progress_bar_update.cancel()
            except:
                pass

            Inicio.position = -1
            Inicio.numero_musica = n_audio

            def update_progress():
                while True:
                    if Inicio.mudanca_faixa_inicio or Musicas.mudanca_faixa_musica:
                        break
                    print(Inicio.numero_musica)
                    time.sleep(1)
                    if Inicio.position >= int(Inicio.tempo_musica):
                        numero = int(Inicio.numero_musica)
                        if numero <= 5:
                            if int(numero) < 5:
                                numero += 1
                            elif numero == 5:
                                numero = 1
                            if numero == 1:
                                titulo1 = self.manager.get_screen("search").ids.titulo0.text
                                artista1 = ''
                                image1 = self.manager.get_screen("search").ids.imagem0.source

                                self.play_modify(titulo1, artista1, f'{numero}', image1)
                                self.play(titulo1, artista1, f'{numero}', image1)

                            if numero == 2:
                                titulo1 = self.manager.get_screen("search").ids.titulo1.text
                                artista1 = ''
                                image1 = self.manager.get_screen("search").ids.imagem1.source

                                self.play_modify(titulo1, artista1, f'{numero}', image1)
                                self.play(titulo1, artista1, f'{numero}', image1)

                            if numero ==3:
                                titulo1 = self.manager.get_screen("search").ids.titulo2.text
                                artista1 = ''
                                image1 = self.manager.get_screen("search").ids.imagem2.source

                                self.play_modify(titulo1, artista1, f'{numero}', image1)
                                self.play(titulo1, artista1, f'{numero}', image1)

                            if numero == 4:
                                titulo1 = self.manager.get_screen("search").ids.titulo3.text
                                artista1 = ''
                                image1 = self.manager.get_screen("search").ids.imagem3.source

                                self.play_modify(titulo1, artista1, f'{numero}', image1)
                                self.play(titulo1, artista1, f'{numero}', image1)
                            if numero == 5:
                                titulo1 = self.manager.get_screen("search").ids.titulo4.text
                                artista1 = ''
                                image1 = self.manager.get_screen("search").ids.imagem4.source

                                self.play_modify(titulo1, artista1, f'{numero}', image1)
                                self.play(titulo1, artista1, f'{numero}', image1)

                            if numero == 6:
                                titulo1 = self.manager.get_screen("search").ids.titulo5.text
                                artista1 = ''
                                image1 = self.manager.get_screen("search").ids.imagem5.source

                                self.play_modify(titulo1, artista1, f'{numero}', image1)
                                self.play(titulo1, artista1, f'{numero}', image1)

                    else:
                        pass

            if Search.stop_threads3 == False:
                Inicio.progress_bar_update = threading.Thread(target=update_progress).start()
            if Search.stop_threads3 == False:
                Inicio.progress_bar_update = threading.Thread(target=self.update_progress).start()



        else:
            print("O arquivo não existe na pasta raiz do projeto.")

            self.manager.get_screen("inicio").ids.scroll.pos_hint = {'center_x': 0.53, 'top': 0.23}

            self.manager.get_screen("carregamento").ids.progress_carregamento.value = 30
            self.manager.get_screen("carregamento").ids.label_progress.text = f'30%'

            def download_youtube_video(video_url, titulo='playwebm'):
                while True:
                    try:
                        # Cria uma instância do objeto YouTube
                        video = YouTube(video_url)

                        # Seleciona o formato de áudio desejado (webm ou m4a)
                        audio_format = "webm"  # ou "m4a"

                        # Seleciona a faixa de áudio com a maior qualidade disponível
                        audio = video.streams.filter(only_audio=True, file_extension=audio_format).order_by(
                            'abr').desc().first()

                        # Baixa o arquivo de áudio como bytes
                        audio_bytes = io.BytesIO()
                        audio.stream_to_buffer(audio_bytes)

                        # Decodifica a representação em base64 para obter os dados binários do arquivo de áudio
                        audio_data = audio_bytes.getvalue()

                        # Cria o diretório 'som' se ele não existir
                        if not os.path.exists('som'):
                            os.makedirs('som')

                        # Salva o arquivo de áudio decodificado em formato webm na pasta 'som'
                        with open(f"som/{titulo}.webm", "wb") as f:
                            f.write(audio_data)

                        # Imprime a mensagem de conclusão
                        print("Download concluído e arquivo salvo em som/")
                        break
                    except:
                        print('Ocorreu uma excessão ao fazer Download, iniciando novamente!')

            def buscar_video(busca):
                results = SearchVideos(busca, offset=1, mode="json", max_results=1)
                info = json.loads(results.result())["search_result"][0]
                video_url = info["link"]
                thumbnail_url = info['thumbnails'][2]
                title = info["title"]
                return video_url

            urlvideo = buscar_video(f"{titulo} - {artista}")
            download_youtube_video(urlvideo, f'playwebm')

            print('FEZ O DOWNLOAD')

            self.manager.get_screen("carregamento").ids.progress_carregamento.value = 60
            self.manager.get_screen("carregamento").ids.label_progress.text = f'60%'

            def converter_audio_webm_para_ogg(arquivo_webm, arquivo_ogg):
                if platform == 'android':
                    # Define o comando de conversão
                    comando = f"-i {arquivo_webm} -c:v libx264 -c:a vorbis -strict -2 -q:a 4 -y {arquivo_ogg}"

                    # Executa o comando ffmpeg para converter o arquivo
                    Inicio.FFMPEG.Run(comando)

                else:
                    import subprocess
                    comando = f'ffmpeg -i {arquivo_webm} -c:v libx264 -c:a vorbis -strict -2 -q:a 4 -y {arquivo_ogg}'
                    subprocess.run(comando, shell=True)

            # Exemplo de uso da função
            sourceFileDir = os.path.dirname(os.path.abspath(__file__))
            somDir = os.path.join(sourceFileDir, "som")

            arquivo_webm = f'som/playwebm.webm'
            arquivo_ogg = f'som/{titulo_formatado}.ogg'
            converter_audio_webm_para_ogg(arquivo_webm, arquivo_ogg)

            self.manager.get_screen("carregamento").ids.progress_carregamento.value = 80
            self.manager.get_screen("carregamento").ids.label_progress.text = f'80%'

            self.manager.get_screen("inicio").ids.play.icon = 'pause'
            self.manager.get_screen("musicas").ids.play.icon = 'pause'
            self.manager.get_screen("pesquisar").ids.play.icon = 'pause'
            self.manager.get_screen("playlist").ids.play.icon = 'pause'
            self.manager.get_screen("search").ids.play.icon = 'pause'

            # obtém o caminho do diretório atual
            sourceFileDir = os.path.dirname(os.path.abspath(__file__))

            # obtém o caminho da pasta "som"
            somDir = os.path.join(sourceFileDir, "som")

            # obtém o caminho do arquivo "play1.ogg"
            playFile = os.path.join(somDir, f"{titulo_formatado}.ogg")

            Uri = Uri2
            PythonActivity = PythonActivity2
            player = player2

            if platform == 'android':
                if player.isPlaying():
                    player.stop()
                    player.reset()

                uri = Uri.parse('file://' + playFile)
                player.reset()
                player.setDataSource(PythonActivity.mActivity, uri)

                # Prepara o MediaPlayer para reprodução
                player.prepare()
                # Inicia a reprodução do áudio
                """position_ms = 50 * 1000
                player.seekTo(position_ms)"""

                # Obtém a duração do arquivo de áudio em milissegundos
                duration_ms = player.getDuration()

                # Converte a duração para segundos
                duration = duration_ms / 1000
                Inicio.tempo_musica = duration

                print(f"duração {duration}")


            else:
                self.sound = pygame.mixer.music.load(playFile)
                duration = pygame.mixer.Sound(playFile).get_length()
                Inicio.tempo_musica = duration

            if Inicio.position == 0:
                self.manager.get_screen("carregamento").ids.progress_carregamento.value = 100
                self.manager.get_screen("carregamento").ids.label_progress.text = f'100%'
                self.voltar_inicio()

                if platform == 'android':
                    player.start()
                else:
                    pygame.mixer.music.play()

            else:
                self.manager.get_screen("carregamento").ids.progress_carregamento.value = 100
                self.manager.get_screen("carregamento").ids.label_progress.text = f'100%'
                self.voltar_inicio()
                if platform == 'android':
                    player.seekTo(Inicio.position)
                    player.start()
                else:
                    pygame.mixer.music.play()
                    pygame.mixer.music.set_pos(Inicio.position)
                    print(Inicio.position)

            try:
                self.progress_bar_update.cancel()
            except:
                pass

            Inicio.position = -1
            stop_threads3 = False
            print(f'DURAÇÃO TOTALLLLLLL : {Inicio.tempo_musica}')

            Inicio.position = -1
            Inicio.numero_musica = n_audio

            def update_progress():
                while True:
                    if Inicio.mudanca_faixa_inicio or Musicas.mudanca_faixa_musica:
                        break
                    print(Inicio.numero_musica)
                    time.sleep(1)
                    if Inicio.position >= int(Inicio.tempo_musica):
                        numero = int(Inicio.numero_musica)
                        if numero <= 5:
                            if int(numero) < 5:
                                numero += 1
                            elif numero == 5:
                                numero = 1
                            if numero == 1:
                                titulo1 = self.manager.get_screen("search").ids.titulo0.text
                                artista1 = ''
                                image1 = self.manager.get_screen("search").ids.imagem0.source

                                self.play_modify(titulo1, artista1, f'{numero}', image1)
                                self.play(titulo1, artista1, f'{numero}', image1)

                            if numero == 2:
                                titulo1 = self.manager.get_screen("search").ids.titulo1.text
                                artista1 = ''
                                image1 = self.manager.get_screen("search").ids.imagem1.source

                                self.play_modify(titulo1, artista1, f'{numero}', image1)
                                self.play(titulo1, artista1, f'{numero}', image1)

                            if numero == 3:
                                titulo1 = self.manager.get_screen("search").ids.titulo2.text
                                artista1 = ''
                                image1 = self.manager.get_screen("search").ids.imagem2.source

                                self.play_modify(titulo1, artista1, f'{numero}', image1)
                                self.play(titulo1, artista1, f'{numero}', image1)

                            if numero == 4:
                                titulo1 = self.manager.get_screen("search").ids.titulo3.text
                                artista1 = ''
                                image1 = self.manager.get_screen("search").ids.imagem3.source

                                self.play_modify(titulo1, artista1, f'{numero}', image1)
                                self.play(titulo1, artista1, f'{numero}', image1)
                            if numero == 5:
                                titulo1 = self.manager.get_screen("search").ids.titulo4.text
                                artista1 = ''
                                image1 = self.manager.get_screen("search").ids.imagem4.source

                                self.play_modify(titulo1, artista1, f'{numero}', image1)
                                self.play(titulo1, artista1, f'{numero}', image1)

                            if numero == 6:
                                titulo1 = self.manager.get_screen("search").ids.titulo5.text
                                artista1 = ''
                                image1 = self.manager.get_screen("search").ids.imagem5.source

                                self.play_modify(titulo1, artista1, f'{numero}', image1)
                                self.play(titulo1, artista1, f'{numero}', image1)

                    else:
                        pass

            if Search.stop_threads3 == False:
                Inicio.progress_bar_update = threading.Thread(target=update_progress).start()
            if Search.stop_threads3 == False:
                Inicio.progress_bar_update = threading.Thread(target=self.update_progress).start()

    @mainthread
    def voltar_inicio(self):
        self.manager.current = 'search'
        self.manager.transition.direction = 'left'

    def update_progress(self):
        try:
            while True:
                if Inicio.mudanca_faixa_inicio or Musicas.mudanca_faixa_musica:
                    Search.stop_threads3 = False
                    break
                self.manager.get_screen("inicio").ids.progress_bar.max = Inicio.tempo_musica
                self.manager.get_screen("musicas").ids.progress_bar.max = Inicio.tempo_musica
                self.manager.get_screen("pesquisar").ids.progress_bar.max = Inicio.tempo_musica
                self.manager.get_screen("playlist").ids.progress_bar.max = Inicio.tempo_musica
                self.manager.get_screen("search").ids.progress_bar.max = Inicio.tempo_musica
                print('TA AQUI DENTRO!')
                Search.stop_threads3 = True
                time.sleep(1)
                Inicio.position += 1
                if Inicio.progress_bar_valor_novo != 0:
                    if self.manager.current == 'inicio':
                        self.manager.get_screen("inicio").ids.progress_bar.value = Inicio.progress_bar_valor_novo
                    elif self.manager.current == 'musicas':
                        self.manager.get_screen("musicas").ids.progress_bar.value = Inicio.progress_bar_valor_novo
                    elif self.manager.current == 'pesquisar':
                        self.manager.get_screen("pesquisar").ids.progress_bar.value = Inicio.progress_bar_valor_novo
                    elif self.manager.current == 'playlist':
                        self.manager.get_screen("playlist").ids.progress_bar.value = Inicio.progress_bar_valor_novo
                    elif self.manager.current == 'search':
                        self.manager.get_screen("search").ids.progress_bar.value = Inicio.progress_bar_valor_novo

                    Inicio.position = Inicio.progress_bar_valor_novo
                    if platform == 'android':
                        player2.seekTo(Inicio.progress_bar_valor_novo * 1000)

                    else:
                        pygame.mixer.music.set_pos(Inicio.progress_bar_valor_novo)

                    Inicio.progress_bar_valor_novo = 0

                if Inicio.position >= int(Inicio.tempo_musica):
                    self.manager.get_screen("inicio").ids.progress_bar.value = 0
                    self.manager.get_screen("musicas").ids.progress_bar.value = 0
                    self.manager.get_screen("pesquisar").ids.progress_bar.value = 0
                    self.manager.get_screen("playlist").ids.progress_bar.value = 0
                    self.manager.get_screen("search").ids.progress_bar.value = 0
                else:
                    self.manager.get_screen("inicio").ids.progress_bar.value = Inicio.position
                    self.manager.get_screen("musicas").ids.progress_bar.value = Inicio.position
                    self.manager.get_screen("pesquisar").ids.progress_bar.value = Inicio.position
                    self.manager.get_screen("playlist").ids.progress_bar.value = Inicio.position
                    self.manager.get_screen("search").ids.progress_bar.value = Inicio.position
        except:
            pass

    @mainthread
    def play_modify(self, titulo, artista, n_audio, source):
        self.manager.get_screen("inicio").ids.nome_musica.text = titulo
        self.manager.get_screen("inicio").ids.nome_artista.text = artista
        self.manager.get_screen("inicio").ids.image_musica.source = source
        if n_audio == '1':

            if Inicio.ultimo_audio != None:
                if int(Inicio.ultimo_audio) <= 5:
                    icone = "icone0" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("search").ids[icone].icon == "equalizer":
                        self.manager.get_screen("search").ids[icone].icon = "play"
                        self.manager.get_screen("search").ids.icone0.icon = 'equalizer'
            else:
                self.manager.get_screen("search").ids.icone0.icon = 'equalizer'



        elif n_audio == '2':

            if Inicio.ultimo_audio != None:
                if int(Inicio.ultimo_audio) <= 5:
                    playbrasil = "playbrasil" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playbrasil].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playbrasil].icon = "play"
                        self.manager.get_screen("inicio").ids.playbrasil2.icon = 'equalizer'
                else:
                    playmundo = "playmundo" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playmundo].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playmundo].icon = "play"
                        self.manager.get_screen("inicio").ids.playbrasil2.icon = 'equalizer'
            else:
                self.manager.get_screen("inicio").ids.playbrasil2.icon = 'equalizer'


        elif n_audio == '3':

            if Inicio.ultimo_audio != None:
                if int(Inicio.ultimo_audio) <= 5:
                    playbrasil = "playbrasil" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playbrasil].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playbrasil].icon = "play"
                        self.manager.get_screen("inicio").ids.playbrasil3.icon = 'equalizer'
                else:
                    playmundo = "playmundo" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playmundo].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playmundo].icon = "play"
                        self.manager.get_screen("inicio").ids.playbrasil3.icon = 'equalizer'
            else:
                self.manager.get_screen("inicio").ids.playbrasil3.icon = 'equalizer'

        elif n_audio == '4':

            if Inicio.ultimo_audio != None:
                if int(Inicio.ultimo_audio) <= 5:
                    playbrasil = "playbrasil" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playbrasil].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playbrasil].icon = "play"
                        self.manager.get_screen("inicio").ids.playbrasil4.icon = 'equalizer'
                else:
                    playmundo = "playmundo" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playmundo].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playmundo].icon = "play"
                        self.manager.get_screen("inicio").ids.playbrasil4.icon = 'equalizer'
            else:
                self.manager.get_screen("inicio").ids.playbrasil4.icon = 'equalizer'

        elif n_audio == '5':

            if Inicio.ultimo_audio != None:
                if int(Inicio.ultimo_audio) <= 5:
                    playbrasil = "playbrasil" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playbrasil].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playbrasil].icon = "play"
                        self.manager.get_screen("inicio").ids.playbrasil5.icon = 'equalizer'
                else:
                    playmundo = "playmundo" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playmundo].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playmundo].icon = "play"
                        self.manager.get_screen("inicio").ids.playbrasil5.icon = 'equalizer'
            else:
                self.manager.get_screen("inicio").ids.playbrasil5.icon = 'equalizer'

        elif n_audio == '6':

            if Inicio.ultimo_audio != None:
                if int(Inicio.ultimo_audio) <= 5:
                    playbrasil = "playbrasil" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playbrasil].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playbrasil].icon = "play"
                        self.manager.get_screen("inicio").ids.playmundo6.icon = 'equalizer'
                else:
                    playmundo = "playmundo" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playmundo].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playmundo].icon = "play"
                        self.manager.get_screen("inicio").ids.playmundo6.icon = 'equalizer'
            else:
                self.manager.get_screen("inicio").ids.playmundo6.icon = 'equalizer'

        elif n_audio == '7':

            if Inicio.ultimo_audio != None:
                if int(Inicio.ultimo_audio) <= 5:
                    playbrasil = "playbrasil" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playbrasil].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playbrasil].icon = "play"
                        self.manager.get_screen("inicio").ids.playmundo7.icon = 'equalizer'
                else:
                    playmundo = "playmundo" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playmundo].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playmundo].icon = "play"
                        self.manager.get_screen("inicio").ids.playmundo7.icon = 'equalizer'
            else:
                self.manager.get_screen("inicio").ids.playmundo7.icon = 'equalizer'

        elif n_audio == '8':

            if Inicio.ultimo_audio != None:
                if int(Inicio.ultimo_audio) <= 5:
                    playbrasil = "playbrasil" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playbrasil].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playbrasil].icon = "play"
                        self.manager.get_screen("inicio").ids.playmundo8.icon = 'equalizer'
                else:
                    playmundo = "playmundo" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playmundo].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playmundo].icon = "play"
                        self.manager.get_screen("inicio").ids.playmundo8.icon = 'equalizer'
            else:
                self.manager.get_screen("inicio").ids.playmundo8.icon = 'equalizer'

        elif n_audio == '9':

            if Inicio.ultimo_audio != None:
                if int(Inicio.ultimo_audio) <= 5:
                    playbrasil = "playbrasil" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playbrasil].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playbrasil].icon = "play"
                        self.manager.get_screen("inicio").ids.playmundo9.icon = 'equalizer'
                else:
                    playmundo = "playmundo" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playmundo].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playmundo].icon = "play"
                        self.manager.get_screen("inicio").ids.playmundo9.icon = 'equalizer'
            else:
                self.manager.get_screen("inicio").ids.playmundo9.icon = 'equalizer'

        elif n_audio == '10':

            if Inicio.ultimo_audio != None:
                if int(Inicio.ultimo_audio) <= 5:
                    playbrasil = "playbrasil" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playbrasil].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playbrasil].icon = "play"
                        self.manager.get_screen("inicio").ids.playmundo10.icon = 'equalizer'
                else:
                    playmundo = "playmundo" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playmundo].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playmundo].icon = "play"
                        self.manager.get_screen("inicio").ids.playmundo10.icon = 'equalizer'
            else:
                self.manager.get_screen("inicio").ids.playmundo10.icon = 'equalizer'

        Inicio.ultimo_audio = n_audio

    @mainthread
    def play(self, titulo, artista, n_audio, source):
        Search.mudanca_faixa_search = True
        Musicas.mudanca_faixa_musica = False
        Inicio.mudanca_faixa_inicio = False
        self.manager.get_screen("inicio").ids.scroll.pos_hint = {'center_x': 0.53, 'top': 0.23}
        self.manager.get_screen("pesquisar").ids.scroll.pos_hint = {'center_x': 0.53, 'top': 0.23}
        self.manager.get_screen("playlist").ids.scroll.pos_hint = {'center_x': 0.53, 'top': 0.23}
        self.manager.get_screen("musicas").ids.scroll.pos_hint = {'center_x': 0.53, 'top': 0.23}
        self.manager.get_screen("search").ids.scroll.pos_hint = {'center_x': 0.53, 'top': 0.23}

        threading.Thread(target=self.thd_play, args=(titulo, artista, n_audio)).start()
        self.manager.get_screen("carregamento").ids.progress_carregamento.value = 0
        self.manager.get_screen(
            "carregamento").ids.label_progress_info.text = f'Carregando música aguarde, nosso servidor é limitado!'
        self.manager.get_screen("carregamento").ids.label_progress.text = f'10%'
        self.manager.current = 'carregamento'
        self.manager.transition.direction = 'left'

        self.manager.get_screen("inicio").ids.nome_musica.text = titulo
        self.manager.get_screen("inicio").ids.nome_artista.text = artista
        self.manager.get_screen("inicio").ids.image_musica.source = source

        self.manager.get_screen("musicas").ids.nome_musica.text = titulo
        self.manager.get_screen("musicas").ids.nome_artista.text = artista
        self.manager.get_screen("musicas").ids.image_musica.source = source

        self.manager.get_screen("pesquisar").ids.nome_musica.text = titulo
        self.manager.get_screen("pesquisar").ids.nome_artista.text = artista
        self.manager.get_screen("pesquisar").ids.image_musica.source = source

        self.manager.get_screen("playlist").ids.nome_musica.text = titulo
        self.manager.get_screen("playlist").ids.nome_artista.text = artista
        self.manager.get_screen("playlist").ids.image_musica.source = source

        self.manager.get_screen("search").ids.nome_musica.text = titulo
        self.manager.get_screen("search").ids.nome_artista.text = artista
        self.manager.get_screen("search").ids.image_musica.source = source

        # PASSAR A REFERENCIA PARA O PLAY_STOP
        texto = f"{titulo} {artista}"
        titulo_formatado = re.sub(r'[^a-zA-Z0-9_]', '_', texto)

        self.manager.get_screen("inicio").ids.n_audio.text = titulo_formatado

        if n_audio == '1':

            if Inicio.ultimo_audio != None:
                if int(Inicio.ultimo_audio) <= 5:
                    playbrasil = "playbrasil" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playbrasil].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playbrasil].icon = "play"
                        self.manager.get_screen("inicio").ids.playbrasil1.icon = 'equalizer'
                else:
                    playmundo = "playmundo" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playmundo].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playmundo].icon = "play"
                        self.manager.get_screen("inicio").ids.playbrasil1.icon = 'equalizer'
            else:
                self.manager.get_screen("inicio").ids.playbrasil1.icon = 'equalizer'



        elif n_audio == '2':

            if Inicio.ultimo_audio != None:
                if int(Inicio.ultimo_audio) <= 5:
                    playbrasil = "playbrasil" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playbrasil].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playbrasil].icon = "play"
                        self.manager.get_screen("inicio").ids.playbrasil2.icon = 'equalizer'
                else:
                    playmundo = "playmundo" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playmundo].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playmundo].icon = "play"
                        self.manager.get_screen("inicio").ids.playbrasil2.icon = 'equalizer'
            else:
                self.manager.get_screen("inicio").ids.playbrasil2.icon = 'equalizer'


        elif n_audio == '3':

            if Inicio.ultimo_audio != None:
                if int(Inicio.ultimo_audio) <= 5:
                    playbrasil = "playbrasil" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playbrasil].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playbrasil].icon = "play"
                        self.manager.get_screen("inicio").ids.playbrasil3.icon = 'equalizer'
                else:
                    playmundo = "playmundo" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playmundo].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playmundo].icon = "play"
                        self.manager.get_screen("inicio").ids.playbrasil3.icon = 'equalizer'
            else:
                self.manager.get_screen("inicio").ids.playbrasil3.icon = 'equalizer'

        elif n_audio == '4':

            if Inicio.ultimo_audio != None:
                if int(Inicio.ultimo_audio) <= 5:
                    playbrasil = "playbrasil" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playbrasil].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playbrasil].icon = "play"
                        self.manager.get_screen("inicio").ids.playbrasil4.icon = 'equalizer'
                else:
                    playmundo = "playmundo" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playmundo].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playmundo].icon = "play"
                        self.manager.get_screen("inicio").ids.playbrasil4.icon = 'equalizer'
            else:
                self.manager.get_screen("inicio").ids.playbrasil4.icon = 'equalizer'

        elif n_audio == '5':

            if Inicio.ultimo_audio != None:
                if int(Inicio.ultimo_audio) <= 5:
                    playbrasil = "playbrasil" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playbrasil].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playbrasil].icon = "play"
                        self.manager.get_screen("inicio").ids.playbrasil5.icon = 'equalizer'
                else:
                    playmundo = "playmundo" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playmundo].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playmundo].icon = "play"
                        self.manager.get_screen("inicio").ids.playbrasil5.icon = 'equalizer'
            else:
                self.manager.get_screen("inicio").ids.playbrasil5.icon = 'equalizer'

        elif n_audio == '6':

            if Inicio.ultimo_audio != None:
                if int(Inicio.ultimo_audio) <= 5:
                    playbrasil = "playbrasil" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playbrasil].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playbrasil].icon = "play"
                        self.manager.get_screen("inicio").ids.playmundo6.icon = 'equalizer'
                else:
                    playmundo = "playmundo" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playmundo].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playmundo].icon = "play"
                        self.manager.get_screen("inicio").ids.playmundo6.icon = 'equalizer'
            else:
                self.manager.get_screen("inicio").ids.playmundo6.icon = 'equalizer'

        elif n_audio == '7':

            if Inicio.ultimo_audio != None:
                if int(Inicio.ultimo_audio) <= 5:
                    playbrasil = "playbrasil" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playbrasil].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playbrasil].icon = "play"
                        self.manager.get_screen("inicio").ids.playmundo7.icon = 'equalizer'
                else:
                    playmundo = "playmundo" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playmundo].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playmundo].icon = "play"
                        self.manager.get_screen("inicio").ids.playmundo7.icon = 'equalizer'
            else:
                self.manager.get_screen("inicio").ids.playmundo7.icon = 'equalizer'

        elif n_audio == '8':

            if Inicio.ultimo_audio != None:
                if int(Inicio.ultimo_audio) <= 5:
                    playbrasil = "playbrasil" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playbrasil].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playbrasil].icon = "play"
                        self.manager.get_screen("inicio").ids.playmundo8.icon = 'equalizer'
                else:
                    playmundo = "playmundo" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playmundo].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playmundo].icon = "play"
                        self.manager.get_screen("inicio").ids.playmundo8.icon = 'equalizer'
            else:
                self.manager.get_screen("inicio").ids.playmundo8.icon = 'equalizer'

        elif n_audio == '9':

            if Inicio.ultimo_audio != None:
                if int(Inicio.ultimo_audio) <= 5:
                    playbrasil = "playbrasil" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playbrasil].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playbrasil].icon = "play"
                        self.manager.get_screen("inicio").ids.playmundo9.icon = 'equalizer'
                else:
                    playmundo = "playmundo" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playmundo].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playmundo].icon = "play"
                        self.manager.get_screen("inicio").ids.playmundo9.icon = 'equalizer'
            else:
                self.manager.get_screen("inicio").ids.playmundo9.icon = 'equalizer'

        elif n_audio == '10':

            if Inicio.ultimo_audio != None:
                if int(Inicio.ultimo_audio) <= 5:
                    playbrasil = "playbrasil" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playbrasil].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playbrasil].icon = "play"
                        self.manager.get_screen("inicio").ids.playmundo10.icon = 'equalizer'
                else:
                    playmundo = "playmundo" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playmundo].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playmundo].icon = "play"
                        self.manager.get_screen("inicio").ids.playmundo10.icon = 'equalizer'
            else:
                self.manager.get_screen("inicio").ids.playmundo10.icon = 'equalizer'

        Inicio.ultimo_audio = n_audio





class Pesquisar(MDScreen):
    dynamic_ids = DictProperty({})
    contador = 0
    contador_musicas = 0

    contadorplay = 0
    contadormusica = 0
    progress_bar_update = None
    progress_bar_valor_novo = 0

    stop_threads = False
    tempo_musica = None
    numero_musica = None

    sound = None
    position = 0
    pygame.mixer.init()

    # progress_bar_valor_novo = 0
    reproduzidas = []
    url_videos = []

    ultimo_audio = None

    if platform == 'android':
        from jnius import autoclass
        FFMPEG = autoclass('com.sahib.pyff.ffpy')

    def search(self):
        self.manager.current = 'search'
        self.manager.transition.direction = 'left'

    def play_stop(self):
        if platform == 'android':
            if player2.isPlaying():
                player2.pause()
                self.manager.get_screen("inicio").ids.play.icon = 'play'
                self.manager.get_screen("musicas").ids.play.icon = 'play'
                self.manager.get_screen("pesquisar").ids.play.icon = 'play'
                self.manager.get_screen("playlist").ids.play.icon = 'play'
            else:
                player2.start()
                self.manager.get_screen("inicio").ids.play.icon = 'pause'
                self.manager.get_screen("musicas").ids.play.icon = 'pause'
                self.manager.get_screen("pesquisar").ids.play.icon = 'pause'
                self.manager.get_screen("playlist").ids.play.icon = 'pause'
        else:
            print('FUNCIONA APENAS NO ANDROID!')

    def click_barra(self, instance, touch):

        try:
            if instance.collide_point(touch.pos[0], touch.pos[1]):
                # calcula a posição da barra de progresso
                bar_x = instance.x
                bar_width = instance.width
                bar_pos = (touch.pos[0] - bar_x) / bar_width

                # verifica se a posição do toque está dentro dos limites da barra de progresso
                if 0 <= bar_pos <= 1:
                    # a posição do toque está dentro dos limites da barra de progresso
                    touch_pos = bar_pos * instance.max, touch.pos[1]
                    print("Clicado na posição:", touch_pos)
                    Inicio.progress_bar_valor_novo = (int(touch_pos[0]))

                    self.manager.get_screen("inicio").ids.progress_bar.value = Inicio.progress_bar_valor_novo
                    self.manager.get_screen("musicas").ids.progress_bar.value = Inicio.progress_bar_valor_novo
                    self.manager.get_screen("Inicio.").ids.progress_bar.value = Inicio.progress_bar_valor_novo
                    self.manager.get_screen("playlist").ids.progress_bar.value = Inicio.progress_bar_valor_novo

                    Inicio.position = Inicio.progress_bar_valor_novo
        except BaseException as e:
            print(f'Error no click_barra {e} ')

    def stop(self):
        self.manager.get_screen("inicio").ids.scroll.pos_hint = {'center_x': 0.53, 'top': 0.0}
        self.manager.get_screen("musicas").ids.scroll.pos_hint = {'center_x': 0.53, 'top': 0.0}
        self.manager.get_screen("pesquisar").ids.scroll.pos_hint = {'center_x': 0.53, 'top': 0.0}
        self.manager.get_screen("playlist").ids.scroll.pos_hint = {'center_x': 0.53, 'top': 0.0}
        if platform == 'android':
            if player2.isPlaying():
                player2.stop()
                player2.reset()
        else:
            pygame.mixer.music.unload()  # descarrega o arquivo de som

    @mainthread
    def voltar_inicio(self):
        self.manager.current = 'musicas'
        self.manager.transition.direction = 'left'

    def click_playlist(self, playlist, nome):
        self.manager.get_screen("playlist").ids.playlists.clear_widgets()
        dados_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "dados"))
        with open(os.path.join(dados_path, "playlists", f"{playlist}.txt"), "r", encoding="utf-8") as r:
            playlists = eval(r.read())

            self.manager.get_screen("carregamento").ids.progress_carregamento.value = 0
            self.manager.get_screen("carregamento").ids.progress_carregamento.max = int(len(playlists))
            self.manager.get_screen(
                "carregamento").ids.label_progress_info.text = f'Carregando Playlists aguarde, nosso servidor é limitado!'
            self.manager.get_screen("carregamento").ids.label_progress.text = f'10%'
            self.manager.current = 'carregamento'
            self.manager.transition.direction = 'left'
            self.contador = 0

            playlist_items = iter(playlists.items())
            playlist_len = len(playlists)

            def process_chunk(dt):
                self.contador += 1
                try:
                    playlist_id, playlist_info = next(playlist_items)
                except StopIteration:
                    # Todos os itens foram processados, cancele o agendamento
                    Clock.unschedule(process_chunk)

                    self.manager.get_screen("playlist").ids.nomeplay.text = f" Playlists populares ({nome})"
                    self.manager.get_screen("playlist").ids.nome_playlist.title = f"{nome}"
                    self.manager.get_screen("playlist").ids.scrollplaylist.scroll_y = 1  # SETAR PARA O TOPO
                    self.manager.current = 'playlist'
                    self.manager.transition.direction = 'left'

                    return

                nome_playlist = playlist_info["Nome da Playlist"]
                temas = playlist_info["Número de Temas"]
                imagem = playlist_info["URL da Imagem"]
                idplaylist = playlist_id

                card = MDCard(size_hint_y=None,
                              height='180dp',
                              radius=[5, ],
                              md_bg_color=get_color_from_hex('#121212'),
                              on_release=lambda a, id=idplaylist: Musicas.abrir_musica(self, id))
                self.manager.get_screen("carregamento").ids.progress_carregamento.value += 1
                # Atualize o texto do rótulo com a nova porcentagem
                porcentagem_atual = (self.contador / playlist_len) * 100
                self.manager.get_screen("carregamento").ids.label_progress.text = f"{int(porcentagem_atual)}%"

                floatlayout = MDFloatLayout()
                card.add_widget(floatlayout)
                asyncimages = FitImage(source=f"{imagem}",
                                       size_hint_y=None,
                                       height='110dp',
                                       pos_hint={'center_y': .7, 'center_x': .5})
                floatlayout.add_widget(asyncimages)

                titulo = MDLabel(text=f'{nome_playlist}',
                                 halign='center',
                                 font_style='Caption',
                                 bold=True,
                                 pos_hint={'center_y': .28, 'center_x': .5},
                                 theme_text_color="Custom",
                                 text_color=get_color_from_hex('#ffffff'))

                floatlayout.add_widget(titulo)

                faixas = MDLabel(text=f'{temas} Faixas de aúdio',
                                 halign='center',
                                 font_style='Caption',
                                 pos_hint={'center_y': .10, 'center_x': .5},
                                 theme_text_color="Custom",
                                 text_color=get_color_from_hex('#ffffff'))

                floatlayout.add_widget(faixas)

                self.manager.get_screen("playlist").ids.playlists.add_widget(card)

            Clock.schedule_interval(process_chunk, 0.01)


class Playlist(MDScreen):

    def play_stop(self):
        if platform == 'android':
            if player2.isPlaying():
                player2.pause()
                self.manager.get_screen("inicio").ids.play.icon = 'play'
                self.manager.get_screen("musicas").ids.play.icon = 'play'
                self.manager.get_screen("pesquisar").ids.play.icon = 'play'
                self.manager.get_screen("playlist").ids.play.icon = 'play'
            else:
                player2.start()
                self.manager.get_screen("inicio").ids.play.icon = 'pause'
                self.manager.get_screen("musicas").ids.play.icon = 'pause'
                self.manager.get_screen("pesquisar").ids.play.icon = 'pause'
                self.manager.get_screen("playlist").ids.play.icon = 'pause'
        else:
            print('FUNCIONA APENAS NO ANDROID!')

    def click_barra(self, instance, touch):
        if instance.collide_point(touch.pos[0], touch.pos[1]):
            # calcula a posição da barra de progresso
            bar_x = instance.x
            bar_width = instance.width
            bar_pos = (touch.pos[0] - bar_x) / bar_width

            # verifica se a posição do toque está dentro dos limites da barra de progresso
            if 0 <= bar_pos <= 1:
                # a posição do toque está dentro dos limites da barra de progresso
                touch_pos = bar_pos * instance.max, touch.pos[1]
                print("Clicado na posição:", touch_pos)
                Inicio.progress_bar_valor_novo = (int(touch_pos[0]))

                self.manager.get_screen("inicio").ids.progress_bar.value = Inicio.progress_bar_valor_novo
                self.manager.get_screen("musicas").ids.progress_bar.value = Inicio.progress_bar_valor_novo
                self.manager.get_screen("pesquisar").ids.progress_bar.value = Inicio.progress_bar_valor_novo
                self.manager.get_screen("playlist").ids.progress_bar.value = Inicio.progress_bar_valor_novo

                Inicio.position = Inicio.progress_bar_valor_novo

    def stop(self):
        self.manager.get_screen("inicio").ids.scroll.pos_hint = {'center_x': 0.53, 'top': 0.0}
        self.manager.get_screen("musicas").ids.scroll.pos_hint = {'center_x': 0.53, 'top': 0.0}
        self.manager.get_screen("pesquisar").ids.scroll.pos_hint = {'center_x': 0.53, 'top': 0.0}
        self.manager.get_screen("playlist").ids.scroll.pos_hint = {'center_x': 0.53, 'top': 0.0}
        if platform == 'android':
            if player2.isPlaying():
                player2.stop()
                player2.reset()
        else:
            pygame.mixer.music.unload()  # descarrega o arquivo de som

    def voltar(self):
        self.manager.current = 'pesquisar'
        self.manager.transition.direction = 'right'


class Login(MDScreen):
    dynamic_ids = DictProperty({})

    def trocar_image(self):
        imagens = ['imagens/login1.jpg', 'imagens/login2.jpg', 'imagens/login3.jpg', 'imagens/login4.jpg']
        imagem_source = random.choice(imagens)
        screen_manager = App.get_running_app().root
        screen_manager.get_screen("login").ids.imageminicial.source = imagem_source

    def iniciar(self):
        self.manager.current = 'carregamento'
        self.manager.transition.direction = 'left'
        threading.Thread(target=self.thd_carregar_musica).start()
        self.func()

    def func(self):
        print('ENTROU AQUI@')
        if platform == 'android':
            import os
            from jnius import autoclass

            """# Importa as classes necessárias do Android
            MediaPlayer = autoclass('android.media.MediaPlayer')
            Uri = autoclass('android.net.Uri')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')

            # Cria um novo objeto MediaPlayer
            player = MediaPlayer()

            # Define a fonte de áudio para o arquivo especificado
            file_path = os.path.abspath('som1.ogg')
            uri = Uri.parse('file://' + file_path)
            player.setDataSource(PythonActivity.mActivity, uri)

            # Prepara o MediaPlayer para reprodução
            player.prepare()

            # Inicia a reprodução do áudio
            position_ms = 50 * 1000
            player.seekTo(position_ms)
            player.start()"""

    @mainthread
    def voltar_inicio(self):
        if Inicio.vermaiscount:
            self.manager.current = 'musicas'
            self.manager.transition.direction = 'left'
        else:
            self.manager.current = 'inicio'
            self.manager.transition.direction = 'left'

    def thd_carregar_musica(self):
        with open('dados/playlists/populares.txt', 'r', encoding='utf-8') as populares:
            lista_populares = eval(populares.read())
        try:
            with open(f'dados/musica_brasil_log.txt', 'r', encoding='utf-8') as brasil:
                lista_brasil = eval(brasil.read())

            with open(f'dados/musica_internacional.txt', 'r', encoding='utf-8') as mundo:
                lista_mundo = eval(mundo.read())
        except:
            print('error!!!!')
            if not os.path.exists('dados'):
                os.makedirs('dados')
            musicas = [
                {"musica": "musica1", "artista": "artista1", "imagem": "imagem1", "url": "url"},
                {"musica": "musica2", "artista": "artista2", "imagem": "imagem2", "url": "url"},
                {"musica": "musica3", "artista": "artista3", "imagem": "imagem3", "url": "url"},
                {"musica": "musica4", "artista": "artista4", "imagem": "imagem4", "url": "url"},
                {"musica": "musica5", "artista": "artista5", "imagem": "imagem5", "url": "url"}
            ]
            with open(f'dados/musica_brasil_log.txt', 'w', encoding='utf-8') as g:
                lista_brasil = g.write(str(musicas))

            with open(f'dados/musica_internacional.txt', 'w', encoding='utf-8') as mg:
                lista_brasil = mg.write(str(musicas))

            with open(f'dados/musica_brasil_log.txt', 'r', encoding='utf-8') as brasil:
                lista_brasil = eval(brasil.read())

            with open(f'dados/musica_internacional.txt', 'r', encoding='utf-8') as mundo:
                lista_mundo = eval(mundo.read())

                print(lista_mundo)

        primeiras_musicas = list(lista_populares.keys())[:20]

        # Seleciona aleatoriamente até 5 músicas dessa lista
        playlist_populares = random.sample(primeiras_musicas, k=min(5, len(primeiras_musicas)))

        contadorplaylist = 0
        # Percorrer as chaves aleatórias e exibir as informações correspondentes
        for chave in playlist_populares:
            contadorplaylist += 1
            titulo_playlist = "titulo_playlist" + str(contadorplaylist)
            n_playlist = "n_playlist" + str(contadorplaylist)
            sources = "source_playlist" + str(contadorplaylist)
            playlist = lista_populares[chave]
            iconbutton = "abrir_playlist" + str(contadorplaylist)
            self.manager.get_screen("inicio").ids[titulo_playlist].text = playlist['Nome da Playlist']
            self.manager.get_screen("inicio").ids[n_playlist].text = playlist['Número de Temas'] + str(
                'Faixas de áudio')
            self.manager.get_screen("inicio").ids[sources].source = playlist['URL da Imagem']
            self.manager.get_screen("inicio").ids[iconbutton].on_release = functools.partial(Inicio.vermais, self,
                                                                                             chave)

            print("ID:", chave)
            print()

        contador = 0
        # Iterate over the results

        porcentagem = 0

        pasta_atual = os.getcwd()

        url = "https://api.deezer.com/chart/0/tracks"

        params = {
            "limit": 10,
            "index": 0
        }

        response = requests.get(url, params=params)

        data = response.json()
        for track in data["data"]:
            contador += 1

            porcentagem += 10
            self.manager.get_screen("carregamento").ids.progress_carregamento.value = porcentagem
            self.manager.get_screen("carregamento").ids.label_progress.text = f'{porcentagem}%'

            # Get the song title
            song_title = track["title"]

            # Get the artist name
            artist_name = track["artist"]["name"]

            def buscar_video(busca):
                if lista_brasil[int(contador) - 1]["musica"] == song_title:
                    print('dentro!')
                    thumbnail_url = lista_brasil[int(contador) - 1]["imagem"]
                    video_url = lista_brasil[int(contador) - 1]["url"]
                    Inicio.url_videos.append(video_url)

                    texto = f"{song_title} {artist_name}"
                    titulo_formatado = re.sub(r'[^a-zA-Z0-9_]', '_', texto)

                    playbrasil = "playbrasil" + str(contador)
                    titulobrasil = "titulo_brasil" + str(contador)
                    artistabrasil = "artista_brasil" + str(contador)
                    thumbrasil = "source_brasil" + str(contador)

                    self.manager.get_screen("inicio").ids[titulobrasil].text = song_title
                    self.manager.get_screen("inicio").ids[artistabrasil].text = artist_name
                    time.sleep(0.1)
                    self.manager.get_screen("inicio").ids[thumbrasil].source = thumbnail_url

                    if os.path.exists(f"som/{titulo_formatado}.ogg") and os.path.isfile(f"som/{titulo_formatado}.ogg"):
                        self.manager.get_screen("inicio").ids[playbrasil].icon = 'play'
                    else:
                        self.manager.get_screen("inicio").ids[playbrasil].icon = 'download'

                else:
                    results = SearchVideos(busca, offset=1, mode="json", max_results=1)
                    info = json.loads(results.result())["search_result"][0]
                    video_url = info["link"]
                    thumbnail_url = info['thumbnails'][2]
                    title = info["title"]

                    Inicio.url_videos.append(video_url)

                    texto = f"{song_title} {artist_name}"
                    titulo_formatado = re.sub(r'[^a-zA-Z0-9_]', '_', texto)

                    playbrasil = "playbrasil" + str(contador)
                    titulobrasil = "titulo_brasil" + str(contador)
                    artistabrasil = "artista_brasil" + str(contador)
                    thumbrasil = "source_brasil" + str(contador)

                    self.manager.get_screen("inicio").ids[titulobrasil].text = song_title
                    self.manager.get_screen("inicio").ids[artistabrasil].text = artist_name
                    self.manager.get_screen("inicio").ids[thumbrasil].source = thumbnail_url

                    if os.path.exists(f"som/{titulo_formatado}.ogg") and os.path.isfile(f"som/{titulo_formatado}.ogg"):
                        self.manager.get_screen("inicio").ids[playbrasil].icon = 'play'
                    else:
                        self.manager.get_screen("inicio").ids[playbrasil].icon = 'download'

                    lista_brasil[int(contador) - 1]["musica"] = song_title
                    lista_brasil[int(contador) - 1]["artista"] = artist_name
                    lista_brasil[int(contador) - 1]["imagem"] = thumbnail_url
                    lista_brasil[int(contador) - 1]["url"] = video_url

                    with open(f'dados/musica_brasil_log.txt', 'w', encoding='utf-8') as brasilgravar:
                        brasilgravar.write(str(lista_brasil))

                if porcentagem == 10:
                    self.manager.get_screen(
                        "carregamento").ids.label_progress_info.text = 'Carregando músicas aguarde.'
                elif porcentagem == 20:
                    self.manager.get_screen(
                        "carregamento").ids.label_progress_info.text = 'Desculpe a demora nosso servidor é limitado.'
                elif porcentagem == 30:
                    self.manager.get_screen("carregamento").ids.label_progress_info.text = 'Carregando tendências.'
                elif porcentagem == 40:
                    self.manager.get_screen("carregamento").ids.label_progress_info.text = 'Carregando Play Lists.'
                else:
                    self.manager.get_screen(
                        "carregamento").ids.label_progress_info.text = 'Carregando músicas aguarde.'

                # download_youtube_video(video_url, f'play{contador}')

            print(f'{song_title} {artist_name}')
            try:
                buscar_video(f'{song_title} {artist_name}')
            except BaseException as e:
                print(e)

            if contador == 5:
                break
        contadormundo = 0
        url = 'https://www.billboard.com/charts/hot-100/'
        response = requests.get(url)

        # Parse the HTML response with Beautiful Soup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all of the `div` elements with the class `o-chart-results-list-row-container`
        results = soup.find_all('div', class_='o-chart-results-list-row-container')
        # Iterate over the results
        for result in results:
            contador += 1
            contadormundo += 1
            porcentagem += 10
            print(porcentagem)
            self.manager.get_screen("carregamento").ids.progress_carregamento.value = porcentagem
            self.manager.get_screen("carregamento").ids.label_progress.text = f'{porcentagem}%'

            # Get the song title
            song_title = result.find('h3').text.strip()

            # Get the artist name
            artist_name = result.find('h3').find_next('span').text.strip()

            # print(f'({contador}) {song_title} > {artist_name}')

            ### FUNÇÃO PARA BAIXAR YOUTUBE>:

            def buscar_video(busca):

                if lista_mundo[int(contadormundo) - 1]["musica"] == song_title:
                    thumbnail_url = lista_mundo[int(contadormundo) - 1]["imagem"]
                    video_url = lista_mundo[int(contadormundo) - 1]["url"]
                    Inicio.url_videos.append(video_url)

                    texto = f"{song_title} {artist_name}"
                    titulo_formatado = re.sub(r'[^a-zA-Z0-9_]', '_', texto)

                    playmundo = "playmundo" + str(contador)
                    titulomundo = "titulo_mundo" + str(contadormundo)
                    artistamundo = "artista_mundo" + str(contadormundo)
                    thummundo = "source_mundo" + str(contadormundo)

                    self.manager.get_screen("inicio").ids[titulomundo].text = song_title
                    self.manager.get_screen("inicio").ids[artistamundo].text = artist_name
                    time.sleep(0.1)
                    self.manager.get_screen("inicio").ids[thummundo].source = thumbnail_url

                    if os.path.exists(f"som/{titulo_formatado}.ogg") and os.path.isfile(f"som/{titulo_formatado}.ogg"):
                        self.manager.get_screen("inicio").ids[playmundo].icon = 'play'
                    else:
                        self.manager.get_screen("inicio").ids[playmundo].icon = 'download'

                else:
                    results = SearchVideos(busca, offset=1, mode="json", max_results=1)
                    info = json.loads(results.result())["search_result"][0]
                    video_url = info["link"]
                    thumbnail_url = info['thumbnails'][2]
                    title = info["title"]

                    Inicio.url_videos.append(video_url)

                    texto = f"{song_title} {artist_name}"
                    titulo_formatado = re.sub(r'[^a-zA-Z0-9_]', '_', texto)

                    playmundo = "playmundo" + str(contador)
                    titulomundo = "titulo_mundo" + str(contadormundo)
                    artistamundo = "artista_mundo" + str(contadormundo)
                    thummundo = "source_mundo" + str(contadormundo)

                    self.manager.get_screen("inicio").ids[titulomundo].text = song_title
                    self.manager.get_screen("inicio").ids[artistamundo].text = artist_name
                    self.manager.get_screen("inicio").ids[thummundo].source = thumbnail_url

                    if os.path.exists(f"som/{titulo_formatado}.ogg") and os.path.isfile(f"som/{titulo_formatado}.ogg"):
                        self.manager.get_screen("inicio").ids[playmundo].icon = 'play'
                    else:
                        self.manager.get_screen("inicio").ids[playmundo].icon = 'download'

                    lista_mundo[int(contadormundo) - 1]["musica"] = song_title
                    lista_mundo[int(contadormundo) - 1]["artista"] = artist_name
                    lista_mundo[int(contadormundo) - 1]["imagem"] = thumbnail_url
                    lista_mundo[int(contadormundo) - 1]["url"] = video_url

                    with open(f'dados/musica_internacional.txt', 'w', encoding='utf-8') as mundogravar:
                        mundogravar.write(str(lista_mundo))
                        print('gravou!')

                if porcentagem == 60:
                    self.manager.get_screen(
                        "carregamento").ids.label_progress_info.text = 'Carregando músicas aguarde.'
                elif porcentagem == 70:
                    self.manager.get_screen(
                        "carregamento").ids.label_progress_info.text = 'Desculpe a demora nosso servidor é limitado.'
                elif porcentagem == 80:
                    self.manager.get_screen(
                        "carregamento").ids.label_progress_info.text = 'Carregando músicas no mundo.'
                elif porcentagem == 90:
                    self.manager.get_screen(
                        "carregamento").ids.label_progress_info.text = 'Carregando músicas no Brasil.'
                elif porcentagem == 100:
                    self.manager.get_screen("carregamento").ids.label_progress_info.text = 'Bem-Vindo(a)...'
                    self.voltar_inicio()

            print(f'{song_title} {artist_name}')
            try:
                buscar_video(f'{song_title} {artist_name}')
            except BaseException as e:
                print(e)

            if contador == 10:
                break


class Inicio(MDScreen):
    dynamic_ids = DictProperty({})
    contadorplay = 0
    contadormusica = 0
    contador_lenght = 0
    vermaiscount = False
    progress_bar_update = None
    sound = None
    position = 0
    pygame.mixer.init()

    stop_threads = False
    stop_threads2 = False
    tempo_musica = None
    numero_musica = None

    mudanca_faixa_inicio = False

    progress_bar_valor_novo = 0
    reproduzidas = []
    url_videos = []
    lista_arrastar = []

    ultimo_audio = None
    if platform == 'android':
        from jnius import autoclass
        FFMPEG = autoclass('com.sahib.pyff.ffpy')

    def vermais(self, id):
        print(Inicio.vermaiscount)
        Musicas.abrir_musica(self, id)
        Inicio.vermaiscount = True

        print(f"TESTE 01: {Inicio.vermaiscount}")

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):
            x = touch.pos[0]
            y = touch.pos[1]

            # print(self.manager.get_screen("inicio").ids.scroll.pos)

            if int(y) > 69 and int(y) < 175:
                print(len(Inicio.lista_arrastar))
                Inicio.lista_arrastar.append(int(x))

                maior_numero = max(Inicio.lista_arrastar)
                menor_numero = min(Inicio.lista_arrastar)

                if maior_numero - menor_numero >= 130:
                    print("A diferença entre o maior e o menor número é de pelo menos 70.")
                    self.manager.get_screen("inicio").ids.scroll.pos_hint = {'center_x': 0.53, 'top': 0.0}
                    pygame.mixer.music.unload()  # descarrega o arquivo de som
                    pass
                else:
                    # print("A diferença entre o maior e o menor número não é de pelo menos 70.")
                    pass

    def click_barra(self, instance, touch):

        try:
            if instance.collide_point(touch.pos[0], touch.pos[1]):
                # calcula a posição da barra de progresso
                bar_x = instance.x
                bar_width = instance.width
                bar_pos = (touch.pos[0] - bar_x) / bar_width

                # verifica se a posição do toque está dentro dos limites da barra de progresso
                if 0 <= bar_pos <= 1:
                    # a posição do toque está dentro dos limites da barra de progresso
                    touch_pos = bar_pos * instance.max, touch.pos[1]
                    print("Clicado na posição:", touch_pos)
                    Inicio.progress_bar_valor_novo = (int(touch_pos[0]))

                    self.manager.get_screen("inicio").ids.progress_bar.value = Inicio.progress_bar_valor_novo
                    self.manager.get_screen("musicas").ids.progress_bar.value = Inicio.progress_bar_valor_novo
                    self.manager.get_screen("pesquisar").ids.progress_bar.value = Inicio.progress_bar_valor_novo
                    self.manager.get_screen("playlist").ids.progress_bar.value = Inicio.progress_bar_valor_novo

                    Inicio.position = Inicio.progress_bar_valor_novo
        except BaseException as e:
            print(f'Error no click_barra {e} ')

    def play_stop(self):
        if platform == 'android':
            if player2.isPlaying():
                player2.pause()
                self.manager.get_screen("inicio").ids.play.icon = 'play'
                self.manager.get_screen("musicas").ids.play.icon = 'play'
                self.manager.get_screen("pesquisar").ids.play.icon = 'play'
                self.manager.get_screen("playlist").ids.play.icon = 'play'
            else:
                player2.start()
                self.manager.get_screen("inicio").ids.play.icon = 'pause'
                self.manager.get_screen("musicas").ids.play.icon = 'pause'
                self.manager.get_screen("pesquisar").ids.play.icon = 'pause'
                self.manager.get_screen("playlist").ids.play.icon = 'pause'
        else:
            print('FUNCIONA APENAS NO ANDROID!')

    def thd_play(self, titulo, artista, n_audio, source=None):
        Inicio.position = 0
        progress_bar_valor_novo = 0
        Inicio.contadorplay = 1
        pygame.mixer.music.unload()  # descarrega o arquivo de som
        print(Inicio.url_videos)
        Inicio.lista_arrastar = []
        print(f'Tamanho da lista: {Inicio.lista_arrastar}')

        texto = f"{titulo} {artista}"
        titulo_formatado = re.sub(r'[^a-zA-Z0-9_]', '_', texto)

        print(titulo_formatado)

        if os.path.exists(f"som/{titulo_formatado}.ogg") and os.path.isfile(f"som/{titulo_formatado}.ogg"):
            self.manager.get_screen("inicio").ids.scroll.pos_hint = {'center_x': 0.53, 'top': 0.23}

            self.manager.get_screen("carregamento").ids.progress_carregamento.value = 30
            self.manager.get_screen("carregamento").ids.label_progress.text = f'30%'

            self.manager.get_screen("carregamento").ids.progress_carregamento.value = 60
            self.manager.get_screen("carregamento").ids.label_progress.text = f'60%'

            self.manager.get_screen("carregamento").ids.progress_carregamento.value = 80
            self.manager.get_screen("carregamento").ids.label_progress.text = f'80%'

            self.manager.get_screen("inicio").ids.play.icon = 'pause'
            self.manager.get_screen("musicas").ids.play.icon = 'pause'
            self.manager.get_screen("pesquisar").ids.play.icon = 'pause'
            self.manager.get_screen("playlist").ids.play.icon = 'pause'

            # obtém o caminho do diretório atual
            sourceFileDir = os.path.dirname(os.path.abspath(__file__))

            # obtém o caminho da pasta "som"
            somDir = os.path.join(sourceFileDir, "som")

            # obtém o caminho do arquivo "play1.ogg"
            playFile = os.path.join(somDir, f"{titulo_formatado}.ogg")

            Uri = Uri2
            PythonActivity = PythonActivity2
            player = player2

            if platform == 'android':
                if player.isPlaying():
                    player.stop()
                    player.reset()

                uri = Uri.parse('file://' + playFile)
                player.reset()
                player.setDataSource(PythonActivity.mActivity, uri)

                # Prepara o MediaPlayer para reprodução
                player.prepare()
                # Inicia a reprodução do áudio
                """position_ms = 50 * 1000
                player.seekTo(position_ms)"""

                # Obtém a duração do arquivo de áudio em milissegundos
                duration_ms = player.getDuration()

                # Converte a duração para segundos
                duration = duration_ms / 1000
                Inicio.tempo_musica = duration

                print(f"duração {duration}")


            else:
                self.sound = pygame.mixer.music.load(playFile)
                duration = pygame.mixer.Sound(playFile).get_length()
                Inicio.tempo_musica = duration

            if Inicio.position == 0:
                self.manager.get_screen("carregamento").ids.progress_carregamento.value = 100
                self.manager.get_screen("carregamento").ids.label_progress.text = f'100%'
                self.voltar_inicio()

                if platform == 'android':
                    player.start()
                else:
                    pygame.mixer.music.play()

            else:
                self.manager.get_screen("carregamento").ids.progress_carregamento.value = 100
                self.manager.get_screen("carregamento").ids.label_progress.text = f'100%'
                self.voltar_inicio()
                if platform == 'android':
                    player.seekTo(Inicio.position)
                    player.start()
                else:
                    pygame.mixer.music.play()
                    pygame.mixer.music.set_pos(Inicio.position)
                    print(Inicio.position)

            # print(duration)

            try:
                self.progress_bar_update.cancel()
            except:
                pass

            Inicio.position = -1
            Inicio.numero_musica = n_audio

            def update_progress():
                while True:
                    if Inicio.mudanca_faixa_inicio:
                        break
                    print(Inicio.numero_musica)
                    time.sleep(1)
                    if Inicio.position >= int(Inicio.tempo_musica):
                        numero = int(Inicio.numero_musica)
                        if numero <= 5:
                            if int(numero) < 5:
                                numero += 1
                            elif numero == 5:
                                numero = 1
                            if numero == 1:
                                titulo1 = self.manager.get_screen("inicio").ids.titulo_brasil1.text
                                artista1 = self.manager.get_screen("inicio").ids.artista_brasil1.text
                                image1 = self.manager.get_screen("inicio").ids.source_brasil1.source

                                self.play_modify(titulo1, artista1, f'{numero}', image1)
                                self.play(titulo1, artista1, f'{numero}', image1)
                            if numero == 2:
                                titulo1 = self.manager.get_screen("inicio").ids.titulo_brasil2.text
                                artista1 = self.manager.get_screen("inicio").ids.artista_brasil2.text
                                image1 = self.manager.get_screen("inicio").ids.source_brasil2.source
                                print(artista1)

                                self.play_modify(titulo1, artista1, f'{numero}', image1)
                                self.play(titulo1, artista1, f'{numero}', image1)
                            elif numero == 3:
                                titulo1 = self.manager.get_screen("inicio").ids.titulo_brasil3.text
                                artista1 = self.manager.get_screen("inicio").ids.artista_brasil3.text
                                image1 = self.manager.get_screen("inicio").ids.source_brasil3.source

                                self.play_modify(titulo1, artista1, f'{numero}', image1)
                                self.play(titulo1, artista1, f'{numero}', image1)
                            elif numero == 4:
                                titulo1 = self.manager.get_screen("inicio").ids.titulo_brasil4.text
                                artista1 = self.manager.get_screen("inicio").ids.artista_brasil4.text
                                image1 = self.manager.get_screen("inicio").ids.source_brasil4.source

                                self.play_modify(titulo1, artista1, f'{numero}', image1)
                                self.play(titulo1, artista1, f'{numero}', image1)


                            elif numero == 5:
                                titulo1 = self.manager.get_screen("inicio").ids.titulo_brasil5.text
                                artista1 = self.manager.get_screen("inicio").ids.artista_brasil5.text
                                image1 = self.manager.get_screen("inicio").ids.source_brasil5.source

                                self.play_modify(titulo1, artista1, f'{numero}', image1)
                                self.play(titulo1, artista1, f'{numero}', image1)

                        elif numero > 5:
                            numero = int(Inicio.numero_musica)
                            if int(numero) < 10:
                                numero += 1

                            elif int(numero) == 10:
                                numero = 6
                            self.manager.get_screen("inicio").ids.n_audio.text = titulo_formatado
                            if numero == 6:
                                titulo1 = self.manager.get_screen("inicio").ids.titulo_mundo1.text
                                artista1 = self.manager.get_screen("inicio").ids.artista_mundo1.text
                                image1 = self.manager.get_screen("inicio").ids.source_mundo1.source

                                self.play_modify(titulo1, artista1, f'{numero}', image1)
                                self.play(titulo1, artista1, f'{numero}', image1)

                            elif numero == 7:
                                titulo1 = self.manager.get_screen("inicio").ids.titulo_mundo2.text
                                artista1 = self.manager.get_screen("inicio").ids.artista_mundo2.text
                                image1 = self.manager.get_screen("inicio").ids.source_mundo2.source

                                self.play_modify(titulo1, artista1, f'{numero}', image1)
                                self.play(titulo1, artista1, f'{numero}', image1)
                            elif numero == 8:
                                titulo1 = self.manager.get_screen("inicio").ids.titulo_mundo3.text
                                artista1 = self.manager.get_screen("inicio").ids.artista_mundo3.text
                                image1 = self.manager.get_screen("inicio").ids.source_mundo3.source

                                self.play_modify(titulo1, artista1, f'{numero}', image1)
                                self.play(titulo1, artista1, f'{numero}', image1)
                            elif numero == 9:
                                titulo1 = self.manager.get_screen("inicio").ids.titulo_mundo4.text
                                artista1 = self.manager.get_screen("inicio").ids.artista_mundo4.text
                                image1 = self.manager.get_screen("inicio").ids.source_mundo4.source

                                self.play_modify(titulo1, artista1, f'{numero}', image1)
                                self.play(titulo1, artista1, f'{numero}', image1)
                            elif numero == 10:
                                titulo1 = self.manager.get_screen("inicio").ids.titulo_mundo5.text
                                artista1 = self.manager.get_screen("inicio").ids.artista_mundo5.text
                                image1 = self.manager.get_screen("inicio").ids.source_mundo5.source

                                self.play_modify(titulo1, artista1, f'{numero}', image1)
                                self.play(titulo1, artista1, f'{numero}', image1)

                    else:
                        pass

            if Inicio.stop_threads2 == False:
                Inicio.progress_bar_update = threading.Thread(target=update_progress).start()
            if Inicio.stop_threads2 == False:
                Inicio.progress_bar_update = threading.Thread(target=self.update_progress).start()



        else:
            print("O arquivo não existe na pasta raiz do projeto.")

            self.manager.get_screen("inicio").ids.scroll.pos_hint = {'center_x': 0.53, 'top': 0.23}

            self.manager.get_screen("carregamento").ids.progress_carregamento.value = 30
            self.manager.get_screen("carregamento").ids.label_progress.text = f'30%'

            def download_youtube_video(video_url, titulo='playwebm'):
                while True:
                    try:
                        # Cria uma instância do objeto YouTube
                        video = YouTube(video_url)

                        # Seleciona o formato de áudio desejado (webm ou m4a)
                        audio_format = "webm"  # ou "m4a"

                        # Seleciona a faixa de áudio com a maior qualidade disponível
                        audio = video.streams.filter(only_audio=True, file_extension=audio_format).order_by(
                            'abr').desc().first()

                        # Baixa o arquivo de áudio como bytes
                        audio_bytes = io.BytesIO()
                        audio.stream_to_buffer(audio_bytes)

                        # Decodifica a representação em base64 para obter os dados binários do arquivo de áudio
                        audio_data = audio_bytes.getvalue()

                        # Cria o diretório 'som' se ele não existir
                        if not os.path.exists('som'):
                            os.makedirs('som')

                        # Salva o arquivo de áudio decodificado em formato webm na pasta 'som'
                        with open(f"som/{titulo}.webm", "wb") as f:
                            f.write(audio_data)

                        # Imprime a mensagem de conclusão
                        print("Download concluído e arquivo salvo em som/")
                        break
                    except:
                        print('Ocorreu uma excessão ao fazer Download, iniciando novamente!')

            download_youtube_video(Inicio.url_videos[int(n_audio) - 1], f'playwebm')
            print('FEZ O DOWNLOAD')

            self.manager.get_screen("carregamento").ids.progress_carregamento.value = 60
            self.manager.get_screen("carregamento").ids.label_progress.text = f'60%'

            def converter_audio_webm_para_ogg(arquivo_webm, arquivo_ogg):
                if platform == 'android':
                    # Define o comando de conversão
                    comando = f"-i {arquivo_webm} -c:v libx264 -c:a vorbis -strict -2 -q:a 4 -y {arquivo_ogg}"

                    # Executa o comando ffmpeg para converter o arquivo
                    Inicio.FFMPEG.Run(comando)

                else:
                    import subprocess
                    comando = f'ffmpeg -i {arquivo_webm} -c:v libx264 -c:a vorbis -strict -2 -q:a 4 -y {arquivo_ogg}'
                    subprocess.run(comando, shell=True)

            # Exemplo de uso da função
            sourceFileDir = os.path.dirname(os.path.abspath(__file__))
            somDir = os.path.join(sourceFileDir, "som")

            arquivo_webm = f'som/playwebm.webm'
            arquivo_ogg = f'som/{titulo_formatado}.ogg'
            converter_audio_webm_para_ogg(arquivo_webm, arquivo_ogg)

            self.manager.get_screen("carregamento").ids.progress_carregamento.value = 80
            self.manager.get_screen("carregamento").ids.label_progress.text = f'80%'

            self.manager.get_screen("inicio").ids.play.icon = 'pause'
            self.manager.get_screen("musicas").ids.play.icon = 'pause'
            self.manager.get_screen("pesquisar").ids.play.icon = 'pause'
            self.manager.get_screen("playlist").ids.play.icon = 'pause'

            # obtém o caminho do diretório atual
            sourceFileDir = os.path.dirname(os.path.abspath(__file__))

            # obtém o caminho da pasta "som"
            somDir = os.path.join(sourceFileDir, "som")

            # obtém o caminho do arquivo "play1.ogg"
            playFile = os.path.join(somDir, f"{titulo_formatado}.ogg")

            Uri = Uri2
            PythonActivity = PythonActivity2
            player = player2

            if platform == 'android':
                if player.isPlaying():
                    player.stop()
                    player.reset()

                uri = Uri.parse('file://' + playFile)
                player.reset()
                player.setDataSource(PythonActivity.mActivity, uri)

                # Prepara o MediaPlayer para reprodução
                player.prepare()
                # Inicia a reprodução do áudio
                """position_ms = 50 * 1000
                player.seekTo(position_ms)"""

                # Obtém a duração do arquivo de áudio em milissegundos
                duration_ms = player.getDuration()

                # Converte a duração para segundos
                duration = duration_ms / 1000
                Inicio.tempo_musica = duration

                print(f"duração {duration}")


            else:
                self.sound = pygame.mixer.music.load(playFile)
                duration = pygame.mixer.Sound(playFile).get_length()
                Inicio.tempo_musica = duration

            if Inicio.position == 0:
                self.manager.get_screen("carregamento").ids.progress_carregamento.value = 100
                self.manager.get_screen("carregamento").ids.label_progress.text = f'100%'
                self.voltar_inicio()

                if platform == 'android':
                    player.start()
                else:
                    pygame.mixer.music.play()

            else:
                self.manager.get_screen("carregamento").ids.progress_carregamento.value = 100
                self.manager.get_screen("carregamento").ids.label_progress.text = f'100%'
                self.voltar_inicio()
                if platform == 'android':
                    player.seekTo(Inicio.position)
                    player.start()
                else:
                    pygame.mixer.music.play()
                    pygame.mixer.music.set_pos(Inicio.position)
                    print(Inicio.position)

            try:
                self.progress_bar_update.cancel()
            except:
                pass

            Inicio.position = -1
            stop_threads2 = False
            print(f'DURAÇÃO TOTALLLLLLL : {Inicio.tempo_musica}')

            Inicio.position = -1
            Inicio.numero_musica = n_audio

            def update_progress():
                while True:
                    if Inicio.mudanca_faixa_inicio:
                        break
                    print(Inicio.numero_musica)
                    time.sleep(1)
                    if Inicio.position >= int(Inicio.tempo_musica):
                        numero = int(Inicio.numero_musica)
                        if numero <= 5:
                            if int(numero) < 5:
                                numero += 1
                            elif numero == 5:
                                numero = 1
                            if numero == 1:
                                titulo1 = self.manager.get_screen("inicio").ids.titulo_brasil1.text
                                artista1 = self.manager.get_screen("inicio").ids.artista_brasil1.text
                                image1 = self.manager.get_screen("inicio").ids.source_brasil1.source

                                self.play_modify(titulo1, artista1, f'{numero}', image1)
                                self.play(titulo1, artista1, f'{numero}', image1)
                            if numero == 2:
                                titulo1 = self.manager.get_screen("inicio").ids.titulo_brasil2.text
                                artista1 = self.manager.get_screen("inicio").ids.artista_brasil2.text
                                image1 = self.manager.get_screen("inicio").ids.source_brasil2.source
                                print(artista1)

                                self.play_modify(titulo1, artista1, f'{numero}', image1)
                                self.play(titulo1, artista1, f'{numero}', image1)
                            elif numero == 3:
                                titulo1 = self.manager.get_screen("inicio").ids.titulo_brasil3.text
                                artista1 = self.manager.get_screen("inicio").ids.artista_brasil3.text
                                image1 = self.manager.get_screen("inicio").ids.source_brasil3.source

                                self.play_modify(titulo1, artista1, f'{numero}', image1)
                                self.play(titulo1, artista1, f'{numero}', image1)
                            elif numero == 4:
                                titulo1 = self.manager.get_screen("inicio").ids.titulo_brasil4.text
                                artista1 = self.manager.get_screen("inicio").ids.artista_brasil4.text
                                image1 = self.manager.get_screen("inicio").ids.source_brasil4.source

                                self.play_modify(titulo1, artista1, f'{numero}', image1)
                                self.play(titulo1, artista1, f'{numero}', image1)


                            elif numero == 5:
                                titulo1 = self.manager.get_screen("inicio").ids.titulo_brasil5.text
                                artista1 = self.manager.get_screen("inicio").ids.artista_brasil5.text
                                image1 = self.manager.get_screen("inicio").ids.source_brasil5.source

                                self.play_modify(titulo1, artista1, f'{numero}', image1)
                                self.play(titulo1, artista1, f'{numero}', image1)

                        elif numero > 5:
                            numero = int(Inicio.numero_musica)
                            if int(numero) < 10:
                                numero += 1

                            elif int(numero) == 10:
                                numero = 6
                            self.manager.get_screen("inicio").ids.n_audio.text = titulo_formatado
                            if numero == 6:
                                titulo1 = self.manager.get_screen("inicio").ids.titulo_mundo1.text
                                artista1 = self.manager.get_screen("inicio").ids.artista_mundo1.text
                                image1 = self.manager.get_screen("inicio").ids.source_mundo1.source

                                self.play_modify(titulo1, artista1, f'{numero}', image1)
                                self.play(titulo1, artista1, f'{numero}', image1)

                            elif numero == 7:
                                titulo1 = self.manager.get_screen("inicio").ids.titulo_mundo2.text
                                artista1 = self.manager.get_screen("inicio").ids.artista_mundo2.text
                                image1 = self.manager.get_screen("inicio").ids.source_mundo2.source

                                self.play_modify(titulo1, artista1, f'{numero}', image1)
                                self.play(titulo1, artista1, f'{numero}', image1)
                            elif numero == 8:
                                titulo1 = self.manager.get_screen("inicio").ids.titulo_mundo3.text
                                artista1 = self.manager.get_screen("inicio").ids.artista_mundo3.text
                                image1 = self.manager.get_screen("inicio").ids.source_mundo3.source

                                self.play_modify(titulo1, artista1, f'{numero}', image1)
                                self.play(titulo1, artista1, f'{numero}', image1)
                            elif numero == 9:
                                titulo1 = self.manager.get_screen("inicio").ids.titulo_mundo4.text
                                artista1 = self.manager.get_screen("inicio").ids.artista_mundo4.text
                                image1 = self.manager.get_screen("inicio").ids.source_mundo4.source

                                self.play_modify(titulo1, artista1, f'{numero}', image1)
                                self.play(titulo1, artista1, f'{numero}', image1)
                            elif numero == 10:
                                titulo1 = self.manager.get_screen("inicio").ids.titulo_mundo5.text
                                artista1 = self.manager.get_screen("inicio").ids.artista_mundo5.text
                                image1 = self.manager.get_screen("inicio").ids.source_mundo5.source

                                self.play_modify(titulo1, artista1, f'{numero}', image1)
                                self.play(titulo1, artista1, f'{numero}', image1)

                    else:
                        pass

            if Inicio.stop_threads2 == False:
                Inicio.progress_bar_update = threading.Thread(target=update_progress).start()
            if Inicio.stop_threads2 == False:
                Inicio.progress_bar_update = threading.Thread(target=self.update_progress).start()

    def update_progress(self):
        try:
            while True:
                if Inicio.mudanca_faixa_inicio:
                    Inicio.stop_threads2 = False
                    break
                self.manager.get_screen("inicio").ids.progress_bar.max = Inicio.tempo_musica
                self.manager.get_screen("musicas").ids.progress_bar.max = Inicio.tempo_musica
                self.manager.get_screen("pesquisar").ids.progress_bar.max = Inicio.tempo_musica
                self.manager.get_screen("playlist").ids.progress_bar.max = Inicio.tempo_musica
                print('TA AQUI DENTRO!')
                Inicio.stop_threads2 = True
                time.sleep(1)
                Inicio.position += 1
                if Inicio.progress_bar_valor_novo != 0:
                    if self.manager.current == 'inicio':
                        self.manager.get_screen("inicio").ids.progress_bar.value = Inicio.progress_bar_valor_novo
                    elif self.manager.current == 'musicas':
                        self.manager.get_screen("musicas").ids.progress_bar.value = Inicio.progress_bar_valor_novo
                    elif self.manager.current == 'pesquisar':
                        self.manager.get_screen("pesquisar").ids.progress_bar.value = Inicio.progress_bar_valor_novo
                    elif self.manager.current == 'playlist':
                        self.manager.get_screen("playlist").ids.progress_bar.value = Inicio.progress_bar_valor_novo

                    Inicio.position = Inicio.progress_bar_valor_novo
                    if platform == 'android':
                        player2.seekTo(Inicio.progress_bar_valor_novo * 1000)

                    else:
                        pygame.mixer.music.set_pos(Inicio.progress_bar_valor_novo)

                    Inicio.progress_bar_valor_novo = 0

                if Inicio.position >= int(Inicio.tempo_musica):
                    self.manager.get_screen("inicio").ids.progress_bar.value = 0
                    self.manager.get_screen("musicas").ids.progress_bar.value = 0
                    self.manager.get_screen("pesquisar").ids.progress_bar.value = 0
                    self.manager.get_screen("playlist").ids.progress_bar.value = 0
                else:
                    self.manager.get_screen("inicio").ids.progress_bar.value = Inicio.position
                    self.manager.get_screen("musicas").ids.progress_bar.value = Inicio.position
                    self.manager.get_screen("pesquisar").ids.progress_bar.value = Inicio.position
                    self.manager.get_screen("playlist").ids.progress_bar.value = Inicio.position
        except:
            pass

    @mainthread
    def play_modify(self, titulo, artista, n_audio, source):
        self.manager.get_screen("inicio").ids.nome_musica.text = titulo
        self.manager.get_screen("inicio").ids.nome_artista.text = artista
        self.manager.get_screen("inicio").ids.image_musica.source = source

        if n_audio == '1':

            if Inicio.ultimo_audio != None:
                if int(Inicio.ultimo_audio) <= 5:
                    playbrasil = "playbrasil" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playbrasil].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playbrasil].icon = "play"
                        self.manager.get_screen("inicio").ids.playbrasil1.icon = 'equalizer'
                else:
                    playmundo = "playmundo" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playmundo].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playmundo].icon = "play"
                        self.manager.get_screen("inicio").ids.playbrasil1.icon = 'equalizer'
            else:
                self.manager.get_screen("inicio").ids.playbrasil1.icon = 'equalizer'



        elif n_audio == '2':

            if Inicio.ultimo_audio != None:
                if int(Inicio.ultimo_audio) <= 5:
                    playbrasil = "playbrasil" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playbrasil].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playbrasil].icon = "play"
                        self.manager.get_screen("inicio").ids.playbrasil2.icon = 'equalizer'
                else:
                    playmundo = "playmundo" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playmundo].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playmundo].icon = "play"
                        self.manager.get_screen("inicio").ids.playbrasil2.icon = 'equalizer'
            else:
                self.manager.get_screen("inicio").ids.playbrasil2.icon = 'equalizer'


        elif n_audio == '3':

            if Inicio.ultimo_audio != None:
                if int(Inicio.ultimo_audio) <= 5:
                    playbrasil = "playbrasil" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playbrasil].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playbrasil].icon = "play"
                        self.manager.get_screen("inicio").ids.playbrasil3.icon = 'equalizer'
                else:
                    playmundo = "playmundo" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playmundo].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playmundo].icon = "play"
                        self.manager.get_screen("inicio").ids.playbrasil3.icon = 'equalizer'
            else:
                self.manager.get_screen("inicio").ids.playbrasil3.icon = 'equalizer'

        elif n_audio == '4':

            if Inicio.ultimo_audio != None:
                if int(Inicio.ultimo_audio) <= 5:
                    playbrasil = "playbrasil" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playbrasil].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playbrasil].icon = "play"
                        self.manager.get_screen("inicio").ids.playbrasil4.icon = 'equalizer'
                else:
                    playmundo = "playmundo" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playmundo].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playmundo].icon = "play"
                        self.manager.get_screen("inicio").ids.playbrasil4.icon = 'equalizer'
            else:
                self.manager.get_screen("inicio").ids.playbrasil4.icon = 'equalizer'

        elif n_audio == '5':

            if Inicio.ultimo_audio != None:
                if int(Inicio.ultimo_audio) <= 5:
                    playbrasil = "playbrasil" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playbrasil].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playbrasil].icon = "play"
                        self.manager.get_screen("inicio").ids.playbrasil5.icon = 'equalizer'
                else:
                    playmundo = "playmundo" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playmundo].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playmundo].icon = "play"
                        self.manager.get_screen("inicio").ids.playbrasil5.icon = 'equalizer'
            else:
                self.manager.get_screen("inicio").ids.playbrasil5.icon = 'equalizer'

        elif n_audio == '6':

            if Inicio.ultimo_audio != None:
                if int(Inicio.ultimo_audio) <= 5:
                    playbrasil = "playbrasil" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playbrasil].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playbrasil].icon = "play"
                        self.manager.get_screen("inicio").ids.playmundo6.icon = 'equalizer'
                else:
                    playmundo = "playmundo" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playmundo].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playmundo].icon = "play"
                        self.manager.get_screen("inicio").ids.playmundo6.icon = 'equalizer'
            else:
                self.manager.get_screen("inicio").ids.playmundo6.icon = 'equalizer'

        elif n_audio == '7':

            if Inicio.ultimo_audio != None:
                if int(Inicio.ultimo_audio) <= 5:
                    playbrasil = "playbrasil" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playbrasil].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playbrasil].icon = "play"
                        self.manager.get_screen("inicio").ids.playmundo7.icon = 'equalizer'
                else:
                    playmundo = "playmundo" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playmundo].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playmundo].icon = "play"
                        self.manager.get_screen("inicio").ids.playmundo7.icon = 'equalizer'
            else:
                self.manager.get_screen("inicio").ids.playmundo7.icon = 'equalizer'

        elif n_audio == '8':

            if Inicio.ultimo_audio != None:
                if int(Inicio.ultimo_audio) <= 5:
                    playbrasil = "playbrasil" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playbrasil].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playbrasil].icon = "play"
                        self.manager.get_screen("inicio").ids.playmundo8.icon = 'equalizer'
                else:
                    playmundo = "playmundo" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playmundo].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playmundo].icon = "play"
                        self.manager.get_screen("inicio").ids.playmundo8.icon = 'equalizer'
            else:
                self.manager.get_screen("inicio").ids.playmundo8.icon = 'equalizer'

        elif n_audio == '9':

            if Inicio.ultimo_audio != None:
                if int(Inicio.ultimo_audio) <= 5:
                    playbrasil = "playbrasil" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playbrasil].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playbrasil].icon = "play"
                        self.manager.get_screen("inicio").ids.playmundo9.icon = 'equalizer'
                else:
                    playmundo = "playmundo" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playmundo].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playmundo].icon = "play"
                        self.manager.get_screen("inicio").ids.playmundo9.icon = 'equalizer'
            else:
                self.manager.get_screen("inicio").ids.playmundo9.icon = 'equalizer'

        elif n_audio == '10':

            if Inicio.ultimo_audio != None:
                if int(Inicio.ultimo_audio) <= 5:
                    playbrasil = "playbrasil" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playbrasil].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playbrasil].icon = "play"
                        self.manager.get_screen("inicio").ids.playmundo10.icon = 'equalizer'
                else:
                    playmundo = "playmundo" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playmundo].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playmundo].icon = "play"
                        self.manager.get_screen("inicio").ids.playmundo10.icon = 'equalizer'
            else:
                self.manager.get_screen("inicio").ids.playmundo10.icon = 'equalizer'

        Inicio.ultimo_audio = n_audio

    @mainthread
    def play(self, titulo, artista, n_audio, source):
        Musicas.mudanca_faixa_musica = True
        Inicio.mudanca_faixa_inicio = False
        self.manager.get_screen("inicio").ids.scroll.pos_hint = {'center_x': 0.53, 'top': 0.23}
        self.manager.get_screen("pesquisar").ids.scroll.pos_hint = {'center_x': 0.53, 'top': 0.23}
        self.manager.get_screen("playlist").ids.scroll.pos_hint = {'center_x': 0.53, 'top': 0.23}
        self.manager.get_screen("musicas").ids.scroll.pos_hint = {'center_x': 0.53, 'top': 0.23}

        threading.Thread(target=self.thd_play, args=(titulo, artista, n_audio)).start()
        self.manager.get_screen("carregamento").ids.progress_carregamento.value = 0
        self.manager.get_screen(
            "carregamento").ids.label_progress_info.text = f'Carregando música aguarde, nosso servidor é limitado!'
        self.manager.get_screen("carregamento").ids.label_progress.text = f'10%'
        self.manager.current = 'carregamento'
        self.manager.transition.direction = 'left'

        self.manager.get_screen("inicio").ids.nome_musica.text = titulo
        self.manager.get_screen("inicio").ids.nome_artista.text = artista
        self.manager.get_screen("inicio").ids.image_musica.source = source

        self.manager.get_screen("musicas").ids.nome_musica.text = titulo
        self.manager.get_screen("musicas").ids.nome_artista.text = artista
        self.manager.get_screen("musicas").ids.image_musica.source = source

        self.manager.get_screen("pesquisar").ids.nome_musica.text = titulo
        self.manager.get_screen("pesquisar").ids.nome_artista.text = artista
        self.manager.get_screen("pesquisar").ids.image_musica.source = source

        self.manager.get_screen("playlist").ids.nome_musica.text = titulo
        self.manager.get_screen("playlist").ids.nome_artista.text = artista
        self.manager.get_screen("playlist").ids.image_musica.source = source

        # PASSAR A REFERENCIA PARA O PLAY_STOP
        texto = f"{titulo} {artista}"
        titulo_formatado = re.sub(r'[^a-zA-Z0-9_]', '_', texto)

        self.manager.get_screen("inicio").ids.n_audio.text = titulo_formatado

        if n_audio == '1':

            if Inicio.ultimo_audio != None:
                if int(Inicio.ultimo_audio) <= 5:
                    playbrasil = "playbrasil" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playbrasil].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playbrasil].icon = "play"
                        self.manager.get_screen("inicio").ids.playbrasil1.icon = 'equalizer'
                else:
                    playmundo = "playmundo" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playmundo].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playmundo].icon = "play"
                        self.manager.get_screen("inicio").ids.playbrasil1.icon = 'equalizer'
            else:
                self.manager.get_screen("inicio").ids.playbrasil1.icon = 'equalizer'



        elif n_audio == '2':

            if Inicio.ultimo_audio != None:
                if int(Inicio.ultimo_audio) <= 5:
                    playbrasil = "playbrasil" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playbrasil].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playbrasil].icon = "play"
                        self.manager.get_screen("inicio").ids.playbrasil2.icon = 'equalizer'
                else:
                    playmundo = "playmundo" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playmundo].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playmundo].icon = "play"
                        self.manager.get_screen("inicio").ids.playbrasil2.icon = 'equalizer'
            else:
                self.manager.get_screen("inicio").ids.playbrasil2.icon = 'equalizer'


        elif n_audio == '3':

            if Inicio.ultimo_audio != None:
                if int(Inicio.ultimo_audio) <= 5:
                    playbrasil = "playbrasil" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playbrasil].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playbrasil].icon = "play"
                        self.manager.get_screen("inicio").ids.playbrasil3.icon = 'equalizer'
                else:
                    playmundo = "playmundo" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playmundo].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playmundo].icon = "play"
                        self.manager.get_screen("inicio").ids.playbrasil3.icon = 'equalizer'
            else:
                self.manager.get_screen("inicio").ids.playbrasil3.icon = 'equalizer'

        elif n_audio == '4':

            if Inicio.ultimo_audio != None:
                if int(Inicio.ultimo_audio) <= 5:
                    playbrasil = "playbrasil" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playbrasil].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playbrasil].icon = "play"
                        self.manager.get_screen("inicio").ids.playbrasil4.icon = 'equalizer'
                else:
                    playmundo = "playmundo" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playmundo].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playmundo].icon = "play"
                        self.manager.get_screen("inicio").ids.playbrasil4.icon = 'equalizer'
            else:
                self.manager.get_screen("inicio").ids.playbrasil4.icon = 'equalizer'

        elif n_audio == '5':

            if Inicio.ultimo_audio != None:
                if int(Inicio.ultimo_audio) <= 5:
                    playbrasil = "playbrasil" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playbrasil].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playbrasil].icon = "play"
                        self.manager.get_screen("inicio").ids.playbrasil5.icon = 'equalizer'
                else:
                    playmundo = "playmundo" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playmundo].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playmundo].icon = "play"
                        self.manager.get_screen("inicio").ids.playbrasil5.icon = 'equalizer'
            else:
                self.manager.get_screen("inicio").ids.playbrasil5.icon = 'equalizer'

        elif n_audio == '6':

            if Inicio.ultimo_audio != None:
                if int(Inicio.ultimo_audio) <= 5:
                    playbrasil = "playbrasil" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playbrasil].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playbrasil].icon = "play"
                        self.manager.get_screen("inicio").ids.playmundo6.icon = 'equalizer'
                else:
                    playmundo = "playmundo" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playmundo].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playmundo].icon = "play"
                        self.manager.get_screen("inicio").ids.playmundo6.icon = 'equalizer'
            else:
                self.manager.get_screen("inicio").ids.playmundo6.icon = 'equalizer'

        elif n_audio == '7':

            if Inicio.ultimo_audio != None:
                if int(Inicio.ultimo_audio) <= 5:
                    playbrasil = "playbrasil" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playbrasil].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playbrasil].icon = "play"
                        self.manager.get_screen("inicio").ids.playmundo7.icon = 'equalizer'
                else:
                    playmundo = "playmundo" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playmundo].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playmundo].icon = "play"
                        self.manager.get_screen("inicio").ids.playmundo7.icon = 'equalizer'
            else:
                self.manager.get_screen("inicio").ids.playmundo7.icon = 'equalizer'

        elif n_audio == '8':

            if Inicio.ultimo_audio != None:
                if int(Inicio.ultimo_audio) <= 5:
                    playbrasil = "playbrasil" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playbrasil].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playbrasil].icon = "play"
                        self.manager.get_screen("inicio").ids.playmundo8.icon = 'equalizer'
                else:
                    playmundo = "playmundo" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playmundo].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playmundo].icon = "play"
                        self.manager.get_screen("inicio").ids.playmundo8.icon = 'equalizer'
            else:
                self.manager.get_screen("inicio").ids.playmundo8.icon = 'equalizer'

        elif n_audio == '9':

            if Inicio.ultimo_audio != None:
                if int(Inicio.ultimo_audio) <= 5:
                    playbrasil = "playbrasil" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playbrasil].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playbrasil].icon = "play"
                        self.manager.get_screen("inicio").ids.playmundo9.icon = 'equalizer'
                else:
                    playmundo = "playmundo" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playmundo].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playmundo].icon = "play"
                        self.manager.get_screen("inicio").ids.playmundo9.icon = 'equalizer'
            else:
                self.manager.get_screen("inicio").ids.playmundo9.icon = 'equalizer'

        elif n_audio == '10':

            if Inicio.ultimo_audio != None:
                if int(Inicio.ultimo_audio) <= 5:
                    playbrasil = "playbrasil" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playbrasil].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playbrasil].icon = "play"
                        self.manager.get_screen("inicio").ids.playmundo10.icon = 'equalizer'
                else:
                    playmundo = "playmundo" + str(Inicio.ultimo_audio)
                    if self.manager.get_screen("inicio").ids[playmundo].icon == "equalizer":
                        self.manager.get_screen("inicio").ids[playmundo].icon = "play"
                        self.manager.get_screen("inicio").ids.playmundo10.icon = 'equalizer'
            else:
                self.manager.get_screen("inicio").ids.playmundo10.icon = 'equalizer'

        Inicio.ultimo_audio = n_audio

    def playclock(self, titulo, artista, n_audio, source):
        self.manager.get_screen("inicio").ids.nome_musica.text = titulo
        self.manager.get_screen("inicio").ids.nome_artista.text = artista
        self.manager.get_screen("inicio").ids.image_musica.source = source

    def stop(self):
        self.manager.get_screen("inicio").ids.scroll.pos_hint = {'center_x': 0.53, 'top': 0.0}
        if platform == 'android':
            if player2.isPlaying():
                player2.stop()
                player2.reset()
        else:
            pygame.mixer.music.unload()  # descarrega o arquivo de som

    @mainthread
    def voltar_inicio(self):
        if Inicio.vermaiscount == True:
            self.manager.current = 'musicas'
            self.manager.transition.direction = 'left'
        else:
            self.manager.current = 'inicio'
            self.manager.transition.direction = 'left'


class WindowManager(ScreenManager):
    pass


class main(MDApp):

    def build(self):
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])
        else:
            Window.size = (360, 640)
        # set window size and title
        # Window.size = (360, 640)
        # Window.title = 'Fluminense App'
        return

    if platform == 'android':
        @run_on_ui_thread
        def change_color(self):
            if platform == 'android':
                Color = autoclass("android.graphics.Color")
                WindowManager = autoclass('android.view.WindowManager$LayoutParams')
                activity = autoclass('org.kivy.android.PythonActivity').mActivity
                ###################################################
                window = activity.getWindow()
                window.clearFlags(WindowManager.FLAG_TRANSLUCENT_STATUS)  # NON INDISPENSABILE SU ALCUNI SMARTPHONE
                window.addFlags(WindowManager.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS)
                window.setStatusBarColor(Color.parseColor('#121212'))
                window.setNavigationBarColor(Color.parseColor('#1DD05D'))

    def on_start(self):
        if platform == 'android':
            self.change_color()
        startion_instance = Login()
        startion_instance.trocar_image()


# Run app
main().run()
