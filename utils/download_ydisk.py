import requests
import os


def download_index_json_if_exists(token, remote_folder, filename, local_path, base_url):
    headers = {"Authorization": f"OAuth {token}"}
    disk_path = os.path.join(remote_folder, filename)
    params = {"path": disk_path}

    meta_url = f"{base_url}"
    resp = requests.get(meta_url, headers=headers, params=params)
    if resp.status_code != 200:
        return False
    download_url = f"{base_url}/download"
    resp = requests.get(download_url, headers=headers, params=params)
    if resp.status_code != 200:
        return False
    href = resp.json().get("href")
    if not href:
        return False

    r = requests.get(href)
    if r.status_code == 200:
        with open(local_path, "wb") as f:
            f.write(r.content)
        return True
    return False
