"""
路网数据获取脚本（Road Network Data Fetching）
==============================================
通过高德开放平台 API（AMap API）获取：
  1) 地级行政区的经纬度（地理编码 / 行政区划接口）
  2) 城间驾车距离与行车耗时（距离测量接口）

输出：
  data/raw/cities.csv           行政区编码、名称、经度、纬度
  data/raw/distance_matrix.csv  城间距离（km）与行车耗时（分钟）

安全红线：API Key 仅从环境变量读取（见 config.py），绝不入库。
"""
from __future__ import annotations

import csv
import time
from pathlib import Path

import requests

from config import RAW_DIR, get_amap_api_key

AMAP_GEOCODE_URL = "https://restapi.amap.com/v3/geocode/geo"
AMAP_DISTANCE_URL = "https://restapi.amap.com/v3/distance"


def geocode_city(city_name: str, api_key: str) -> tuple[str, str] | None:
    """地理编码：城市名 -> (经度 lng, 纬度 lat)。失败返回 None。"""
    resp = requests.get(
        AMAP_GEOCODE_URL,
        params={"key": api_key, "address": city_name, "city": city_name},
        timeout=15,
    )
    data = resp.json()
    if data.get("status") == "1" and data.get("geocodes"):
        loc = data["geocodes"][0].get("location", "")
        if loc:
            lng, _, lat = loc.partition(",")
            return lng, lat
    return None


def fetch_city_coordinates(city_names: list[str], api_key: str) -> list[dict]:
    """
    批量地理编码。
    注意：高德个人开发者 QPS 有限，需按间隔限速（Rate Limit）。
    """
    cities = []
    for i, name in enumerate(city_names):
        loc = geocode_city(name, api_key)
        if loc:
            cities.append({"city": name, "lng": loc[0], "lat": loc[1]})
        else:
            print(f"[warn] 地理编码失败: {name}")
        time.sleep(0.3)  # 限速，防止触发风控
    return cities


def fetch_distance(orig: str, dest: str, api_key: str) -> dict | None:
    """两点驾车距离：返回 {'distance_km': float, 'duration_min': float}。"""
    resp = requests.get(
        AMAP_DISTANCE_URL,
        params={"key": api_key, "origins": orig, "destination": dest, "type": "1"},
        timeout=15,
    )
    data = resp.json()
    if data.get("status") == "1" and data.get("results"):
        r = data["results"][0]
        return {
            "distance_km": round(float(r.get("distance", 0)) / 1000, 1),
            "duration_min": round(float(r.get("duration", 0)) / 60, 1),
        }
    return None


def build_distance_matrix(cities: list[dict], api_key: str) -> None:
    """
    构建城间距离/耗时矩阵（全量 337×337 会触发大量请求，
    建议按需只算 候选仓×需求点 或分批断点续传）。
    """
    n = len(cities)
    out = RAW_DIR / "distance_matrix.csv"
    with out.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["origin", "dest", "distance_km", "duration_min"])
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                r = fetch_distance(
                    f"{cities[i]['lng']},{cities[i]['lat']}",
                    f"{cities[j]['lng']},{cities[j]['lat']}",
                    api_key,
                )
                if r:
                    writer.writerow(
                        [cities[i]["city"], cities[j]["city"], r["distance_km"], r["duration_min"]]
                    )
                time.sleep(0.2)


def main(city_list_file: str | None = None) -> None:
    """
    入口：city_list_file 为城市名单文件（每行一个城市名）。
    未提供时使用内置最小样例（正式运行请替换为 337 个地级行政区名单）。
    """
    api_key = get_amap_api_key()
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    if city_list_file:
        names = [ln.strip() for ln in Path(city_list_file).read_text().splitlines() if ln.strip()]
    else:
        # TODO: 替换为完整 337 地级行政区名单（材料归位后落地）
        names = ["北京市", "上海市", "广州市", "深圳市", "成都市"]

    cities = fetch_city_coordinates(names, api_key)

    out = RAW_DIR / "cities.csv"
    with out.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["city", "lng", "lat"])
        writer.writeheader()
        writer.writerows(cities)
    print(f"[ok] 城市坐标已写入 {out}（{len(cities)} 个城市）")


if __name__ == "__main__":
    main()
