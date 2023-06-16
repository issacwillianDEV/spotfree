from kivy.utils import platform
if platform == 'android':
    from jnius import autoclass

    # Importa as classes necessárias do Android
    MediaPlayer2 = autoclass('android.media.MediaPlayer')
    Uri2 = autoclass('android.net.Uri')
    PythonActivity2 = autoclass('org.kivy.android.PythonActivity')

    # Cria um novo objeto MediaPlayer
    player2 = MediaPlayer2()
else:
    MediaPlayer2 = None
    Uri2 = None
    PythonActivity2 = None
    player2 = None