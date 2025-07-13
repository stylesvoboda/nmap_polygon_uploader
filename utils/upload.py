import os
import requests


def check_folder_exists(disk_token, path, disk_base_url):
    headers = {"Authorization": f"OAuth {disk_token}"}
    params = {"path": path}

    response = requests.get(f"{disk_base_url}", headers=headers, params=params)

    if response.status_code == 200:
        return True
    elif response.status_code == 404:
        response = requests.put(f"{disk_base_url}", headers=headers, params=params)
        if response.status_code == 201:
            print(f"Папка '{path}' успешно создана.")
            return True
        else:
            print(f"Ошибка при создании папки '{path}': {response.json()}")
            return False
    else:
        print(f"Ошибка при проверке папки '{path}': {response.json()}")
        return False


def upload_to_ydisk(local_file_path, disk_base_folder, current_date_folder, disk_token, disk_base_url):
    file_name = os.path.basename(local_file_path)
    disk_path = f"{disk_base_folder}/{current_date_folder}/{file_name}"

    print(disk_path)

    headers = {"Authorization": f"OAuth {disk_token}"}
    params = {"path": disk_path, "overwrite": "true"}

    response = requests.get(f"{disk_base_url}/upload", headers=headers, params=params)

    if response.status_code != 200:
        print("Ошибка получения ссылки для загрузки:", response.json())
        return False

    upload_href = response.json()["href"]

    with open(local_file_path, "rb") as file_data:
        upload_response = requests.put(upload_href, data=file_data)

    if upload_response.status_code == 201:
        print(f"Файл '{file_name}' успешно загружен на Яндекс.Диск.")

        try:
            os.remove(local_file_path)
            print(f"Локальный файл '{local_file_path}' удален.")
        except OSError as e:
            print(f"Ошибка при удалении файла '{local_file_path}': {e}")

        return True
    else:
        print(f"Ошибка при загрузке файла '{file_name}': {upload_response.text}")
        return False


def check_and_create_root_folder(disk_base_folder, disk_token, disk_base_url):
    return check_folder_exists(disk_token, disk_base_folder, disk_base_url)


def check_or_create_data_folder(disk_base_folder, current_date_folder, disk_token, disk_base_url):
    full_path = f"{disk_base_folder}/{current_date_folder}"
    print(full_path)
    return check_folder_exists(disk_token, full_path, disk_base_url)
