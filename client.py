import yaml 
import tkinter as tk
from PIL import Image, ImageTk, ImageOps
import webbrowser
import webview
from threading import Thread, RLock
from http.server import HTTPServer, SimpleHTTPRequestHandler
import re
import requests
import base64
from pySmartDL import SmartDL
import zipfile
import os

#https://stackoverflow.com/a/42615559
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)
os.chdir(application_path)
def load_yaml(default, file):
    if not os.path.exists(file):
        print('File not found. Using default configuration.')
        return default
    else:
        try:
            with open(file, 'r') as file:
                loaded_config = yaml.safe_load(file)
                default.update(loaded_config)
                return default
        except yaml.YAMLError as e:
            print(e)
            return default

default_config = {
    'browser_mode': 0,
    'default_game': 0,
    'frameless': False,
    'resizable': True,
    'fullscreen': True,
    'width': 0,
    'height': 0,
    'port': 56800,
    'run_in_browser': False,
    'update_link': 'https://github.com/ShinoNia/Honkai-Visual-Novels',
    'update_repo_author': 'ShinoNia',
    'update_repo_name': 'Honkai-Visual-Novels',
    'download_thread': 1,
    'client_width': 1000,
    'client_height': 500,
    'client_x': 50,
    'client_y': 50
}
config = load_yaml(default_config, 'config.yaml')

default_games = {
    "games": [
        {
            "background": "duriduri/bg.png",
            "default_lang": 0,
            "langs": ["xml/en-US/", "xml/ko-KR/"],
            "name": "Durandal",
            "path": "duriduri",
        },
        {
            "background": "ae/bg.jpg",
            "default_lang": 0,
            "langs": ["xml/en-US/", "xml/ko-KR/"],
            "name": "Anti-Entropy",
            "path": "ae",
        },
    ],
    "version": 0.0,
}

games = load_yaml(default_games, 'games.yaml')
gamelist_version = games['version']
games = games['games']
lock = RLock()

regex = re.compile(
    r'^(?:http|ftp)s?://'
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
    r'localhost|'
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'
    r'\[?[A-F0-9]*:[A-F0-9:]+\]?)' 
    r'(?::\d+)?'
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

def fix(string):
    if not string.endswith('/'):
        return string + '/'
    return string


def validate_numeric_input(char):
    if str.isdigit(char) or char == "":
        return True
    else:
        return False

def kill_server():
    try:
        httpd.shutdown()
        server_thread.join()
    except Exception as e:
        print(e)
        pass



def run_server(port, lang):
    global httpd
    server_address = ('', port)
    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if 'xmlfiles' in self.path:
                new_direct = fix(lang)
                if re.match(regex, new_direct):
                    new_path = new_direct + self.path.split('xmlfiles/')[1]
                    self.send_response(302)
                    self.send_header('Location', new_path)
                    self.end_headers()
                else:
                    self.path = self.path.replace('xmlfiles/', new_direct)  
                    super().do_GET()
            else:
                super().do_GET()
        def end_headers(self):
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
            super().end_headers()
    httpd = HTTPServer(server_address, Handler)
    httpd.serve_forever() 
    httpd.server_close()

def launch_game():
    global server_thread
    kill_server()
    server_thread = Thread(target=run_server, args=(int(config['port']), selected_lang.get()))
    server_thread.start()
    url = f'http://localhost:{config["port"]}/{games[selected_game]["path"]}'

    if config['run_in_browser']: 
        webbrowser.open(url, new=config['browser_mode'], autoraise=True)
    else:
        webview.create_window(title=games[selected_game]['name'], url=url, width=int(width_var.get()), height=int(height_var.get()), frameless=config['frameless'], resizable=config['resizable'], fullscreen=config['fullscreen'], private_mode=False)
        webview.start()


def download_game(*args):
    download_popup.deiconify()


def change_mode(*args):
    global config
    config['run_in_browser'] = browser_var.get()
    config['browser_mode'] = int(browser_mode_var.get())
    config['resizable'] = resize_var.get()
    config['frameless'] = frame_var.get()
    config['width'] = int(width_var.get())
    config['height'] = int(height_var.get())
    config['port'] = int(port_var.get())
    config['download_thread'] = int(dl_thread_var.get())


def fullscreen_toggle(*args):
    global config
    if size_var.get() == 'Fullscreen':
        config['fullscreen'] = True
    else:
        config['fullscreen'] = False 

def lang_change(*args):
    global games
    games[selected_game]['default_lang'] = langs.index(selected_lang.get())

def load_lang(selected_game):
    global langs, lang_dropdown

    langs = games[selected_game]['langs']
    selected_lang.set(langs[games[selected_game]['default_lang']])
    
    #https://stackoverflow.com/questions/17580218/changing-the-options-of-a-optionmenu-when-clicking-a-button
    lang_dropdown['menu'].delete(0, 'end')
    for lang in langs:
        lang_dropdown['menu'].add_command(label=lang, command=tk._setit(selected_lang, lang))


def update_game(*args):
    global photo, config, selected_game
    selected_game = options.index(selected_option.get())
    try:
        photo = Image.open(games[selected_game]['background'])
    except Exception as e:
        print(e)
        photo = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
    resize_background(None)

    load_lang(selected_game)
    config['default_game'] = selected_game
    try:
        set_label()
        set_button()
    except NameError:
        pass

def resize_background(e):
    global photo, background
    if e == None:
        image = ImageOps.fit(photo, (background.winfo_width(), background.winfo_height()))
    else:
        image = ImageOps.fit(photo, (e.width, e.height))
    resized = ImageTk.PhotoImage(image)
    background.configure(image=resized)
    background.image=resized

def settings_toggle(*args):
    settings.grid_forget() if settings.winfo_manager() else settings.grid(row=1, column=0, sticky="nwes")

def download_toggle(*args):
    dl_frame.grid_forget() if dl_frame.winfo_manager() else dl_frame.grid(row=1, column=4, sticky="nwes")


root = tk.Tk()

root.title("Honkai Visual Novels")
root.configure(bg="#000000")
root.geometry(f"{config['client_width']}x{config['client_height']}+{config['client_x']}+{config['client_y']}")

root.grid_rowconfigure(2, weight=1)
root.grid_rowconfigure(1, weight=20)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)
root.grid_columnconfigure(3, weight=1)

background = tk.Label(root)
background.grid(row=0, column=1, columnspan=3, rowspan=3, sticky="nsew")
background.bind('<Configure>', resize_background)

# Settings frame

settings = tk.Frame(root)


settings.grid_columnconfigure(0, weight=2)
settings.grid_columnconfigure(1, weight=1)


vcmd = (settings.register(validate_numeric_input), '%P')
def create_entry(text, variable, default_value, row, callback):
    tk.Label(settings, text=text).grid(row=row, column=0)
    entry = tk.Entry(settings, textvariable=variable, validate='all', validatecommand=vcmd)
    variable.set(default_value)
    variable.trace('w', callback)
    entry.grid(row=row, column=1)

def create_checkbutton(text, variable, default_value, row, callback):
    tk.Label(settings, text=text).grid(row=row, column=0)
    checkbox = tk.Checkbutton(settings, variable=variable)
    variable.set(default_value)
    variable.trace('w', callback)
    checkbox.grid(row=row, column=1)


selected_lang = tk.StringVar()
selected_lang.trace('w', lang_change)
tk.Label(settings, text='Langague: ').grid(row=0, column=0)
lang_dropdown = tk.OptionMenu(settings, selected_lang, [])
lang_dropdown.grid(row=0, column=1)



browser_var = tk.BooleanVar()
create_checkbutton('Launch in browser: ', browser_var, config['run_in_browser'], 1, change_mode)

tk.Label(settings, text='Browser mode: ').grid(row=2, column=0)
browser_modes = [0, 1, 2]
browser_mode_var = tk.StringVar()
browser_mode_var.set(config['browser_mode'])
browser_mode_var.trace('w', change_mode)
browser_mode_dropdown = tk.OptionMenu(settings, browser_mode_var, *browser_modes)
browser_mode_dropdown.grid(row=2, column = 1)

port_var = tk.StringVar()
create_entry('Port: ', port_var, config['port'], 3, change_mode)

sizes = ['Resolution', 'Fullscreen']
size_var = tk.StringVar()
size_var.trace('w', fullscreen_toggle)
if config['fullscreen']:
    size_var.set('Fullscreen')
else:
    size_var.set('Resolution')
size_dropdown = tk.OptionMenu(settings, size_var, *sizes)
size_dropdown.grid(row=4, column=0)
resolution_frame = tk.Frame(settings)
resolution_frame.grid(row=4, column=1)
width_var = tk.StringVar()
height_var = tk.StringVar()
width_var.set(config['width'])
height_var.set(config['height'])
width_var.trace('w', change_mode)
height_var.trace('w', change_mode)
width_entry = tk.Entry(resolution_frame, textvariable=width_var, validate='all', validatecommand=vcmd)
height_entry = tk.Entry(resolution_frame, textvariable=height_var, validate='all', validatecommand=vcmd)
width_entry.grid(row=0, column=0, sticky='we')
tk.Label(resolution_frame, text='X').grid(row=0, column=1)
height_entry.grid(row=0, column=2, sticky='we')

resize_var = tk.BooleanVar()
create_checkbutton('Resizable: ', resize_var, config['resizable'], 5, change_mode)

frame_var = tk.BooleanVar()
create_checkbutton('Frameless: ', frame_var, config['frameless'], 6, change_mode)

dl_thread_var = tk.StringVar()
create_entry('Number of download threads: ', dl_thread_var, config['download_thread'], 7, change_mode)

# End settings frame

settings_button = tk.Button(root, text='Settings', command=settings_toggle)
settings_button.grid(row=0, column=1, sticky='w')

options = [i['name'] for i in games]
selected_option = tk.StringVar()
selected_option.trace('w', update_game)
selected_option.set(options[config['default_game']])
dropdown = tk.OptionMenu(root, selected_option, *options)
dropdown.config(width=15)
dropdown.grid(row=0, column=2, sticky="we")

dl_button = tk.Button(root, text='Download/Update/Repair', command=download_toggle)
dl_button.grid(row=0, column=3, sticky='e')


launch_button = tk.Button(root, text='Play!', command=launch_game)
launch_button.grid(row=2, column=3, sticky="wnse")

#Download frame
states = {
    'downloading': {},
    'installing': {},
    'download_process': {},
    'pg_var': {},
    'versions': {
        'latest': {'gamelist': 'N/A'},
        'current': {'gamelist': 'N/A'}
    },
    'download_url': {}
}
new_games = None
for game in [i['path'] for i in games]:
    states['downloading'][game] = {'game': False, 'lang': False}
    states['installing'][game] = {'game': False, 'lang': False}
    states['download_process'][game] = {'game': None, 'lang': None}
    states['pg_var'][game] = {'game': tk.StringVar(), 'lang': tk.StringVar()}
    states['versions']['latest'][game] = {'game': 'N/A', 'lang': 'N/A'}
    states['versions']['current'][game] = {'game': 'N/A', 'lang': 'N/A'}
    states['download_url'][game] = {'game': None, 'lang': None}

fetched_update = False

def overwrite_games():
    global games
    games = new_games

def set_label():
    game_path = games[selected_game]['path']
    for var, ver in [(dl_game_lb_var, 'game'), (dl_lang_lb_var, 'lang')]:
        var.set(f"Current version: {states['versions']['current'][game_path][ver]} | Latest version: {states['versions']['latest'][game_path][ver]}")
    dl_gamelist_lb_var.set(f"Current version: {states['versions']['current']['gamelist']} | Latest version: {states['versions']['latest']['gamelist']}")
    for label, t in [(dl_game_pg, 'game'), (dl_lang_pg, 'lang')]:
        label.config(textvariable=states['pg_var'][game_path][t])

def fetch_current_version():
    for path in [i['path'] for i in games]:
        try:
            states['versions']['current'][path]['game'] = open(f'{path}/version', 'r').read().split('\n')[0]
        except Exception as e:
            print(e)
            pass
        try:
            states['versions']['current'][path]['lang'] = open(f'{path}/xml/version', 'r').read().split('\n')[0]
        except Exception as e:
            print(e)
            pass
    states['versions']['current']['gamelist'] = str(gamelist_version)
    set_label()

def fetch_update_thread():
    Thread(target=fetch_latest_version).start()
def fetch_latest_version():
    global new_games
    root.after(0, fetch_update.config, {'text': 'Fetching...', 'state': 'disable'})
    api_url = f"https://api.github.com/repos/{config['update_repo_author']}/{config['update_repo_name']}/releases"
    response = requests.get(api_url)
    if response.status_code != 200:
            print(f"Error: Unable to fetch releases (status code: {response.status_code})")
            return None
    releases = response.json()
    def get_latest(asset_prefix):
        newest_asset = None
        for release in releases:
            assets = release.get('assets', [])
            for asset in assets:
                if asset['name'].startswith(asset_prefix):
                    if newest_asset is None or release['published_at'] > newest_asset['published_at']:
                        return asset

    for path in [i['path'] for i in games]:
        for prefix in ['game', 'lang']:
            asset = get_latest(f'{prefix}-{path}')
            if asset:
                version = os.path.splitext(asset['name'])[0].split('-')[-1]
                states['versions']['latest'][path][prefix] = version
                states['download_url'][path][prefix] = asset['browser_download_url']
    response = requests.get(f"https://api.github.com/repos/{config['update_repo_author']}/{config['update_repo_name']}/contents/games.yaml")
    if response.status_code == 200:
        base64_string = response.json()['content']
        base64_bytes = base64_string.encode("ascii")
        new_games_string = base64.b64decode(base64_bytes).decode("ascii")
        new_games = yaml.safe_load(new_games_string)
        states['versions']['latest']['gamelist'] = new_games['version']
        new_games = new_games['games']
    root.after(0, fetch_update.config, {'text': 'Fetch updates', 'state': 'normal'})
    set_label()
    set_button()
    

def stop_download(game, dl_type):
    states['download_process'][game][dl_type].stop()
    states['downloading'][game][dl_type] = False

def start_download_thread(game, dl_type):
    Thread(target=start_download, args=(game, dl_type)).start()

keep_download = True
def start_download(game, dl_type):
  with lock:
   try:
    os.makedirs('downloads', exist_ok=True)
    url = states['download_url'][game][dl_type]
    states['downloading'][game][dl_type] = True
    root.after(0, set_button)
    obj = SmartDL(url, 'downloads', threads=config['download_thread'], timeout=5)
    states['download_process'][game][dl_type] = obj
    obj.start(blocking=False)
    while not obj.isFinished() and keep_download:
        speed = obj.get_speed(True)
        eta = obj.get_eta(True)
        pg_bar = obj.get_progress_bar()
        root.after(0, states['pg_var'][game][dl_type].set, f'{speed} {pg_bar} {eta}')
    states['downloading'][game][dl_type] = False
    if obj.isSuccessful():
        states['installing'][game][dl_type] = True 
        root.after(0, set_button)
        zip_path = obj.get_dest()
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(os.getcwd())
        os.remove(zip_path)
    else:
        root.after(0, states['pg_var'][game][dl_type].set, obj.get_errors())
    states['installing'][game][dl_type] = False
    root.after(0, set_button)
    root.after(0, update_game)
   except Exception as e:
    states['downloading'][game][dl_type] = False
    states['installing'][game][dl_type] = False
    root.after(0, states['pg_var'][game][dl_type].set, e)
    root.after(0, set_button)


def set_button():
    game_path = games[selected_game]['path']
    for button, text, alttext in [(dl_game_button, 'game', 'game'), (dl_lang_button, 'translation', 'lang'), (dl_gamelist_button, 'gamelist', None)]:
        if button != dl_gamelist_button:
            if states['downloading'][game_path][alttext]:
                button.config(text='Cancel', command=lambda game_path=game_path, alttext=alttext: stop_download(game_path, alttext), state='normal')
            elif states['installing'][game_path][alttext]:
                button.config(text='Installing', state='disable') 
            elif states['download_url'][game_path][alttext] == None:
                    button.config(text=f'Update {text}', state='disable')
            else:
                button.config(text=f'Update {text}', state='normal', command=lambda game_path=game_path, alttext=alttext: start_download_thread(game=game_path, dl_type=alttext))
        else:
            if new_games == None:
                button.config(text=f'Update {text}', state='disable')
            else:
                button.config(text=f'Update {text}', state='normal')



dl_frame = tk.Frame(root)

dl_game_button = tk.Button(dl_frame)
dl_game_pg = tk.Label(dl_frame)
dl_lang_button = tk.Button(dl_frame)
dl_lang_pg = tk.Label(dl_frame)
dl_gamelist_button = tk.Button(dl_frame, command=overwrite_games)
dl_launcher_button = tk.Button(dl_frame, text='Update launcher', command=lambda: webbrowser.open(config['update_link']))

dl_game_lb_var, dl_lang_lb_var, dl_gamelist_lb_var = [tk.StringVar() for _ in range(3)]
row = 0
for button, lbvar, pg in [(dl_game_button, dl_game_lb_var, dl_game_pg),  (dl_lang_button, dl_lang_lb_var, dl_lang_pg), (dl_gamelist_button, dl_gamelist_lb_var, None), (dl_launcher_button, None, None)]:
    button.grid(row=row, column=0)
    tk.Label(dl_frame, textvariable=lbvar).grid(row=row, column=1)
    if button != dl_launcher_button and button != dl_gamelist_button:
        pg.grid(row=row+1, column=0, columnspan=2)
    row += 2



fetch_update = tk.Button(dl_frame, text='Fetch updates', command=fetch_update_thread)
fetch_update.grid(row=row, column = 0, columnspan=2)

set_button()
fetch_current_version()




def on_close():
    config['client_width'], config['client_height'], config['client_x'], config['client_y'] = [root.winfo_width(), root.winfo_height(), root.winfo_x(), root.winfo_y()]
    root.destroy()


root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()


#clean up
kill_server()
keep_download = False



with open('config.yaml', 'w') as f:
    yaml.dump(config, f)
with open('games.yaml', 'w') as f:
    yaml.dump({'version': gamelist_version, 'games': games}, f)
