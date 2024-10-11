# TODO: implement a typeahead search component; it has to call an endpoint on the backend that provides autocompletions

old_queries = ["google pixel", "iphone 12", "macbook pro", "python", "java"]


def autocomplete(query, queries_db=old_queries):
    return [q for q in queries_db if query.lower().strip() in q.lower().strip()]


if __name__ == "__main__":
    print(autocomplete(" p "))
