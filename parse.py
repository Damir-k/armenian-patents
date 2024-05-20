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

def main():
    certificate_ids = {
        "parsing_date": datetime.date.today().isoformat(),
        "entries": 0,
        "overviews": []
    }
    for fmad in tqdm(generate_fmads()):
        overview = get_overview_by_fmad(fmad, 'en')
        if overview['data']:
            certificate_ids["entries"] += len(overview["data"])
            certificate_ids['overviews'].append(overview)

    with open("./data/en/data.json", "w", encoding='utf-8') as f:
        f.write(json.dumps(certificate_ids, ensure_ascii=False))
        



if __name__ == "__main__":
    main()