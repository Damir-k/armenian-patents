import itertools
import json
import datetime
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


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
    with open("./data/ICID codes.json") as f:
        classes = json.load(f)["classes"]
    
    for icid_class in classes:
        for subclass in classes[icid_class]:
            yield icid_class + '-' + subclass

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
    
    print("Confirming every id is downloaded and unique... ", end="")
    for (i, patent) in progress:
        next_certificate = patent["certificate_id"]
        if i != next_certificate:
            raise ValueError(f"Error at id={i}")
    print("Done!")

    return downloaded_patents

def get_ICID_json(language : str):
    print("Downloading every entry with ICID")
    content = {
        "parsing_date": datetime.date.today().isoformat(),
        "entries": 0,
        "icid_code_groups": []
    }
    progress = tqdm(generate_icid_codes(), total=251)
    for icid_code in progress:
        progress.set_description(icid_code)
        group = get_group_by_icid_code(icid_code=icid_code, language=language)
        if group['data']:
            content["entries"] += len(group["data"])
            content['icid_code_groups'].append(group)
    
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
    
    all_patents = fix_patents_list(ready_patents, languge=language)
    print(f"Every patent up to {content["parsing_date"]} is succesfully downloaded in {path}patents.json")
    print(f"In total: {all_patents[-1]["certificate_id"]} unique patents")

    with open(path + "patents.json", "w", encoding='utf-8') as f:
        f.write(json.dumps(all_patents, ensure_ascii=False, indent=4))

def main():
    print("Select language (default = en) [ en | ru | hy | all ]")
    language = input(">>>").strip().lower() or "en"
    if language not in ["en", "ru", "hy", "all"]:
        raise ValueError(f"'{language}' is not a supported language")
    
    query = ["en", "ru", "hy"] if language == "all" else [language]
    
    print("What do you want to do?")
    print("1: Get only ICID.json (patents with ICID id)")
    print("2: Get all patents in patents.json (will require step one done)")
    match int(input(">>>")):
        case 1:
            for language in query:
                get_ICID_json(language)
        case 2:
            for language in query:
                get_all_patents(language)
        case _:
            print("No such option")

if __name__ == "__main__":
    main()