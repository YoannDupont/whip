"""description:
  Lasso is the process of fetching some information about some entity. You may
  or may not know what you are looking for (= you have the QID already or not).
  This package allows to catch the (potentially) right entry in Wikidata.
"""

import requests
import pywikibot
from pywikibot.data import api
from wikidataintegrator import wdi_core


__wikipedia_url = "https://{lang}.wikipedia.org/wiki/{pagename}"
__wikidata_site = pywikibot.Site("wikidata", "wikidata")


def query_wikidata(name, lang, limit=1):
    """Query Wikidata to fetch information about a term."""

    params = {
        'action': 'wbsearchentities',
        'format': 'json',
        'language': lang,
        'type' : 'item',
        'search': name,
        "limit": limit
    }
    request = api.Request(site=__wikidata_site, parameters=params)
    return request.submit()


def query_wikipedia(name, lang):
    url = __wikipedia_url.format(lang=lang, pagename=name)
    openURL = requests.get(url)
    if openURL.status_code != 200:
        return []

    # img and input tags may cause lxml to raise an exception. Since they do not
    # provide any meaningful information for our purpose, we discard them.
    # CHECKME: if they get used anywhere else, compile them (unlikely).
    # TODO: replace with HTML parser?
    data = openURL.text
    data = re.sub(r'<img\s.+?>', '', data, flags=re.M + re.DOTALL)
    data = re.sub(r'<input\s.+?>', '', data, flags=re.M + re.DOTALL)
    try:
        root = etree.fromstring(data)
    except etree.XMLSyntaxError as exc:
        return []

    a_list = root.iter("a")
    for a_elt in a_list:
        children = list(a_elt)
        for child in children:
            if child.tag == 'span':
                text = etree.tostring(child, method="text", encoding="unicode").strip().lower()
                if "wikidata" in text:
                    found = True
                    wdurl = a_elt.attrib["href"]
                    qid = wdurl.rsplit('/', 1)[-1]
                    return [qid]
    return []


def from_qid(qid, kb=None):
    """Return the Wikidata entry given the Wikidata identifier (QID) given in argument.
    This assumes you know which QID you are looking for. You can give a knowledge base
    if you have some claims loaded, otherwise, the code will request Wikidata.
    """

    if kb is None:
        item = wdi_core.WDItemEngine(wd_item_id=qid).get_wd_json_representation()
    else:
        item = kb[qid]

    return item


def from_name(name, langs, maximum_candidates=5):
    """Return Wikidata entries for a given name in given langs. The process
    stops at the first language where some Wikidata ID (QID) is found. If no
    items are found while querying Wikidata, the method will try to query
    Wikipedia to find a page and get its Wikidata ID.
    """

    qids = []
    for lang in langs:
        caught = query_wikidata(name, lang, limit=maximum_candidates)

        success = caught["success"]
        if not success:
            raise RuntimeError(f"Requesting {name} for {lang} failed.")

        search = caught["search"]
        if search:
            for item in search:
                qids.append(item["id"])
            break

    if qids:
        return qids

    print("nothing found via Wikidata api, looking through Wikipedia")
    for lang in langs:
        qids = query_wikipedia(name, lang)
        if qids:
            break

    return qids
