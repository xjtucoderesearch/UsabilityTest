import csv
from math import trunc

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
    plt.setp(bp['medians'], color=mediancolor, linewidth=1.8)


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

fig = plt.figure(figsize=(8.5, 3.5))
ax = fig.gca()

medians = {}
total = len(langs) * len(algorithms)
for ia, algorithm in enumerate(algorithms):
    plt.plot([], c=algorithms[algorithm][0], label=algorithms[algorithm][1])
    for il, lang in enumerate(langs):
        label = f'{lang}-{algorithm}'
        # Print avg value for (lang, algorithm) pair regardless of analyzers
        print(label, sum(data[label][0])/len(data[label][0]))
        boxplot = ax.boxplot(
            data[label],
            widths=0.22,
            positions=np.array(range(len(data[label]))) * 1 + il * 8 - 0.18 * (-1) ** ia,
            patch_artist=True,
            flierprops={
                'marker': 'o',
                'markersize': 4,
                'markerfacecolor': 'none',
                'markeredgecolor': algorithms[algorithm][0]}
        )
        medians[label] = list(map(lambda p: p.get_ydata()[0], boxplot['medians']))
        set_box_color(boxplot, algorithms[algorithm][0], algorithms[algorithm][3])

print(medians)

for ia, algorithm in enumerate(algorithms):
    for il, lang in enumerate(langs):
        label = f'{lang}-{algorithm}'
        x = 2.5 + 8 * il + 3.3 * (-1) ** (ia + 1)
        ymin = min(medians[label])
        ymax = max(medians[label])
        ax.plot(
            (x, x),
            (ymin, ymax),
            linewidth=1.5,
            linestyle=(0, (1, 0.5)),
            color=algorithms[algorithm][2],
            marker='_',
        )
        ax.text(
            x,
            ymin - 4,
            f'{trunc(ymax - ymin)}%',
            size=10,
            weight='bold',
            ha='center',
            va='top',
            color=algorithms[algorithm][2]
        )

ax.set_xlim([-1.5, 22.5])

plt.xticks(range(0, len(ticks) * 3 + 4), ticks + [''] * 2 + ticks + [''] * 2 + ticks)

plt.legend(loc='lower right', prop={'size': 10})

ax2 = ax.twiny()
ax2.set_xlim(ax.get_xlim())
ax2.set_xticks([2.5, 10.5, 18.5])
ax2.set_xticklabels(map(lambda l: name_for[l], langs), weight='bold')
ax2.tick_params(length=0)

fig.tight_layout()

plt.subplots_adjust(left=0.049, right=0.999, top=0.92, bottom=0.087)

# Set mode here
mode = 'view'

if mode == 'view':
    fig.show()
elif mode == 'save':
    fig.savefig(f'G:\\My Drive\\ASE 2022\\motivation.png')