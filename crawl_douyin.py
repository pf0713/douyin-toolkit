"""
爬取抖音今日热榜，保存为 JSON
"""
import json
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

APIS = [
    # DailyHotApi 聚合接口
    "https://api-hot.imsyy.top/douyin?cache=true",
    # 备用
    "https://hotlist.imsyy.top/douyin?cache=true",
    # vvhan
    "https://api.vvhan.com/api/hotlist/douyin",
    # tenapi
    "https://tenapi.cn/v2/douyinhot",
]


def try_apis():
    for url in APIS:
        try:
            print(f"尝试: {url}")
            r = requests.get(url, headers=HEADERS, timeout=10)
            if r.status_code == 200:
                data = r.json()
                items = data.get("data", [])
                if items:
                    return items, url
        except Exception as e:
            print(f"  失败: {e}")
    return None, None


def parse_items(items):
    """统一解析不同 API 返回格式"""
    results = []
    for item in items:
        title = item.get("title") or item.get("name") or item.get("word") or ""
        hot = item.get("hot") or item.get("hotValue") or item.get("heat") or ""
        if title:
            results.append({"title": title, "hot": str(hot), "rank": len(results) + 1})
    return results


def main():
    print("=== 抖音热榜爬虫 ===\n")
    items, source = try_apis()

    if items:
        results = parse_items(items)
        out = {
            "source": source,
            "count": len(results),
            "data": results,
        }
        path = "C:/Users/86151/Desktop/CC实验/douyin_hot.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 成功爬取 {len(results)} 条热榜数据 → {path}")
        print("\n=== 热榜前30 ===")
        for r in results[:30]:
            print(f"  {r['rank']:2d}. {r['title']} | {r['hot']}")
    else:
        print("❌ 所有 API 均失败，请检查网络或更换 API")


if __name__ == "__main__":
    main()
