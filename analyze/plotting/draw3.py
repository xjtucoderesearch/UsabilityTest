from colour import Color
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from shapely.geometry import LineString, Point

from pre import init

collection, tags, mode, langs, tools, metrics = init()

plt.style.use('./my.mplstyle')


def draw(lang, original_data):
    fig, ax = plt.subplots(num=f'{lang}', figsize=(6.4, 4.8))
    plt.xlabel('Completion Time (s)')
    plt.ylabel('Peak Memory Usage (GB)')

    if lang == 'cpp':
        ax.set_xlim([0, 1300])
        ax.set_ylim([0, 10.5])
    elif lang == 'java':
        ax.set_xlim([0, 1300])
        ax.set_ylim([0, 10.5])
    elif lang == 'python':
        ax.set_xlim([0, 1825])
        ax.set_ylim([0, 3.2])
    elif lang == 'ts':
        ax.set_xlim([0, 420])
        ax.set_ylim([0, 6.5])

    # Universal pruning, remove the project's data for all
    # if one tool's is bad
    data = {}
    indices = set([])
    for key in original_data:
        if lang == 'ts' and key.startswith('depends'):
            continue
        for index, value in enumerate(original_data[key]):
            # Not for SourceTrail, its data is originally unfulfilled,
            # this will be handled later in a sandbox
            if not key.startswith('sourcetrail') and np.isnan(value):
                indices.add(index)
    for key in original_data:
        if lang == 'ts' and key.startswith('depends'):
            continue
        data[key] = np.delete(original_data[key], list(indices))

    def draw_tool(loc, time, memory, color, marker):
        def size_mapping():
            maximum = max(loc)
            # Map loc to point size between (2~10)^2
            return list(map(lambda i: i / maximum * 96 + 4, loc))

        s = size_mapping()
        legend = plt.scatter(
            time,
            memory,
            marker=marker,
            s=s,
            linewidths=0.5,
            color='none',
            edgecolors=color,
            alpha=1,
        )
        return legend

    def draw_trend(tool, _loc, _time, _memory, color, bgcolor, marker, linestyle):
        if lang != 'python':
            milestone = 1 * 10 ** 6
            milestone_str = '1MLoC'
        else:
            milestone = 1 * 10 ** 6
            milestone_str = '1MLoC'

        # Manually remove obvious abnormal point
        indices = []
        if lang == 'java' and tool == 'sourcetrail':
            # This does not affect the result too many
            # indices.append(2)
            # indices.append(25)
            pass
        elif lang == 'cpp' and tool == 'depends':
            indices.append(14)
            indices.append(55)
        if len(indices) != 0:
            loc = np.delete(_loc, indices)
            time = np.delete(_time, indices)
            memory = np.delete(_memory, indices)
        else:
            loc = _loc
            time = _time
            memory = _memory

        popt, _ = curve_fit(lambda x, a, b, c: a * x ** b + c,
                            time,
                            memory,
                            # A lower number will cause interation fails on python-st
                            maxfev=2400)

        def trend(x):
            return popt[0] * x ** popt[1] + popt[2]

        # Helper functions
        def trend_inverse(y):
            return ((y - popt[2]) / popt[0]) ** -popt[1]

        def d_trend(x):
            return popt[0] * popt[1] * x ** (popt[1] - 1)

        def sampling():
            pairs = []
            for x in range(0, 3000, 1):
                pairs.append((x, trend(x)))
            pline = LineString(pairs)
            projection = []
            for index, value in enumerate(time):
                opoint = Point(value, memory[index])
                projection.append(pline.project(opoint))

            # Calculate the LoC~CurveLength function
            params, _ = curve_fit(lambda x, a, b: a * x + b, loc, projection)

            def loc2len(x):
                return params[0] * x + params[1]

            # If maximum LoC is less than 1M / 200K, then extend the right-most
            # coords to that milestones
            suggested_eol = pline.interpolate(max(max(projection), loc2len(milestone)))

            return suggested_eol, lambda loc: pline.interpolate(loc2len(loc)).x

        eol, loc2x = sampling()
        valid_x = max(0, trend_inverse(0))
        if lang == 'python' and tool == 'sourcetrail':
            valid_x = 25
        x = np.linspace(valid_x, eol.x, 100)
        y = trend(x)
        # vwidth = 4 + x[:-1] / max(x) * 16
        # points = np.array([x, y]).T.reshape(-1, 1, 2)
        # segments = np.concatenate([points[:-1], points[1:]], axis=1)
        # lc = LineCollection(segments,
        #                     linewidths=vwidth,
        #                     color=bgcolor,
        #                     path_effects=[path_effects.Stroke(capstyle="round")])
        # ax.add_collection(lc)\

        # White background cover
        ax.plot(x,
                y,
                color='w',
                linewidth=8,
                alpha=0.8,
                zorder=24)
        ax.plot(x,
                y,
                color='w',
                linewidth=12,
                alpha=0.6,
                zorder=25)
        # Colored lines
        trendline, = ax.plot(x,
                             y,
                             color=color,
                             linestyle=linestyle,
                             linewidth=2,
                             zorder=50)

        # Draw milestone
        mx = loc2x(milestone)
        my = trend(mx)
        plt.plot(mx,
                 my,
                 'o',
                 ms=9,
                 mew=2,
                 c='w',
                 markeredgecolor=color,
                 zorder=99)
        print(f'{lang}-{tool}-1mloc: {mx}, {my}')

        # Calculate R2
        residuals = memory - trend(time)
        ss_res = np.sum(residuals ** 2)
        ss_tot = np.sum((memory - np.mean(memory)) ** 2)
        r_squared = 1 - (ss_res / ss_tot)
        print(f'{lang}-{tool}-r2: {r_squared}')

        return trendline

    legends = []
    mTools = tools if lang != 'ts' else {'enre': tools['enre'], 'understand': tools['understand']}
    for tool in mTools:
        fixture = tools[tool]
        loc = data['loc']
        time = data[f'{tool}-{metrics[0]}']
        memory = data[f'{tool}-{metrics[1]}']
        # Remove any nan for SourceTrail and re-assign variable
        # This won't pollute the original data,
        # thus performs the functionality of a sandbox
        if tool.startswith('sourcetrail'):
            indices = set([])
            for metric in metrics:
                for i, v in enumerate(data[f'{tool}-{metric}']):
                    if np.isnan(v):
                        indices.add(i)
            indices = list(indices)
            loc = np.delete(loc, indices)
            time = np.delete(time, indices)
            memory = np.delete(memory, indices)

        l = draw_tool(loc,
                      time,
                      memory,
                      Color(fixture[1]).rgb,
                      fixture[3])

        t = draw_trend(tool,
                       loc,
                       time,
                       memory,
                       Color(fixture[1]).rgb,
                       Color(fixture[2]).rgb,
                       fixture[3],
                       fixture[4])
        legends.append((l, t))

    legends.append(plt.Line2D(
        (0, 0),
        (1, 1),
        marker='o',
        ms=9,
        mew=2,
        c='w',
        markeredgecolor='#888888',
    ))

    legend_pos = {
        'cpp': 'upper left',
        'java': 'upper right',
        'python': 'lower right',
        'ts': 'upper right',
    }

    ax.legend(handles=legends,
              labels=list(map(lambda t: mTools[t][0], mTools)) + ['1MLoC'],
              prop={'size': 14},
              loc=legend_pos[lang])

    fig.tight_layout()

    if mode == 'view':
        ax.title.set_text(f'performance-{lang}')
        fig.show()
    else:
        if lang == 'python':
            plt.subplots_adjust(left=0.105, right=0.999, top=0.999, bottom=0.125)
        elif lang == 'ts':
            plt.subplots_adjust(left=0.079, right=0.999, top=0.999, bottom=0.125)
        else:
            plt.subplots_adjust(left=0.096, right=0.999, top=0.999, bottom=0.125)
        fig.savefig(f'G:\\My Drive\\ASE 2022\\performance-{lang}.png')


for lang in langs:
    draw(lang, collection[lang])
