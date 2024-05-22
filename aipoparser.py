import itertools
import json
import datetime
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# The only global variable, its ugly, but I dont know how to cleanly get rid of it
icid_codes_amount = 251

def aipo_request(icid_code : str = '', certificate_id : str = '', language : str = '') -> requests.Response:
    return requests.request(
        'post',
        'https://aipo.am/' + language + '//ajax/search_mods_search_int_classification',
        data={
            'logic': 'partial',
            'FMAD': icid_code,
            'Reg_num': certificate_id,

            'App_num':'',
            'App_date':'',
            'name':'',
            'AppPers':'',
            'Auth':'',
            'Owner':''
        }
    )

def get_patent_by_id(id : int, language : str) -> dict:
    response = aipo_request(certificate_id=id, language=language)
    try:
        application_id, title, certificate_id = BeautifulSoup(response.text, features="html.parser").find_all("td")
    except ValueError:
        return dict()
    
    return {
        "certificate_id": int(certificate_id.get_text()),
        "application_id": int(application_id.get_text()),
        "title": title.get_text(),
        "patent_link": 'https://old.aipa.am/search_mods/industrial_design/view_item.php?id=' + \
            certificate_id.get_text() + '&language=' + language
    }

def get_group_by_icid_code(icid_code : str, language : str):
    response = aipo_request(icid_code=icid_code, language=language)
    soup = BeautifulSoup(response.text, features="html.parser")
    
    group = {
        "ICID_code": icid_code,
        "data": []
    }
    for (application_id, title, certificate_id) in itertools.batched(soup.find_all("td"), n=3):
        group['data'].append({
            "certificate_id": int(certificate_id.get_text()),
            "application_id": int(application_id.get_text()),
            "title": title.get_text(),
            "patent_link": 'https://old.aipa.am/search_mods/industrial_design/view_item.php?id=' + \
                certificate_id.get_text() + '&language=' + language
        })
    return group

def generate_icid_codes():
    global icid_codes_amount 
    try:
        with open("./data/ICID codes.json") as f:
            classes = json.load(f)["classes"]
        icid_codes_amount = 251
        for icid_class in classes:
            for subclass in classes[icid_class]:
                yield icid_class + '-' + subclass
    except FileNotFoundError:
        print("There is no './data/ICID codes.json' present, do you want to generate ICID codes by bruteforce?")
        assert input("[y/n] >>>").strip().lower() == 'y', "Make sure you have './data/ICID codes.json' present"
        icid_codes_amount = 32 * 20
        for icid_class in map(str, range(1, 33)):
            for subclass in map(str, range(0, 19)):
                yield icid_class.zfill(2) + '-' + subclass.zfill(2)
            yield icid_class.zfill(2) + '-99'

def fix_patents_list(downloaded_patents : list, languge : str):
    downloaded_patents.sort(key = lambda patent: patent["certificate_id"])
    progress = tqdm(
        enumerate(downloaded_patents, start=1), 
        total=downloaded_patents[-1]["certificate_id"]
    )
    for (i, patent) in progress:
        next_certificate = patent["certificate_id"]
        if i == next_certificate:
            progress.set_description(f"Correct id={i}")
            continue
        elif i < next_certificate:
            progress.set_description(f"Missing id={i}")
            missing = get_patent_by_id(id=i, language=languge)
            downloaded_patents.insert(i - 1, missing)
            i += 1
            continue
        while i > downloaded_patents[i-1]["certificate_id"]:
            progress.set_description(f"Dublicate id={i}")
            downloaded_patents.pop(i - 1)
    
    # try to download past the upper boundary
    new_id = downloaded_patents[-1]["certificate_id"] + 1
    while attempt := get_patent_by_id(id=new_id, language=languge):
        downloaded_patents.append(attempt)
        new_id += 1
    
    print("Confirming every id is downloaded and unique... ", end="")
    progress.reset()
    for (i, patent) in progress:
        next_certificate = patent["certificate_id"]
        if i != next_certificate:
            raise ValueError(f"Error at id={i}")
    print("Done!")

    return downloaded_patents

def get_ICID_json(language : str):
    print("Downloading every entry with ICID for", language, "language")
    content = {
        "parsing_date": datetime.date.today().isoformat(),
        "entries": 0,
        "icid_code_groups": []
    }
    progress = tqdm(generate_icid_codes(), total=icid_codes_amount)
    for icid_code in progress:
        progress.set_description(icid_code)
        group = get_group_by_icid_code(icid_code=icid_code, language=language)
        if group['data']:
            content["entries"] += len(group["data"])
            content['icid_code_groups'].append(group)
    
    Path("./data/" + language).mkdir(parents=True, exist_ok=True)
    with open("./data/" + language + "/ICID.json", "w", encoding='utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False, indent=4))

def get_all_patents(language : str):
    path = "./data/" + language + "/"
    try:
        with open(path + "ICID.json", "r", encoding='utf-8') as f:
            content = json.load(f)
    except FileNotFoundError:
        print(f"Missing {path + "ICID.json"}\nDo you want to get it? [y/n]")
        if input(">>>").strip().lower() == "y":
            get_ICID_json(language)
        else:
            return

        with open(path + "ICID.json", "r", encoding='utf-8') as f:
            content = json.load(f)
             
    ready_patents = []
    for group in content["icid_code_groups"]:
        for patent in group["data"]:
            ready_patents.append(patent)
    
    print("ICID.json parsed, fixing patents for", language, "language")
    all_patents = fix_patents_list(ready_patents, languge=language)
    print(f"Every patent up to {content["parsing_date"]} is succesfully downloaded in {path}patents.json")
    print(f"In total: {all_patents[-1]["certificate_id"]} unique patents")

    with open(path + "patents.json", "w", encoding='utf-8') as f:
        f.write(json.dumps(all_patents, ensure_ascii=False, indent=4))

def get_all_info_for_patent(patent : dict):
    soup = BeautifulSoup(
        requests.request(
            method="get",
            url=patent["patent_link"]
        ).text, 
        features="html.parser"
    )
    captions_map = {
        "(11)": "id",
        "(13)": "document_view_code",
        "(21)": "application_id",
        "(22)": "application_date",
        "(31)": "first_application_info",
        "(51)": "ICID_codes",
        "(54)": "title",
        "(71)": "applicant",
        "(72)": "authors",
        "(73)": "patent_owner",
        "(55)": "images"
    }

    info = {}
    for p in soup.find_all("p"):
        if p.has_attr("class") and "captions" in p["class"]:
            if p.get_text()[:4] not in captions_map:
                assert "expired" not in info, f"Key 'expired' already exists! id={info["id"]}"
                key = "expired"
            else:
                key = captions_map[p.get_text()[:4]]
        elif p.has_attr("class") and "data" in p["class"]:
            if key == 'authors':
                info[key] = list(map(lambda name: name + ')', p.get_text().split(")")[:-1]))
            elif key == 'ICID_codes':
                info[key] = list(map(lambda code: code.strip(), p.get_text().split(",")))   
            elif key == "id" or key == "application_id":
                info[key] = int(p.get_text())
            else:
                info[key] = p.get_text()
        elif p.has_attr("style"):
            if "images" not in info:
                info["images"] = list()
            info["images"].append("https://old.aipa.am" + p.img["src"])

    return info

def get_all_info(language : str):
    path = "./data/" + language + "/"
    try:
        with open(path + "patents.json", "r", encoding='utf-8') as f:
            content = json.load(f)
    except FileNotFoundError:
        print(f"Missing {path + "patents.json"}\nDo you want to get it? [y/n]")
        assert input(">>>").strip().lower() == "y", "Get option 1 and 2 done first"
        get_all_patents(language=language)

        with open(path + "patents.json", "r", encoding='utf-8') as f:
            content = json.load(f)
    
    print("Extracting detailed info for every patent,", language, "language")
    all_info = list()
    try:
        progress = tqdm(content)
        for patent in progress:
            progress.set_description(f"parsing id={patent["certificate_id"]:3d}")
            info = get_all_info_for_patent(patent)
            all_info.append(info)
    finally:
        with open(path + "all_info.json", "w", encoding='utf-8') as f:
            f.write(json.dumps(all_info, ensure_ascii=False, indent=4))
