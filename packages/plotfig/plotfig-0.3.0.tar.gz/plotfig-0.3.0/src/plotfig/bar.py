from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
from matplotlib.axes import Axes
from matplotlib.ticker import FuncFormatter, ScalarFormatter
from scipy import stats

# 类型别名
Num = int | float  # 可同时接受int和float的类型
NumArray = list[Num] | npt.NDArray[np.float64]  # 数字数组类型

__all__ = [
    "plot_one_group_bar_figure",
    "plot_one_group_violin_figure",
    "plot_multi_group_bar_figure",
]


def compute_summary(data: NumArray) -> tuple[float, float, float]:
    """计算均值、标准差、标准误"""
    mean = np.mean(data)
    sd = np.std(data, ddof=1)
    se = sd / np.sqrt(len(data))
    return mean, sd, se


def add_scatter(
    ax: Axes,
    x_pos: Num,
    data: NumArray,
    color: str,
    dots_size: Num = 35,
) -> None:
    """添加散点"""
    ax.scatter(
        x_pos,
        data,
        c=color,
        s=dots_size,
        edgecolors="white",
        linewidths=1,
        alpha=0.5,
    )


def set_yaxis(
    ax: Axes,
    data: NumArray,
    options: dict[str, Any] | None,
) -> None:
    """设置Y轴格式"""
    if options.get("y_lim_range"):
        ax.set_ylim(*options["y_lim_range"])
    else:
        y_min, y_max = np.min(data), np.max(data)
        y_range = y_max - y_min
        golden_ratio = 5**0.5 - 1
        ax_min = (
            0
            if options.get("ax_min_is_0")
            else y_min - (y_range / golden_ratio - y_range / 2)
        )
        ax_max = y_max + (y_range / golden_ratio - y_range / 2)
        ax.set_ylim(ax_min, ax_max)

    if options.get("y_max_tick_to_one"):
        ticks = [
            tick
            for tick in ax.get_yticks()
            if tick <= options.get("y_max_tick_to_value", 1)
        ]
        ax.set_yticks(ticks)

    if options.get("math_text", True) and (np.min(data) < 0.1 or np.max(data) > 100):
        formatter = ScalarFormatter(useMathText=True)
        formatter.set_powerlimits((-2, 2))
        ax.yaxis.set_major_formatter(formatter)

    if options.get("one_decimal_place"):
        if options.get("math_text", True):
            print("“one_decimal_place”会与“math_text”冲突，请关闭“math_text”后再开启！")
        else:
            ax.yaxis.set_major_formatter(plt.FormatStrFormatter("%.1f"))

    if options.get("percentage"):
        if options.get("math_text", True):
            print("“percentage”会与“math_text”冲突，请关闭“math_text”后再开启！")
        else:
            ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"{x:.0%}"))


def perform_stat_test(
    data1: NumArray,
    data2: NumArray,
    method: str,
) -> tuple[float, float]:
    """执行统计检验"""
    if method == "ttest_ind":
        stat, p = stats.ttest_ind(data1, data2)
    elif method == "ttest_rel":
        stat, p = stats.ttest_rel(data1, data2)
    elif method == "mannwhitneyu":
        stat, p = stats.mannwhitneyu(data1, data2, alternative="two-sided")
    else:
        raise ValueError(f"未知统计方法: {method}")
    return stat, p


def annotate_significance(
    ax: Axes,
    comparisons: list[tuple[int, int, float]],
    y_base: Num,
    interval: Num,
    line_color: str,
    star_offset: Num,
    fontsize: Num,
    color: str,
) -> None:
    """添加显著性星号和连线"""
    for (i, j, pval), count in zip(comparisons, range(1, len(comparisons) + 1)):
        y = y_base + count * interval
        ax.annotate(
            "",
            xy=(i, y),
            xytext=(j, y),
            arrowprops=dict(
                edgecolor=line_color, width=0.5, headwidth=0.1, headlength=0.1
            ),
        )
        stars = "*" if pval > 0.01 else "**" if pval > 0.001 else "***"
        ax.text(
            (i + j) / 2,
            y + star_offset,
            stars,
            ha="center",
            va="center",
            color=color,
            fontsize=fontsize,
        )


def plot_one_group_bar_figure(
    data: list[NumArray],
    ax: Axes | None = None,
    labels_name: list[str] | None = None,
    width: Num = 0.5,
    colors: list[str] | None = None,
    dots_size: Num = 35,
    dots_color: list[list[str]] | None = None,
    title_name: str = "",
    x_label_name: str = "",
    y_label_name: str = "",
    statistic: bool = False,
    test_method: str = "ttest_ind",
    p_list: list[float] | None = None,
    errorbar_type: str = "se",
    **kwargs: Any,
) -> None:
    """绘制单组柱状图，包含散点和误差条。

    Args:
        data (list[NumArray]): 包含多个数据集的列表，每个数据集是一个数字数组。
        ax (Axes | None, optional): matplotlib 的 Axes 对象，用于绘图。默认为 None，使用当前的 Axes。
        labels_name (list[str] | None, optional): 每个数据集的标签名称。默认为 None，使用索引作为标签。
        width (Num, optional): 柱子的宽度。默认为 0.5。
        colors (list[str] | None, optional): 每个柱子的颜色。默认为 None，使用灰色。
        dots_size (Num, optional): 散点的大小。默认为 35。
        dots_color (list[list[str]] | None, optional): 每个数据集中散点的颜色。默认为 None，使用灰色。
        title_name (str, optional): 图表的标题。默认为空字符串。
        x_label_name (str, optional): X 轴的标签。默认为空字符串。
        y_label_name (str, optional): Y 轴的标签。默认为空字符串。
        statistic (bool, optional): 是否进行统计检验并标注显著性标记。默认为 False。
        test_method (str, optional): 统计检验的方法，支持 "ttest_ind"、"ttest_rel" 和 "mannwhitneyu"。默认为 "ttest_ind"。
        p_list (list[float] | None, optional): 外部提供的 p 值列表，用于统计检验。默认为 None。
        errorbar_type (str, optional): 误差条类型，支持 "sd"（标准差）和 "se"（标准误）。默认为 "se"。
        **kwargs (Any): 其他可选参数，用于进一步定制图表样式。

    Returns:
        None
    """

    if ax is None:
        ax = plt.gca()
    if labels_name is None:
        labels_name = [str(i) for i in range(len(data))]
    if colors is None:
        colors = ["gray"] * len(data)

    np.random.seed(1998)

    means, sds, ses = [], [], []
    x_positions = np.arange(len(labels_name))
    scatter_positions = []

    for i, d in enumerate(data):
        mean, sd, se = compute_summary(d)
        means.append(mean)
        sds.append(sd)
        ses.append(se)
        scatter_x = np.random.normal(i, 0.1, len(d))
        scatter_positions.append(scatter_x)

    if errorbar_type == "sd":
        error_values = sds
    elif errorbar_type == "se":
        error_values = ses

    # 绘制柱子
    ax.bar(x_positions, means, width=width, color=colors, alpha=1, edgecolor="k")
    ax.errorbar(
        x_positions,
        means,
        error_values,
        fmt="none",
        linewidth=1,
        capsize=3,
        color="black",
    )

    # 绘制散点
    for i, d in enumerate(data):
        if dots_color is None:
            add_scatter(ax, scatter_positions[i], d, ["gray"] * len(d), dots_size)
        else:
            add_scatter(ax, scatter_positions[i], d, dots_color[i], dots_size)

    # 美化
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title(
        title_name,
        fontsize=kwargs.get("title_fontsize", 10),
        pad=kwargs.get("title_pad", 20),
    )
    ax.set_xlabel(x_label_name, fontsize=kwargs.get("x_label_fontsize", 10))
    ax.set_ylabel(y_label_name, fontsize=kwargs.get("y_label_fontsize", 10))
    ax.set_xticks(x_positions)
    ax.set_xticklabels(
        labels_name,
        ha=kwargs.get("x_label_ha", "center"),
        rotation_mode="anchor",
        fontsize=kwargs.get("x_tick_fontsize", 10),
        rotation=kwargs.get("x_tick_rotation", 0),
    )
    ax.tick_params(
        axis="y",
        labelsize=kwargs.get("y_tick_fontsize", 10),
        rotation=kwargs.get("y_tick_rotation", 0),
    )

    all_values = np.concatenate(data)
    set_yaxis(ax, all_values, kwargs)

    # 添加统计显著性标记
    if statistic:
        comparisons = []
        idx = 0
        for i in range(len(data)):
            for j in range(i + 1, len(data)):
                if test_method == "external":
                    p = p_list[idx]
                    idx += 1
                else:
                    _, p = perform_stat_test(data[i], data[j], test_method)
                if p <= 0.05:
                    comparisons.append((i, j, p))

        y_max = ax.get_ylim()[1]
        interval = (y_max - np.max(all_values)) / (len(comparisons) + 1)
        annotate_significance(
            ax,
            comparisons,
            np.max(all_values),
            interval,
            line_color=kwargs.get("line_color", "0.5"),
            star_offset=interval / 5,
            fontsize=kwargs.get("asterisk_fontsize", 10),
            color=kwargs.get("asterisk_color", "k"),
        )


def plot_one_group_violin_figure(
    data: list[NumArray],
    ax: Axes | None = None,
    labels_name: list[str] | None = None,
    width: Num = 0.8,
    colors: list[str] | None = None,
    show_dots: bool = False,
    dots_size: Num = 35,
    title_name: str = "",
    x_label_name: str = "",
    y_label_name: str = "",
    statistic: bool = False,
    test_method: str = "ttest_ind",
    p_list: list[float] | None = None,
    show_means: bool = False,
    show_extrema: bool = True,
    **kwargs: Any,
) -> None:
    """绘制单组小提琴图，包含散点和统计显著性标记。

    Args:
        data (list[NumArray]): 包含多个数据集的列表，每个数据集是一个数字数组。
        ax (Axes | None, optional): matplotlib 的 Axes 对象，用于绘图。默认为 None，使用当前的 Axes。
        labels_name (list[str] | None, optional): 每个数据集的标签名称。默认为 None，使用索引作为标签。
        width (Num, optional): 小提琴图的宽度。默认为 0.8。
        colors (list[str] | None, optional): 每个小提琴图的颜色。默认为 None，使用灰色。
        show_dots (bool, optional): 是否显示散点。默认为 False。
        dots_size (Num, optional): 散点的大小。默认为 35。
        title_name (str, optional): 图表的标题。默认为空字符串。
        x_label_name (str, optional): X 轴的标签。默认为空字符串。
        y_label_name (str, optional): Y 轴的标签。默认为空字符串。
        statistic (bool, optional): 是否进行统计检验并标注显著性标记。默认为 False。
        test_method (str, optional): 统计检验的方法，支持 "ttest_ind"、"ttest_rel" 和 "mannwhitneyu"。默认为 "ttest_ind"。
        p_list (list[float] | None, optional): 外部提供的 p 值列表，用于统计检验。默认为 None。
        show_means (bool, optional): 是否显示均值线。默认为 False。
        show_extrema (bool, optional): 是否显示极值线。默认为 True。
        **kwargs (Any): 其他可选参数，用于进一步定制图表样式。

    Returns:
        None
    """

    ax = ax or plt.gca()
    labels_name = labels_name or [str(i) for i in range(len(data))]
    colors = colors or ["gray"] * len(data)

    np.random.seed(1998)  # 固定随机种子保证散点位置可复现

    # 绘制小提琴图
    parts = ax.violinplot(
        dataset=list(data),
        positions=np.arange(len(data)),
        widths=width,
        showmeans=show_means,
        showextrema=show_extrema,
    )

    # 设置小提琴颜色（修改默认样式）
    for pc, color in zip(parts["bodies"], colors):
        pc.set_facecolor(color)
        pc.set_edgecolor("black")
        pc.set_alpha(0.7)

    # 修改内部线条颜色
    if show_extrema:
        parts["cmins"].set_color("black")  # 最小值线
        parts["cmaxes"].set_color("black")  # 最大值线
        parts["cbars"].set_color("black")  # 中线（median）
    if show_means:
        parts["cmeans"].set_color("black")  # 均值线

    # 绘制散点（复用现有函数）
    if show_dots:
        scatter_positions = [
            np.random.normal(i, 0.1, len(d)) for i, d in enumerate(data)
        ]
        for i, d in enumerate(data):
            add_scatter(ax, scatter_positions[i], d, colors[i], dots_size)

    # 美化坐标轴（复用现有函数）
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title(title_name, fontsize=kwargs.get("title_fontsize", 10), pad=20)
    ax.set_xlabel(x_label_name, fontsize=kwargs.get("x_label_fontsize", 10))
    ax.set_ylabel(y_label_name, fontsize=kwargs.get("y_label_fontsize", 10))
    ax.set_xticks(np.arange(len(data)))
    ax.set_xticklabels(
        labels_name,
        fontsize=kwargs.get("x_tick_fontsize", 10),
        rotation=kwargs.get("x_tick_rotation", 0),
    )

    # 设置Y轴（复用现有函数）
    all_values = np.concatenate(data)
    set_yaxis(ax, all_values, kwargs)

    # 添加统计标记（复用现有函数）
    if statistic:
        comparisons = []
        idx = 0
        for i in range(len(data)):
            for j in range(i + 1, len(data)):
                if test_method == "external":
                    p = p_list[idx] if p_list else 1.0
                    idx += 1
                else:
                    _, p = perform_stat_test(data[i], data[j], test_method)
                if p <= 0.05:
                    comparisons.append((i, j, p))

        if comparisons:
            y_max = ax.get_ylim()[1]
            interval = (y_max - np.max(all_values)) / (len(comparisons) + 1)
            annotate_significance(
                ax,
                comparisons,
                np.max(all_values),
                interval,
                line_color=kwargs.get("line_color", "0.5"),
                star_offset=interval / 5,
                fontsize=kwargs.get("asterisk_fontsize", 10),
                color=kwargs.get("asterisk_color", "k"),
            )


def plot_multi_group_bar_figure(
    data: list[list[NumArray]],
    ax: plt.Axes | None = None,
    bar_width: Num = 0.2,
    bar_gap: Num = 0.1,
    bar_color: list[str] | None = None,
    errorbar_type: str = "se",
    dots_color: str = "gray",
    dots_size: int = 35,
    group_labels: list[str] | None = None,
    bar_labels: list[str] | None = None,
    title_name: str = "",
    y_label_name: str = "",
    statistic: bool = False,
    test_method: str = "external",
    p_list: list[list[Num]] | None = None,
    legend: bool = True,
    legend_position: tuple[Num, Num] = (1.2, 1),
    **kwargs: Any,
) -> None:
    """绘制多组柱状图，包含散点和误差条。

    Args:
        data (list[list[NumArray]]): 包含多个组的数据，每组是一个数据集列表，每个数据集是一个数字数组。
        ax (plt.Axes | None, optional): matplotlib 的 Axes 对象，用于绘图。默认为 None，使用当前的 Axes。
        bar_width (Num, optional): 每个柱子的宽度。默认为 0.2。
        bar_gap (Num, optional): 柱子之间的间隙。默认为 0.1。
        bar_color (list[str] | None, optional): 每个柱子的颜色。默认为 None，使用灰色。
        errorbar_type (str, optional): 误差条类型，支持 "sd"（标准差）和 "se"（标准误）。默认为 "se"。
        dots_color (str, optional): 散点的颜色。默认为 "gray"。
        dots_size (int, optional): 散点的大小。默认为 35。
        group_labels (list[str] | None, optional): 每组的标签名称。默认为 None，使用 "Group i" 作为标签。
        bar_labels (list[str] | None, optional): 每个柱子的标签名称。默认为 None，使用 "Bar i" 作为标签。
        title_name (str, optional): 图表的标题。默认为空字符串。
        y_label_name (str, optional): Y 轴的标签。默认为空字符串。
        statistic (bool, optional): 是否进行统计检验并标注显著性标记。默认为 False。
        test_method (str, optional): 统计检验的方法，支持 "external"（外部提供 p 值）和其他方法。默认为 "external"。
        p_list (list[list[Num]] | None, optional): 外部提供的 p 值列表，用于统计检验。默认为 None。
        legend (bool, optional): 是否显示图例。默认为 True。
        legend_position (tuple[Num, Num], optional): 图例的位置。默认为 (1.2, 1)。
        **kwargs (Any): 其他可选参数，用于进一步定制图表样式。

    Returns:
        None
    """

    # 动态参数
    if ax is None:
        ax = plt.gca()
    n_groups = len(data)
    if group_labels is None:
        group_labels = [f"Group {i + 1}" for i in range(n_groups)]
    # 把所有子列表展开成一个大列表
    all_values = [x for sublist1 in data for sublist2 in sublist1 for x in sublist2]

    x_positions_all = []
    for index_group, group_data in enumerate(data):
        n_bars = len(group_data)
        if bar_labels is None:
            bar_labels = [f"Bar {i + 1}" for i in range(n_bars)]
        if bar_color is None:
            bar_color = ["gray"] * n_bars

        x_positions = (
            np.arange(n_bars) * (bar_width + bar_gap)
            + bar_width / 2
            + index_group
            - (n_bars * bar_width + (n_bars - 1) * bar_gap) / 2
        )
        x_positions_all.append(x_positions)

        # 计算均值、标准差、标准误
        means = [compute_summary(group_data[i])[0] for i in range(n_bars)]
        sds = [compute_summary(group_data[i])[1] for i in range(n_bars)]
        ses = [compute_summary(group_data[i])[2] for i in range(n_bars)]
        if errorbar_type == "sd":
            error_values = sds
        elif errorbar_type == "se":
            error_values = ses
        # 绘制柱子
        bars = ax.bar(
            x_positions, means, width=bar_width, color=bar_color, alpha=1, edgecolor="k"
        )
        ax.errorbar(
            x_positions,
            means,
            error_values,
            fmt="none",
            linewidth=1,
            capsize=3,
            color="black",
        )
        # 绘制散点
        for index_bar, dot in enumerate(group_data):
            dot_x_pos = np.random.normal(
                x_positions[index_bar], scale=bar_width / 7, size=len(dot)
            )
            add_scatter(ax, dot_x_pos, dot, dots_color, dots_size=dots_size)
    if legend:
        ax.legend(bars, bar_labels, bbox_to_anchor=legend_position)
    # x轴
    ax.set_xticks(np.arange(n_groups))
    ax.set_xticklabels(
        group_labels,
        fontsize=kwargs.get("x_tick_fontsize", 10),
        rotation=kwargs.get("x_tick_rotation", 0),
    )
    # 美化
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title(
        title_name,
        fontsize=kwargs.get("title_fontsize", 15),
        pad=kwargs.get("title_pad", 20),
    )
    ax.set_ylabel(y_label_name, fontsize=kwargs.get("y_label_fontsize", 10))
    set_yaxis(ax, all_values, kwargs)
    # 添加统计显著性标记
    if statistic:
        for index_group, group_data in enumerate(data):
            x_positions = x_positions_all[index_group]
            comparisons = []
            idx = 0
            for i in range(len(group_data)):
                for j in range(i + 1, len(group_data)):
                    if test_method == "external":
                        p = p_list[index_group][idx]
                        idx += 1
                    if p <= 0.05:
                        comparisons.append((x_positions[i], x_positions[j], p))
            y_max = ax.get_ylim()[1]
            interval = (y_max - np.max(all_values)) / (len(comparisons) + 1)
            annotate_significance(
                ax,
                comparisons,
                np.max(all_values),
                interval,
                line_color=kwargs.get("line_color", "0.5"),
                star_offset=interval / 5,
                fontsize=kwargs.get("asterisk_fontsize", 10),
                color=kwargs.get("asterisk_color", "k"),
            )


def main():
    pass


if __name__ == "__main__":
    main()
