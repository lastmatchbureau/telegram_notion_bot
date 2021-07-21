def fix_links(txt: str) -> str:
    url_start = 1
    url_end = 1
    while url_start != -1 or url_end != -1:
        url_start = txt.find("[")
        url_end = txt.find("]")
        url = txt[url_start + 1: url_end:]
        txt = txt.replace(f"[{url}]({url})", url)
        txt = txt.replace(f"[{url}+w]({url}+w)", url)
        print(url, f"[{url}]({url})")
    return txt
