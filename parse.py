import requests
from bs4 import BeautifulSoup
import itertools
import json

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




def main():
    response = get_table_by_fmad("01-01", lang="en")
    # with open("test.html", "w") as f:
    #     f.write(response.text)
    soup = BeautifulSoup(response.text, features="html.parser")
    
    overview = {
        "FMAD": '01-01',
        "data": []
    }
    for (application_id, title, certificate_id) in itertools.batched(soup.find_all("td"), n=3):
        overview['data'].append({
            "certificate_id": certificate_id.get_text(),
            "application_id": application_id.get_text(),
            "title": title.get_text(),
            "patent_link": 'https://old.aipa.am/search_mods/industrial_design/view_item.php?id=' + certificate_id.get_text() + '&language=en'
        })
    with open("./data/en/data.json", "w", encoding='utf-8') as f:
        f.write(json.dumps(overview, ensure_ascii=False))
        



if __name__ == "__main__":
    main()