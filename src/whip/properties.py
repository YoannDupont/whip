"""Get properties of a Wikidata item."""

import hashlib


__datatype2url = {
    "commonsMedia": "https://upload.wikimedia.org/wikipedia/commons"
}


def naive_get(item, property_, additional_key=None):
    """propety_ as per PEP8 recommendation."""
    base = item["claims"][property_][0]["mainsnak"]["datavalue"]["value"]

    # some properties have an "additional key" for some values (id, text, etc.)
    if additional_key:
        return base[additional_key]
    else:
        return base


def label(item, lang):
    return item["labels"][lang]["value"]


preferred_name = label


def name_in_native_language(item):
    return item["claims"]["P1559"][0]["mainsnak"]["datavalue"]["value"]["text"]


native_name = name_in_native_language


def label_dict(item, langs=None):
    by_lang = item.get("labels", {})
    available = set(by_lang.keys())
    langs_actual = set(langs or available) & available

    return {lang: by_lang[lang]["value"] for lang in langs_actual}


def label_set(item, langs=None):
    names = set()
    by_lang = item.get("labels", {})
    available = set(by_lang.keys())
    langs_actual = set(langs or available) & available
    for lang in langs_actual:
        names.add(by_lang[lang]["value"])
    return names


labels = label_set


def alias_set(item, langs=None):
    alias_set_ = set()
    aliases_by_lang = item.get("aliases", {})
    available = set(aliases_by_lang.keys())
    langs_actual = set(langs or available) & available
    for lang in langs_actual:
        alias_set_.update(name["value"] for name in aliases_by_lang[lang])
    return alias_set_


aliases = alias_set


def all_names(item, langs=None):
    return labels(item, langs=langs) | aliases(item, langs=langs)


def description(item, lang):
    return item["descriptions"][lang]["value"]


def image(item):
    snak = item["claims"]["P18"][0]["mainsnak"]
    datatype = snak["datatype"]
    filename = snak["datavalue"]["value"]
    name = filename.replace(" ", "_")
    md5 = hashlib.md5(name.encode("utf-8")).hexdigest()
    datatypeurl = __datatype2url[datatype]
    p1 = md5[:1]
    p2 = md5[:2]
    url = f"{datatypeurl}/{p1}/{p2}/{name}"

    return url


def coordinates(item):
    snak = item["claims"]["P625"][0]["mainsnak"]
    return snak["datavalue"]["value"]


def instance_of(item):
    return set(item["mainsnak"]["datavalue"]["value"]["id"] for item in item["claims"].get("P31", []))


is_a = instance_of


def is_earth_location(item):
    # P625 = coordinate location
    P625 = item["claims"].get("P625")
    return P625 and P625[0]["mainsnak"]["datavalue"]["value"]["globe"] == 'http://www.wikidata.org/entity/Q2'


def is_org(item):
    # P159 = headquarters location
    return "P159" in item["claims"]
    # TODO: finish below to replace above
    instanciates = is_a(item)


def is_human(item, also_fictional=True):
    # Q5 = human ; Q15632617 = fictional human
    ids = set(["Q5"])
    if also_fictional:
        ids.add("Q15632617")
    return len(ids & is_a(item)) != 0


def is_date_abs(item):
    # Q47150325 = calendar day of a given year
    return "Q47150325" in is_a(item)


def date_of_birth(item):
    return item["claims"]["P569"][0]["mainsnak"]["datavalue"]["value"]


def date_of_death(item):
    return item["claims"]["P570"][0]["mainsnak"]["datavalue"]["value"]


def sex_or_gender(item):
    return item["claims"]["P21"][0]["mainsnak"]["datavalue"]["value"]["id"]
