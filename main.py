import json
import os
import uuid
from datetime import datetime

import geopandas as gpd

from utils.download_ydisk import download_index_json_if_exists
from utils.settings import *
from utils.upload_ydisk import upload_to_ydisk, check_and_create_root_folder, \
    check_or_create_data_folder

nmap_data_folder = datetime.now().strftime("%Y-%m-%d")
print(f"Папка для текущей даты: {nmap_data_folder}")


def read_and_remove_archive(def_shp_data, def_shp_name):
    try:
        gdf = gpd.read_file(f"zip://{def_shp_data}!{def_shp_name}", encoding="utf-8")

        try:
            os.remove(def_shp_data)
            print("Shapefile обработан и удалён.")
        except FileNotFoundError:
            print("Shapefile для удаления не обнаружен.")

        return gdf

    except Exception as err:
        print(f"Ошибка при чтении Shapefile: {err}")
        return None


gdf = read_and_remove_archive(def_shp_data, def_shp_name)

if gdf is not None:
    print("Данные успешно загружены")
else:
    print("Ошибка при загрузке данных")
    exit(1)


def extract_geometry(geometry):
    geom_type = geometry.geom_type

    if geom_type == 'Polygon':
        return [
            [list(coord) for coord in geometry.exterior.coords],
            *[[list(coord) for coord in interior.coords] for interior in geometry.interiors]
        ]
    elif geom_type == 'MultiPolygon':
        return [
            [
                [list(coord) for coord in poly.exterior.coords],
                *[[list(coord) for coord in interior.coords] for interior in poly.interiors]
            ]
            for poly in geometry.geoms
        ]
    elif geom_type == 'LineString':
        return [list(coord) for coord in geometry.coords]
    elif geom_type == 'MultiLineString':
        return [list(list(coords) for coords in line.coords) for line in geometry.geoms]
    elif geom_type == 'Point':
        return list(geometry.coords[0])
    elif geom_type == 'MultiPoint':
        return [list(point.coords[0]) for point in geometry.geoms]
    elif geom_type == 'GeometryCollection':
        result = []
        for geom in geometry.geoms:
            try:
                result.append(extract_geometry(geom))
            except ValueError:
                continue
        return result
    else:
        raise ValueError(f"Неподдерживаемый тип геометрии: {geom_type}")


remote_folder = os.path.join(nmap_app_path, nmap_data_folder)

# 1. Проверяем наличие index.json на Яндекс Диске
index_exists = download_index_json_if_exists(
    ydex_api_key,
    remote_folder,
    nmap_data,
    local_index_path,
    ydex_api_path
)

output = {
    "paths": {},
    "points": {}
}

# 2. Если index.json найден, загружаем его и объединяем с новым output после извлечения геометрии
if index_exists:
    with open(local_index_path, "r", encoding="utf-8") as f:
        old_data = json.load(f)
    # После извлечения геометрии (после цикла по gdf) объединяем output
    merge_old_index = True
    os.remove(local_index_path)
else:
    merge_old_index = False

for _, row in gdf.iterrows():
    try:
        geom = row.geometry
        geom_type = geom.geom_type

        if geom_type == 'Polygon':
            # Внешний контур как LineString
            exterior_coords = [list(coord) for coord in geom.exterior.coords]
            poly_uuid = str(uuid.uuid4())
            output["paths"][poly_uuid] = exterior_coords
            # Внутренние контуры как отдельные LineString
            for interior in geom.interiors:
                interior_coords = [list(coord) for coord in interior.coords]
                interior_uuid = str(uuid.uuid4())
                output["paths"][interior_uuid] = interior_coords

        elif geom_type == 'MultiPolygon':
            for poly in geom.geoms:
                # Внешний контур как LineString
                exterior_coords = [list(coord) for coord in poly.exterior.coords]
                poly_uuid = str(uuid.uuid4())
                output["paths"][poly_uuid] = exterior_coords
                # Внутренние контуры как отдельные LineString
                for interior in poly.interiors:
                    interior_coords = [list(coord) for coord in interior.coords]
                    interior_uuid = str(uuid.uuid4())
                    output["paths"][interior_uuid] = interior_coords

        elif geom_type in ['LineString', 'MultiLineString', 'GeometryCollection']:
            coords = extract_geometry(geom)
            if isinstance(coords[0], list):
                for path_coords in coords:
                    poly_uuid = str(uuid.uuid4())
                    output["paths"][poly_uuid] = [path_coords]
            else:
                poly_uuid = str(uuid.uuid4())
                output["paths"][poly_uuid] = [coords]

        elif geom_type in ['Point', 'MultiPoint']:
            coords = extract_geometry(geom)
            if isinstance(coords[0], list):
                for point_coords in coords:
                    point_uuid = str(uuid.uuid4())
                    output["points"][point_uuid] = point_coords
            else:
                point_uuid = str(uuid.uuid4())
                output["points"][point_uuid] = coords

    except ValueError as e:
        print(f"Пропущена геометрия: {e}")
    except Exception as e:
        print(f"Ошибка при обработке строки: {e}")

# После цикла объединяем, если был старый index.json
if merge_old_index:
    output["paths"].update(old_data.get("paths", {}))
    output["points"].update(old_data.get("points", {}))

with open("index.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=4)

check_and_create_root_folder(
    nmap_app_path,
    ydex_api_key,
    ydex_api_path
)

check_or_create_data_folder(
    nmap_app_path,
    nmap_data_folder,
    ydex_api_key,
    ydex_api_path
)

upload_to_ydisk(
    nmap_data,
    nmap_app_path,
    nmap_data_folder,
    ydex_api_key,
    ydex_api_path
)
