import requests


def get_keywords(text):
    """
    :param text: plain text taken in to be analysed for keywords.
    :return: dictionary of { 'keyword' : count }
    """
    # Call NodeRED to access Watson
    url = 'https://resume-node-red.mybluemix.net/CV'
    response = requests.post(url, data=text.encode('ascii', errors='ignore')).json()

    # Select all proper nouns and capitalised nouns from text
    # Take into account strings of multiple proper nouns
    temp_keywords = []
    common_PROPN = 'JanuaryFebruaryMarchAprilMayJuneJulyAugustSeptemberOctoberNovemberDecemberABCDEFGCSEsReferences'
    prev = None
    for word in response['syntax']['tokens']:
        if word['part_of_speech'] == 'PROPN' or (
                word['part_of_speech'] == 'NOUN' and word['text'][0].isupper()):
            if prev and word['text'].lower() in common_PROPN.lower():
                temp_keywords.append(prev)
            elif word['text'].lower() in common_PROPN.lower():
                continue
            elif prev:
                prev += ' ' + word['text']
                temp_keywords.append(prev)
            else:
                temp_keywords.append(word['text'])
                prev = word['text']
        else:
            prev = None
    i = 0
    while i + 1 < len(temp_keywords):
        if temp_keywords[i] in temp_keywords[i + 1]:
            del temp_keywords[i]
        else:
            i += 1

    # Reformat list of proper nouns to be a dictionary of counts
    my_keywords = {}
    for kw in temp_keywords:
        if kw not in common_PROPN:
            my_keywords[kw] = temp_keywords.count(kw)

    # Add in IBMs keywords
    for kw in response['keywords']:
        my_keywords[kw['text']] = kw['count']

    return my_keywords
