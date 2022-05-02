import argparse
import csv
import numpy as np

name_for = {'cpp': 'C++',
            'java': 'Java',
            'python': 'Python'}


def init():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', help='Specify the deploy mode')
    parser.add_argument('lang',
                        help='Specify the target language')
    parser.add_argument('-s',
                        '--no-sourcetrail',
                        help='Do not plot SourceTrail\'s Data',
                        action=argparse.BooleanOptionalAction)
    parser.add_argument('-p',
                        '--prune-all',
                        help='Remove a result among all tools\' if it\'s going to be removed in one\'s',
                        action=argparse.BooleanOptionalAction)
    args = parser.parse_args()

    mode = args.mode
    try:
        ['view', 'save'].index(mode)
    except ValueError:
        raise ValueError(f'Invalid mode {mode}, only support view / save')

    langs = args.lang
    try:
        ['all', 'cpp', 'java', 'python'].index(langs)
    except ValueError:
        raise ValueError(f'Invalid lang {langs}, only support all / cpp / java / python')
    else:
        if langs == 'all':
            langs = ['cpp', 'java', 'python']
        else:
            langs = [langs]

    # Fixtures
    tools = {
        'depends': ['Depends', '#34D90B', '#d0ffcf'],  # Green
        'enre': ['ENRE', '#006CD9', '#e3edff'],  # Blue
        'sourcetrail': ['SourceTrail', '#DB941D', '#FFF2D6'],  # Yellow
        'understand': ['Understand', '#D916AE', '#FCDCEE'],  # Purple
    }
    # tools = {
    #     'depends': ['Depends', '#249908', '#d0ffcf'],  # Green
    #     'enre': ['ENRE', '#006CD9', '#e3edff'],  # Blue
    #     'sourcetrail': ['SourceTrail', '#9C6914', '#FFF2D6'],  # Yellow
    #     'understand': ['Understand', '#990F7B', '#FCDCEE'],  # Purple
    # }
    metrics = ['time', 'memory']

    collection = {}

    # Loading data
    for lang in langs:
        print(f'Loading {lang} data')
        curr = collection[lang] = {}
        try:
            # Using 'sig' to suppress the BOM generated by Excel
            with open(f'../data/{lang}.csv', 'r', encoding='utf-8-sig') as file:
                data = csv.reader(file)
                curr['loc'] = []
                for tool in tools:
                    for metric in metrics:
                        curr[f'{tool}-{metric}'] = []

                for row in data:
                    curr['loc'].append(int(row[0]))
                    c = 1
                    for tool in tools:
                        for metric in metrics:
                            # Convert MB to GB if it's memory data
                            curr[f'{tool}-{metric}'].append(float(row[c]) / (1 if c % 2 == 1 else 1024))
                            c += 1
        except EnvironmentError:
            print(f'No {lang}.csv file found, skipping to the next')
            continue
        # Convert to numpy array
        for key in curr:
            if key != 'loc':
                curr[key] = np.array(curr[key])
                # Convert 0, -1 or any error indicators to NaN
                curr[key][curr[key] <= 0] = np.nan
        # If an error indicator shows up as LoC, remove it and associated datas
        indices = []
        for index, value in enumerate(curr['loc']):
            if value <= 0:
                indices.append(index)
        for key in curr.keys():
            curr[key] = np.delete(curr[key], indices)

    if args.no_sourcetrail is True:
        del tools['sourcetrail']

    return collection, {
        'prune_all': args.prune_all
    }, mode, langs, tools, metrics
