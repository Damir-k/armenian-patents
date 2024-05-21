import requests
from bs4 import BeautifulSoup
import itertools
import json
import datetime
from tqdm import tqdm


def get_table_by_fmad(fmad='01-01', lang='en'):
    if lang not in ['en', 'ru', 'hy']:
        raise Exception("Tried to request a table in non-supported language. Use 'en', 'ru' or 'hy'.")

    response = requests.request(
        'post',
        'https://aipo.am/' + lang + '//ajax/search_mods_search_int_classification',
        data={
            'logic': 'partial',
            'FMAD': fmad,

            'Reg_num':'',
            'App_num':'',
            'App_date':'',
            'name':'',
            'AppPers':'',
            'Auth':'',
            'Owner':''
        }
    )
    return response

def get_overview_by_fmad(fmad='01-01', lang='en'):
    response = get_table_by_fmad(fmad, lang)
    soup = BeautifulSoup(response.text, features="html.parser")
    
    overview = {
        "FMAD": fmad,
        "data": []
    }
    for (application_id, title, certificate_id) in itertools.batched(soup.find_all("td"), n=3):
        overview['data'].append({
            "certificate_id": certificate_id.get_text(),
            "application_id": application_id.get_text(),
            "title": title.get_text(),
            "patent_link": 'https://old.aipa.am/search_mods/industrial_design/view_item.php?id=' + certificate_id.get_text() + '&language=en'
        })
    return overview

def generate_fmads():
    fmads = []
    for i in range(33): # 32 - amount of classes in fmad (mkpo, icid)
        for j in range(17): # 16 - maximum second index in every class
            fmads.append(str(i).zfill(2) + '-' + str(j).zfill(2))
    return fmads

def get_patent_by_id(id, lang="en"):
    response = requests.request(
        'post',
        'https://aipo.am/' + lang + '//ajax/search_mods_search_int_classification',
        data={
            'logic': 'partial',
            'Reg_num': str(id),

            'FMAD': '',
            'App_num':'',
            'App_date':'',
            'name':'',
            'AppPers':'',
            'Auth':'',
            'Owner':''
        }
    )
    soup = BeautifulSoup(response.text, features="html.parser")
    application_id, title, certificate_id = soup.find_all("td")
    return {
        "certificate_id": certificate_id.get_text(),
        "application_id": application_id.get_text(),
        "title": title.get_text(),
        "patent_link": 'https://old.aipa.am/search_mods/industrial_design/view_item.php?id=' + certificate_id.get_text() + '&language=en'
    }

def download_remaining(downloaded_patents):
    downloaded_patents.sort(key = lambda patent: int(patent["certificate_id"]))
    progress = tqdm(
            enumerate(downloaded_patents, start=1), 
            desc="Downloading remaining patents", 
            total=int(downloaded_patents[-1]["certificate_id"])
        )
    for (i, patent) in progress:
        next_certificate = int(patent["certificate_id"])
        if i == next_certificate:
            progress.set_description(f"Checking")
            continue
        elif i < next_certificate:
            progress.set_description(f"Missing id={i}")
            missing = get_patent_by_id(id=i)
            downloaded_patents.insert(i - 1, missing)
            i += 1
            continue
        while i > int(downloaded_patents[i-1]["certificate_id"]):
            progress.set_description(f"Dublicate id={i}")
            downloaded_patents.pop(i - 1)
    
    progress = tqdm(
            enumerate(downloaded_patents, start=1), 
            desc="Confirming every certificate id is present once", 
            total=int(downloaded_patents[-1]["certificate_id"])
        )
    for (i, patent) in progress:
        next_certificate = int(patent["certificate_id"])
        if i != next_certificate:
            raise ValueError(f"Error at id={i}")
    
    return downloaded_patents

def download_patents(all : bool):
    if all:
        certificate_ids = {
            "parsing_date": datetime.date.today().isoformat(),
            "entries": 0,
            "overviews": []
        }

        for fmad in tqdm(generate_fmads(), desc="Downloading every entry with FMAD"):
            overview = get_overview_by_fmad(fmad, 'en')
            if overview['data']:
                certificate_ids["entries"] += len(overview["data"])
                certificate_ids['overviews'].append(overview)
        
        with open("./data/en/data.json", "w", encoding='utf-8') as f:
            f.write(json.dumps(certificate_ids, ensure_ascii=False))
    else:
        with open("./data/en/data.json", "r", encoding='utf-8') as f:
            certificate_ids = json.load(f)
            
    almost_all_patents = []
    for overview in tqdm(certificate_ids["overviews"], desc="Extracting individual patents"):
        for patent in overview["data"]:
            almost_all_patents.append(patent)
    
    all_patents = download_remaining(almost_all_patents)
    print(f"Every patent up to {certificate_ids["parsing_date"]} is succesfully downloaded in ./data/en/patents.json")

    with open("./data/en/patents.json", "w", encoding='utf-8') as f:
        f.write(json.dumps(all_patents, ensure_ascii=False))

def main():
    print("What do you want to do?")
    print("1: Download all certificate ids with links to the patents")
    print("2: download only patents without FMAD (needs 1st option to be done)")
    match int(input()):
        case 1:
            download_patents(all=True)
        case 2:
            download_patents(all=False)
        case _:
            print("No such option")
    


if __name__ == "__main__":
    main()