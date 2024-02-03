#【参考】https://qiita.com/ZeroQuake/items/e6dd2691fe8fa5e2b3b2
from PIL import Image
import requests
from io import BytesIO
import json

def generate_geojson(url, MeshCode):
    # メッシュコードから地理的な境界を計算
    lat = int(MeshCode[:2]) / 1.5
    lng = int(MeshCode[2:4]) + 100
    lat2 = lat + 2 / 3
    lng2 = lng + 1
    
    # ウェブから画像をロード
    image_url = f"https://www.jma.go.jp/bosai/estimated_intensity_map/data/{url}/{MeshCode}.png"
    response = requests.get(image_url)
    # img = Image.open(BytesIO(response.content)).resize((800, 800))
    
    # レスポンスから画像をロード
    img = Image.open(BytesIO(response.content))
    
    # 画像をRGBAモードに変換（必要な場合）
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # 画像のサイズを変更
    img = img.resize((800, 800))

    # 画像データ解析の準備
    img_data = img.load()
    EstimateShindoData = []
    
    # 画像を分析してGeoJSONデータを構築
    y = 1
    for i in range(320):
        x = 1
        for j in range(320):
            r, g, b, a = img_data[x, y]
            intensity = None
            
            # 透明度が50を超えるピクセルについて色を分析
            if a > 50:
                # 色に基づいて震度を判定
                if abs(r - 250) < 16 and abs(g - 230) < 16 and abs(b - 150) < 16: intensity = "4"
                elif abs(r - 255) < 16 and abs(g - 230) < 16 and abs(b - 0) < 16: intensity = "5-"
                elif abs(r - 255) < 16 and abs(g - 153) < 16 and abs(b - 0) < 16: intensity = "5+"
                elif abs(r - 255) < 16 and abs(g - 40) < 16 and abs(b - 0) < 16: intensity = "6-"
                elif abs(r - 165) < 16 and abs(g - 0) < 16 and abs(b - 33) < 16: intensity = "6+"
                elif abs(r - 180) < 16 and abs(g - 0) < 16 and abs(b - 104) < 16: intensity = "7"
                
                # 震度が識別された場合、GeoJSONデータを構築
                if intensity:
                    North = lat2 + ((lat - lat2) / 320) * i
                    South = lat2 + ((lat - lat2) / 320) * (i + 1)
                    West = lng + ((lng2 - lng) / 320) * j
                    East = lng + ((lng2 - lng) / 320) * (j + 1)
                    
                    EstimateShindoData.append({
                        "type": "Feature",
                        # "properties": {"rgb": [r, g, b], "Intensity": intensity},
                        "properties": {"Intensity": intensity},
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [[
                                [West, North],
                                [East, North],
                                [East, South],
                                [West, South],
                                [West, North]
                            ]]
                        }
                    })
            # JavaScriptのx,y座標の更新ロジックを反映
            if j % 2 == 0: x += 3
            else: x += 2
        if i % 2 == 0: y += 2
        else: y += 3
    
    # GeoJSONオブジェクトを構築
    return {
        "type": "FeatureCollection",
        "features": EstimateShindoData
    }

# 例えば、複数のURLとメッシュコードのリストがある場合
url_mesh_codes = [
   {"url": "202401011610_390", "MeshCode": "5135"},
    {"url": "202401011610_390", "MeshCode": "5235"},
    {"url": "202401011610_390", "MeshCode": "5236"},
    {"url": "202401011610_390", "MeshCode": "5237"},
    {"url": "202401011610_390", "MeshCode": "5334"},
    {"url": "202401011610_390", "MeshCode": "5335"},
    {"url": "202401011610_390", "MeshCode": "5336"},
    {"url": "202401011610_390", "MeshCode": "5337"},
    {"url": "202401011610_390", "MeshCode": "5338"},
    {"url": "202401011610_390", "MeshCode": "5435"},
    {"url": "202401011610_390", "MeshCode": "5436"},
    {"url": "202401011610_390", "MeshCode": "5437"},
    {"url": "202401011610_390", "MeshCode": "5438"},
    {"url": "202401011610_390", "MeshCode": "5439"},
    {"url": "202401011610_390", "MeshCode": "5440"},
    {"url": "202401011610_390", "MeshCode": "5536"},
    {"url": "202401011610_390", "MeshCode": "5537"},
    {"url": "202401011610_390", "MeshCode": "5538"},
    {"url": "202401011610_390", "MeshCode": "5539"},
    {"url": "202401011610_390", "MeshCode": "5636"},
    {"url": "202401011610_390", "MeshCode": "5637"},
    {"url": "202401011610_390", "MeshCode": "5638"},
    {"url": "202401011610_390", "MeshCode": "5639"},
    {"url": "202401011610_390", "MeshCode": "5640"},
    {"url": "202401011610_390", "MeshCode": "5738"},
    {"url": "202401011610_390", "MeshCode": "5739"},
    {"url": "202401011610_390", "MeshCode": "5740"},
    {"url": "202401011610_390", "MeshCode": "5839"}
]

# 全てのGeoJSONフィーチャをマージ
all_features = []
for item in url_mesh_codes:
    geojson = generate_geojson(item['url'], item['MeshCode'])
    all_features.extend(geojson['features'])

# 最終的なGeoJSONオブジェクト
final_geojson = {
    "type": "FeatureCollection",
    "features": all_features
}

# GeoJSONデータをファイルに保存
output_file_path = 'estimated_shindo_3.geojson'
with open(output_file_path, 'w') as file:
    json.dump(final_geojson, file)

print(f"GeoJSONデータが{output_file_path}に保存されました。")
