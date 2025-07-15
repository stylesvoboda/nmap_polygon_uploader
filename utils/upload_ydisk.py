import os
import requests


def check_folder_exists(
        YDEX_API_KEY,
        path,
        YDEX_API_PATH
):
    headers = {"Authorization": f"OAuth {YDEX_API_KEY}"}
    params = {"path": path}

    response = requests.get(f"{YDEX_API_PATH}", headers=headers, params=params)

    if response.status_code == 200:
        return True
    elif response.status_code == 404:
        response = requests.put(f"{YDEX_API_PATH}", headers=headers, params=params)
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
        NMAP_DATA,
        NMAP_APP_PATH,
        current_date_folder,
        YDEX_API_KEY,
        YDEX_API_PATH
):
    file_name = os.path.basename(NMAP_DATA)
    disk_path = f"{NMAP_APP_PATH}/{current_date_folder}/{file_name}"

    print(disk_path)
    print(NMAP_DATA)

    headers = {"Authorization": f"OAuth {YDEX_API_KEY}"}
    params = {"path": disk_path, "overwrite": "true"}

    response = requests.get(f"{YDEX_API_PATH}/upload", headers=headers, params=params)

    if response.status_code != 200:
        print("Ошибка получения ссылки для загрузки:", response.json())
        return False

    upload_href = response.json()["href"]

    with open(NMAP_DATA, "rb") as file_data:
        upload_response = requests.put(upload_href, data=file_data)

    if upload_response.status_code == 201:
        print(f"Файл '{file_name}' успешно загружен на Яндекс.Диск.")

        try:
            os.remove(NMAP_DATA)
            print(f"Локальный файл '{NMAP_DATA}' удален.")
        except OSError as e:
            print(f"Ошибка при удалении файла '{NMAP_DATA}': {e}")

        return True
    else:
        print(f"Ошибка при загрузке файла '{file_name}': {upload_response.text}")
        return False


def check_and_create_root_folder(
        NMAP_APP_PATH,
        YDEX_API_KEY,
        YDEX_API_PATH
):
    return check_folder_exists(
        YDEX_API_KEY,
        NMAP_APP_PATH,
        YDEX_API_PATH
    )


def check_or_create_data_folder(
        NMAP_APP_PATH,
        current_date_folder,
        YDEX_API_KEY,
        YDEX_API_PATH
):
    full_path = f"{NMAP_APP_PATH}/{current_date_folder}"
    print(full_path)
    return check_folder_exists(YDEX_API_KEY, full_path, YDEX_API_PATH)
