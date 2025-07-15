import os
import requests


def check_folder_exists(
        ydex_api_key,
        path,
        ydex_api_path
):
    headers = {"Authorization": f"OAuth {ydex_api_key}"}
    params = {"path": path}

    response = requests.get(f"{ydex_api_path}", headers=headers, params=params)

    if response.status_code == 200:
        return True
    elif response.status_code == 404:
        response = requests.put(f"{ydex_api_path}", headers=headers, params=params)
        if response.status_code == 201:
            print(f"Папка '{path}' успешно создана.")
            return True
        else:
            print(f"Ошибка при создании папки '{path}': {response.json()}")
            return False
    else:
        print(f"Ошибка при проверке папки '{path}': {response.json()}")
        return False


def upload_to_ydisk(
        nmap_data,
        nmap_app_path,
        nmap_data_folder,
        ydex_api_key,
        ydex_api_path
):
    file_name = os.path.basename(nmap_data)
    disk_path = f"{nmap_app_path}/{nmap_data_folder}/{file_name}"

    print(disk_path)
    print(nmap_data)

    headers = {"Authorization": f"OAuth {ydex_api_key}"}
    params = {"path": disk_path, "overwrite": "true"}

    response = requests.get(f"{ydex_api_path}/upload", headers=headers, params=params)

    if response.status_code != 200:
        print("Ошибка получения ссылки для загрузки:", response.json())
        return False

    upload_href = response.json()["href"]

    with open(nmap_data, "rb") as file_data:
        upload_response = requests.put(upload_href, data=file_data)

    if upload_response.status_code == 201:
        print(f"Файл '{file_name}' успешно загружен на Яндекс.Диск.")

        try:
            os.remove(nmap_data)
            print(f"Локальный файл '{nmap_data}' удален.")
        except OSError as e:
            print(f"Ошибка при удалении файла '{nmap_data}': {e}")

        return True
    else:
        print(f"Ошибка при загрузке файла '{file_name}': {upload_response.text}")
        return False


def check_and_create_root_folder(
        nmap_app_path,
        ydex_api_key,
        ydex_api_path
):
    return check_folder_exists(
        ydex_api_key,
        nmap_app_path,
        ydex_api_path
    )


def check_or_create_data_folder(
        nmap_app_path,
        nmap_data_folder,
        ydex_api_key,
        ydex_api_path
):
    full_path = f"{nmap_app_path}/{nmap_data_folder}"
    print(full_path)
    return check_folder_exists(ydex_api_key, full_path, ydex_api_path)
