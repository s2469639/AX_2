import os
import requests

def get_kakao_api_key():
    return os.getenv("KAKAO_REST_KEY") or os.getenv("MAP_API_KEY")

def search_places_kakao(keyword: str):
    """카카오 로컬 키워드 검색 API 호출"""
    api_key = get_kakao_api_key()
    if not api_key:
        return []
    
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {api_key}"}
    params = {"query": keyword, "size": 5}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=5)
        response.raise_for_status()
        documents = response.json().get("documents", [])
        
        results = []
        for doc in documents:
            results.append({
                "name": doc.get("place_name"),
                "address": doc.get("road_address_name") or doc.get("address_name"),
                "phone": doc.get("phone", ""),
                "lat": float(doc.get("y")),
                "lng": float(doc.get("x")),
                "url": doc.get("place_url", "")
            })
        return results
    except Exception:
        return []

def search_category_kakao(cat_code: str, lat: float, lng: float, radius: int = 1500):
    """주변 편의시설 (식당/카페/편의점) 검색 API 호출"""
    api_key = get_kakao_api_key()
    if not api_key:
        return []
    
    url = "https://dapi.kakao.com/v2/local/search/category.json"
    headers = {"Authorization": f"KakaoAK {api_key}"}
    params = {
        "category_group_code": cat_code,
        "x": str(lng),
        "y": str(lat),
        "radius": radius,
        "size": 15,
        "sort": "distance"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=5)
        response.raise_for_status()
        documents = response.json().get("documents", [])
        
        results = []
        for doc in documents:
            results.append({
                "name": doc.get("place_name"),
                "address": doc.get("road_address_name") or doc.get("address_name"),
                "phone": doc.get("phone", ""),
                "distance": doc.get("distance", ""),
                "lat": float(doc.get("y")),
                "lng": float(doc.get("x")),
                "url": doc.get("place_url", "")
            })
        return results
    except Exception:
        return []