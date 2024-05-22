from aipoparser import get_ICID_json, get_all_patents, get_all_info


def main():
    print("Select language (default = en) [ en | ru | hy | all ]")
    language = input(">>>").strip().lower() or "en"
    if language not in ["en", "ru", "hy", "all"]:
        raise ValueError(f"'{language}' is not a supported language")
    
    query = ["en", "ru", "hy"] if language == "all" else [language]
    
    print("What do you want to do?")
    print("1: Get only ICID.json (patents with ICID id)")
    print("2: Get all patents in patents.json (will require step one done)")
    print("3: Go through each patent and extract all information available")
    match int(input(">>>")):
        case 1:
            for language in query:
                get_ICID_json(language)
        case 2:
            for language in query:
                get_all_patents(language)
        case 3:
            for language in query:
                get_all_info(language)
        case _:
            print("No such option")

if __name__ == "__main__":
    main()