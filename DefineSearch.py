import requests
import Auth
from pprint import pprint
import DefaultSettings
import DbConnectionHandler


# TO DO:
# mistake handling
# going inside dictionary function - simple and transparent!
# print for fetched data?


def category_search(session, params, search_url):
    data = {'categories': {'subcategories': [{'id': 'temp'}, {'id': 'temp2'}]}}
    while len(data['categories']['subcategories']) != 1:
        response = session.get(search_url, params=params)
        data = response.json()
        print(data)

        for categorie in data["categories"]["subcategories"]:
            pprint(categorie["name"] + ' ' + categorie["id"])

        temp_category = input()
        params["category.id"] = temp_category


def filter_search(session, params, search_url):
    # get data with previously established category id and phrase
    response = session.get(search_url, params=params)
    data = response.json()

    print(data['filters'])
    for filter_dict in data['filters']:
        print(filter_dict)
        print(filter_dict['type'])
        print(filter_dict['name'])

        if filter_dict['type'] == 'MULTI':
            multi_choice(filter_dict, params)

        if filter_dict['type'] == 'TEXT':
            text_choice(filter_dict, params)

        if filter_dict['type'] == 'NUMERIC':
            numeric_choice(filter_dict, params)

        if filter_dict['type'] == 'SINGLE':
            single_choice(filter_dict, params)

    print(params)


def multi_choice(filter_dict, params):

    temp_iter = 1
    temp_dict = []
    for value in filter_dict['values']:
        print(str(list(value.values())[1]) + ' ' + str(list(value.values())[0]) + ' ' + str(temp_iter))

        temp_iter += 1

    # input needs to expect user not to specify some filters, e.g. delivery methods
    choice = input()
    if choice == 'none':
        print('none')
    else:
        choice = choice.split(',')
        for index in choice:
            temp_dict.append(filter_dict['values'][int(index) - 1])
    prefix = str(filter_dict['id'])
    for value in temp_dict:
        params[prefix] = str(value['value'])


def single_choice(filter_dict, params):

    temp_iter = 1

    for value in filter_dict['values']:
        print(str(list(value.values())[1]) + ' ' + str(list(value.values())[0]) + ' ' + str(temp_iter))


        temp_iter += 1

    # input needs to expect user not to specify some filters, e.g. delivery methods
    choice = input()
    if choice == 'none':
        print('none')
    else:
        prefix = str(filter_dict['id'])
        temp = filter_dict['values'][int(choice) - 1]
        params[prefix] = temp['value']


def text_choice(filter_dict, params):
    prefix = str(filter_dict['id'])
    choice = input()
    if choice == 'none':
        print('none')
    else:
        params[prefix] = str(choice)


def numeric_choice(filter_dict, params):
    prefix = str(filter_dict['id'])
    for value in filter_dict['values']:
        print(value['name'])
        choice = input()
        if choice != 'none':
            params[prefix + value['idSuffix']] = choice


def finalize_search(params):
    print('podaj mail')
    email = input()
    print('podaj próg cenowy')
    price_treshold = input()
    params['price_threshold'] = price_treshold
    search_string = [params, email]
    return search_string


def search_start():
    # Main function, will determine set of products, that interest user
    # it will return params dictionary, which contains search phrase, leaf category id and set of filters
    # with params set we can query allegro multiple times every period of time, and get constant results
    # taking into account new items, added after defining search!
    access_token = Auth.get_access_token()
    DEFAULT_SEARCH_URL = Auth.DEFAULT_SEARCH_URL

    headers = {"charset": "utf-8", "Accept-Language": "pl-PL", "Content-Type": "application/json",
               "Accept": 'application/vnd.allegro.public.v1+json',
               "Authorization": "Bearer {}".format(access_token)}
    phrase = "xiaomi redmi note 8 pro"
    category = "300525"
    params = {"phrase": phrase, 'category.id': category}

    with requests.Session() as session:
        session.headers.update(headers)

        category_search(session, params, DEFAULT_SEARCH_URL)

        # when displaying filters add count parameter
        # important to distinct filter type e.g. multi or text!
        # filter and category selection will be different in final product, dont bother

        filter_search(session, params, DEFAULT_SEARCH_URL)

        search_params_list = finalize_search(params)
        print(search_params_list)

        DbConnectionHandler.update_search_table(search_params_list)

    return params


