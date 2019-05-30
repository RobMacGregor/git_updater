# coding: utf-8

import sha
import urequests
import os
import machine
from config import *


def do_connect(essid, password):
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(essid, password)
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())

def get_content_from_github(repo_owner, repo_name, folder=''):
    """
    Функция возвращает файлы и папки из репозитория гитхаб в указанной папке
    """
    url_folder = 'https://api.github.com/repos/{0}/{1}/contents/{2}'
    contents_url = url_folder.format(repo_owner, repo_name, folder)
    print(contents_url)
    r = urequests.get(contents_url)
    if r.status_code == 200:
        return r.json()
    elif r.status_code == 404:
        print("User or repo not found")
        return None
    elif int(str(r.status_code)[:2]) == 50:
        print("Server error")
        return None
    
def get_content_from_folder(repo_name, folder=''):
    """
    Функция возвращает файлы из папки
    """
    if folder == '':
        try:
            return os.listdir(repo_name)
        except FileNotFoundError:
            os.mkdir(repo_name)
            return []
    else:
        return os.listdir(str(repo_name) + '/' + str(folder))
    
def md5sum(filename):
    """
    Возвращает md5 sum файла
    """
    with open(filename, mode='rb') as f:
        d = sha.SHA1()
        d.update(f.read())
    return d.hexdigest()


def md5sum_git(stroke):
    """
    Возвращает md5 sum строки
    """
    d = sha.SHA1()
    d.update(stroke)
    return d.hexdigest()


def compare_files(file_from_folder, file_from_github):
    """
    Функция сравнивает два файла
    """
    md5_folder = md5sum(file_from_folder)
    md5_github = md5sum_git(file_from_github)
    if md5_folder == md5_github:
        return 0
    else:
        return 1
    
def update(repo_owner, repo_name, essid, password):
    "Функция служит для обновления указанного репозитория github"
	need_reload = 0
	
	do_connect(essid, password)
    
    folder = ''
    current_files_github = get_content_from_github(repo_owner, repo_name, folder='')
    current_files_folder = get_content_from_folder(repo_name, folder='')
    current_folder = ''
    for file in current_files_github:
        if file['name'] not in current_files_folder:
            print("Загрузить файл", file['name'])
            r = urequests.get(file['download_url'])
            with open(str(current_folder) + str(repo_name) + '/' + str(file['name']), 'w') as f:
                f.write(r.content.decode("utf-8"))
			need_reload = 1
        else:
            print("Сравнить файлы", file['name'])
            r = urequests.get(file['download_url'])
            if compare_files(str(current_folder) + str(repo_name) + '/' + str(file['name']), r.content) == 0:
                print('Файлы одинаковые')
            else:
                print('Файлы разные, загружаем файл с github')
                with open(str(current_folder) + str(repo_name) + '/' + str(file['name']), 'w') as f:
                    f.write(r.content.decode("utf-8"))
				need_reload = 1
			current_files_folder.remove(str(file['name']))
	if current_files_folder != []:
		for file in current_files_folder:
			print('Файл {0} отсутствует на github. Удалить'.format(file))
			os.remove(str(current_folder) + str(repo_name) + '/' + str(file['name']))
		
	if need_reload == 1:
		machine.reset()
		return 1
	else:
		return 0

update(repo_owner, repo_name, essid, password)