import requests

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



if __name__ == "__main__":
    main()