from whip.lasso import from_name, from_qid

from whip.properties import instance_of, naive_get, label

def get_author(bookname, lang="en", N_candidates=5):
    """Basic function to get author name from a book name."""

    qids = from_name(bookname, langs=[lang], maximum_candidates=N_candidates)
    entries = [from_qid(qid) for qid in qids]
    books = [entry for entry in entries if "Q7725634" in instance_of(entry)]
    book_names = [label(book, lang) for book in books]

    author_qids = [
        naive_get(book, "P50", extra_key="id") # some properties have an "extra" level.
        for book in books
    ]
    author_entries = [
        from_qid(author_qid)
        for author_qid in author_qids
    ]
    author_names = [
        label(author_entry, lang)
        for author_entry in author_entries
    ]

    return list(zip(book_names, author_names))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser("Get author from book name in given language.")
    parser.add_argument(
        "bookname", help="The name of the book. Use quoting/escaping if the name has spaces."
    )
    parser.add_argument("lang", help="The language for querying wikidata.")
    parser.add_argument("-N", "--N-candidates", type=int, default=5, help="The number of candidates to evaluate.")
    parser.add_argument("-d", "--delimiter", default="\t", help="The delimiter to use.")

    args = parser.parse_args()

    names = get_author(args.bookname, args.lang, args.N_candidates)
    delim = args.delimiter

    for book, author in names:
        print(book, author, sep=delim)
