import requests, json, csv, os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm


def get_raw_items(lang="hindi", pages=10):
    items = {}
    items.setdefault("items", [])
    for i in range(1, pages+1):
        x = requests.post(
            "https://oshoworld.com/api/server/audio/search-series-home",
            data={
                "page": i,
                "language": lang
            }
        )
        items["items"] += (x.json()["items"])
    return items


def write_to_json(items_dict, lang="hindi"):
    with open(f"items-{lang}.json", "w", encoding='utf-8') as f:
        f.write(json.dumps(items_dict, ensure_ascii=False))


def extract_to_csv(lang="hindi"):
    with open(f"items-{lang}.json", "r") as f:
        items = json.load(f)['items']
    with open(f"items-{lang}.csv", 'w') as f:
        writer = csv.DictWriter(f, fieldnames=items[0].keys(), extrasaction='ignore')
        writer.writeheader()
        writer.writerows(items)
        for item in items:
            if item.get('countSeries'):
                # This is a series of discourses
                # 663f36a98113078817866f03,040-055,Geeta Darshan,audio-series-geeta-darshan-all,uploads/no_image.png,17
                item['count'] = item.pop('countSeries')
                if item["_id"] == "663f36a98113078817866f03":
                    geeta = [{'index': '040', 'title': 'Geeta Darshan Vol-1 & 2 # 1-18', 'slug': 'geeta-darshan-vol-1-2-by-osho-1-18', 'image': 'uploads/no_image.png', 'count': 18}, {'index': '041', 'title': 'Geeta Darshan Vol-3 # 1-10', 'slug': 'geeta-darshan-vol-3-by-osho-1-10', 'image': 'uploads/no_image.png', 'count': 10}, {'index': '042', 'title': 'Geeta Darshan Vol-4 # 1-18', 'slug': 'geeta-darshan-vol-4-by-osho-1-18', 'image': 'uploads/no_image.png', 'count': 18}, {'index': '043', 'title': 'Geeta Darshan Vol-5 # 1-11', 'slug': 'geeta-darshan-vol-5-by-osho-1-11', 'image': 'uploads/no_image.png', 'count': 11}, {'index': '044', 'title': 'Geeta Darshan Vol-6 # 1-21', 'slug': 'geeta-darshan-vol-6-by-osho-1-21', 'image': 'uploads/no_image.png', 'count': 21}, {'index': '045', 'title': 'Geeta Darshan Vol-7 # 1-10', 'slug': 'geeta-darshan-vol-7-by-osho-1-10', 'image': 'uploads/no_image.png', 'count': 10}, {'index': '046', 'title': 'Geeta Darshan Vol-8 # 1-11', 'slug': 'geeta-darshan-vol-8-by-osho-1-11', 'image': 'uploads/no_image.png', 'count': 11}, {'index': '047', 'title': 'Geeta Darshan Vol-9 # 1-13', 'slug': 'geeta-darshan-vol-9-by-osho-1-13', 'image': 'uploads/no_image.png', 'count': 13}, {'index': '048', 'title': 'Geeta Darshan Vol-10 # 1-15', 'slug': 'geeta-darshan-vol-10-by-osho-1-15', 'image': 'uploads/no_image.png', 'count': 15}, {'index': '049', 'title': 'Geeta Darshan Vol-11 # 1-12', 'slug': 'geeta-darshan-vol-11-by-osho-1-12', 'image': 'uploads/no_image.png', 'count': 12}, {'index': '050', 'title': 'Geeta Darshan Vol-12 # 1-11', 'slug': 'geeta-darshan-vol-12-by-osho-1-11', 'image': 'uploads/no_image.png', 'count': 11}, {'index': '051', 'title': 'Geeta Darshan Vol-13 # 1-12', 'slug': 'geeta-darshan-vol-13-by-osho-1-12', 'image': 'uploads/no_image.png', 'count': 12}, {'index': '052', 'title': 'Geeta Darshan Vol-14 # 1-10', 'slug': 'geeta-darshan-vol-14-by-osho-1-10', 'image': 'uploads/no_image.png', 'count': 10}, {'index': '053', 'title': 'Geeta Darshan Vol-15 # 1-7', 'slug': 'geeta-darshan-vol-15-by-osho-1-7', 'image': 'uploads/no_image.png', 'count': 7}, {'index': '054', 'title': 'Geeta Darshan Vol-16 # 1-8', 'slug': 'geeta-darshan-vol-16-by-osho-1-8', 'image': 'uploads/no_image.png', 'count': 8}, {'index': '055', 'title': 'Geeta Darshan Vol-17 # 1-11', 'slug': 'geeta-darshan-vol-17-by-osho-1-11', 'image': 'uploads/no_image.png', 'count': 11}]
                    for i in geeta:
                        i["_id"] = "663f36a98113078817866f03"
                        # writer.writerow(i) WRONG!!!


def write_per_item_json(lang="hindi"):
    with open(f"items-{lang}.csv", "r") as f:
        reader = csv.DictReader(f)
        ics = [(i["_id"], int(i["count"]), i["slug"]) for i in reader]
    with open(f"items-{lang}-listdata.json", 'w') as f:
        listdata = {}
        for id, count, slug in ics:
            x = requests.post(
                "https://oshoworld.com/api/server/audio/series-filter",
                json={
                    "perPage": count,
                    "currentId": id
                }
            )
            listdata[slug] = x.json()["listData"]
        f.write(json.dumps(listdata, ensure_ascii=False))


def all_urls(lang="hindi"):
    with open(f"items-{lang}-listdata.json", 'r') as f:
        listdata = json.load(f)
    urls = {}
    for key, values in listdata.items():
        urls[key] = ["https://oshoworld.com" + item["file"] for item in values]
    print(urls)
    return urls


def get_count(lang="hindi"):
    count = 0
    with open(f"items-{lang}.csv", "r") as f:
        reader = csv.DictReader(f)
        for i in reader:
            # print(i["count"])
            count += int(str(i["count"]))
    print(count)

def download(lang="hindi"):
    def _start_download(url, path):
        with requests.get(url, stream=True, timeout=30) as r:
            r.raise_for_status()
            with open(str(path) + "/" + url.split("/")[-1], "wb") as f:
                for chunk in r.iter_content(chunk_size=1024*1024):
                    if chunk:
                        f.write(chunk)
        return path

    urls = all_urls(lang)
    for slug, url_list in urls.items():
        path = Path(f"{lang}/{slug}")
        path.mkdir(parents=True, exist_ok=True)
        with ThreadPoolExecutor(max_workers=8) as exec:
            futures = [exec.submit(_start_download, url, path) for url in url_list]
            with tqdm(total=len(futures), desc=f"Downloaing {slug}") as bar:
                for future in as_completed(futures):
                    try:
                        path = future.result()
                    except Exception as e:
                        print(f"Failed: {e}")
                    finally:
                        bar.update(1)


lang_env = os.environ.get("LANG", "hindi")
if lang_env in ["en", "english"]:
    lang = "english"
elif lang_env in ["hi", "hindi"]:
    lang = "hindi"

# items = get_raw_items(lang, pages=11)
# write_to_json(items, lang)
# extract_to_csv(lang)
# write_per_item_json(lang)
# all_urls(lang)
# get_count(lang)
download(lang)
