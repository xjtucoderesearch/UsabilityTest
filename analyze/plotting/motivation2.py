import csv

from pre import name_for, tools
import matplotlib.pyplot as plt
import numpy as np

langs = ['cpp', 'java', 'python']
algorithms = {
    'limbo': ['#006CD9', 'LIMBO', '#004C99', '#EEEEEE'],
    'wca': ['#B8B8B8', 'WCA', '#444444', '#666666'],
}
ticks = ['DE', 'DS', 'DU', 'ES', 'EU', 'SU']

collection = {}

for lang in langs:
    print(f'Loading {lang} data')
    mTools = tools if lang != 'ts' else {'enre': tools['enre'], 'understand': tools['understand']}
    for algorithm in algorithms:
        try:
            # Using 'sig' to suppress the BOM generated by Excel
            with open(f'D:/ASE2022/MacroConsistency-After-V1/mojo_result_{algorithm}_{lang}.csv', 'r', encoding='utf-8-sig') as file:
                data = csv.reader(file)
                curr = [[],[],[],[],[],[]]

                index = -1
                for row in data:
                    index += 1
                    if index != 0:
                        for i in range(1,7):
                            value = float(row[i])
                            # Investigate on why some cells in new data can be greater than 100
                            if value <= 100:
                                curr[i - 1].append(value)
                collection[f'{lang}-{algorithm}'] = curr
        except EnvironmentError:
            print(f'No mojo_result_{algorithm}_{lang}.csv file found, skipping to the next')
            continue


plt.style.use('./my.mplstyle')


def set_box_color(bp, color, mediancolor):
    plt.setp(bp['boxes'], color=color)
    plt.setp(bp['whiskers'], color=color)
    plt.setp(bp['caps'], color=color)
    plt.setp(bp['medians'], color=mediancolor, linewidth=1.6)


data = {}
for lang in langs:
    for i in [3, 5, 1, 4, 0, 2]:
        for algorithm in algorithms:
            if f'{lang}-{algorithm}' not in data:
                data[f'{lang}-{algorithm}'] = []
            column = collection[f'{lang}-{algorithm}'][i]
            # Remove -1 values
            pure = list(filter(lambda x: x >= 0, column))
            data[f'{lang}-{algorithm}'].append(pure)

fig, axs = plt.subplots(1, 3, figsize=(17, 4))

for ax in axs.flat:
    ax.label_outer()

medians = {}
total = len(langs) * len(algorithms)
legends = []
this_all = []
this_lang = {'cpp': [], 'java': [], 'python': []}
for ia, algorithm in enumerate(algorithms):
    plt.plot([], c=algorithms[algorithm][0], label=algorithms[algorithm][1])
    for il, lang in enumerate(langs):
        label = f'{lang}-{algorithm}'
        # Print avg value for (lang, algorithm) pair regardless of analyzers
        this_label = []
        for i in range(6):
            this_all += data[label][i]
            this_lang[lang] += data[label][i]
            this_label += data[label][i]
        print(label, 'avg', np.average(this_label))
        print(label, 'median', np.median(this_label))
        boxplot = axs[il].boxplot(
            data[label],
            widths=0.2,
            positions=np.array(range(len(data[label]))) * 1 - 0.18 * (-1) ** ia,
            patch_artist=True,
            flierprops={
                'marker': 'o',
                'markersize': 4,
                'markerfacecolor': 'none',
                'markeredgecolor': algorithms[algorithm][0]}
        )
        if il == 0:
            legends.append(boxplot['boxes'][0])
        # Print medians
        medians[label] = list(map(lambda p: p.get_ydata()[0], boxplot['medians']))

        for it in range(6):
            median = medians[label][it]
            axs[il].text(
                it - 0.41 * (-1) ** ia,
                median + 1.26,
                int(median),
                size=12,
                weight='bold',
                ha='center',
                va='top',
                color=algorithms[algorithm][2]
            )

        set_box_color(boxplot, algorithms[algorithm][0], algorithms[algorithm][3])

        axs[il].set_xticks(range(0, len(ticks)), ticks)

for lang in langs:
    print(lang, 'avg', np.average(this_lang[lang]))
    print(lang, 'median', np.median(this_lang[lang]))
print('all', 'avg', np.average(this_all))
print('all', 'median', np.median(this_all))
print(medians)

plt.legend(legends, ['LIMBO', 'WCA'], loc='lower right', prop={'size': 12})

fig.tight_layout()

plt.subplots_adjust(left=0.025, right=0.999, top=0.999, bottom=0.08)

# Set mode here
mode = 'view'

if mode == 'view':
    fig.show()
elif mode == 'save':
    fig.savefig(f'G:\\My Drive\\ASE 2022\\motivation.png')
