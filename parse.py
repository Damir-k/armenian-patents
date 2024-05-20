import requests
from bs4 import BeautifulSoup
import itertools
import json

def main():
    response = requests.request(
        'post',
        'https://aipo.am/en//ajax/search_mods_search_int_classification',
        data={
            'logic': 'partial',
            'FMAD': '01-01',

            'Reg_num':'',
            'App_num':'',
            'App_date':'',
            'name':'',
            'AppPers':'',
            'Auth':'',
            'Owner':''
        }
    )
    with open("test.html", "w") as f:
        f.write(response.text)
    
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
    with open("./data/en/data.json", "w") as f:
        f.write(json.dumps(overview))
        



if __name__ == "__main__":
    main()