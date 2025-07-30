from enum import Enum
from typing import Sequence

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.use('TkAgg')


class GraphType(Enum):
    # 散点图
    SCATTER = 0, 'scatter',
    # 折线图
    LINE = 1, 'line',
    # 柱状图
    BAR = 2, 'bar'
    # 饼图
    PIE = 3, 'pie'
    # 直方图
    HIST = 4, 'hist'


def simple_draw(xs: Sequence, ys: Sequence, figure_order: int = 0,
                graph_type: GraphType = GraphType.SCATTER, show: bool = True, title: str = None,
                label: str | Sequence[str] | None = None,
                x_label: str = None, y_label: str = None, save_path: str = None, drawer_size: int = 1) -> bool:
    """
    绘制简单的图形，支持折线图、散点图、柱状图、饼图、直方图、箱线图

    :param xs: x轴数据，与y轴数据长度相同，用于绘制图形
    :param ys: y轴数据，与x轴数据长度相同，用于绘制图形
    :param figure_order: 背景板标号
    :param graph_type: 图形类型
    :param show: 是否展示图形
    :param title: 标题栏文字
    :param label: 图例
    :param x_label: x坐标轴文字
    :param y_label: y坐标轴文字
    :param save_path: 保存图片的路径
    :param drawer_size: 笔尖大小
    :return:
    """
    plt.figure(figure_order)
    if graph_type == GraphType.LINE:
        plt.plot(xs, ys, label=label, linewidth=drawer_size)
    elif graph_type == GraphType.SCATTER:
        plt.scatter(xs, ys, label=label, s=drawer_size)
    elif graph_type == GraphType.BAR:
        plt.bar(xs, ys, label=label, width=drawer_size)
    elif graph_type == GraphType.PIE:
        plt.pie(ys, labels=xs, autopct='%1.1f%%')
    elif graph_type == GraphType.HIST:
        plt.hist(ys, bins=xs, label=label, rwidth=drawer_size)
    else:
        return False
    if label is not None:
        plt.legend()
    if title is not None:
        plt.title(title)
    if x_label is not None:
        plt.xlabel(x_label)
    if y_label is not None:
        plt.ylabel(y_label)
    if save_path is not None:
        plt.savefig(save_path)
    if show:
        plt.show(block=True)
    return True


def draw_with_rgba_image(rgba_data, save_path: str = None):
    """
    根据 RGBA 数据绘制图片并保存到指定路径

    参数:
        rgba_data (numpy.ndarray): 形状为 (H, W, 4) 的 RGBA 数组，取值范围 [0, 1] 或 [0, 255]
        save_path (str): 图片保存路径（支持 .png, .jpg 等格式）
    """
    # 确保数据是 numpy 数组
    rgba_data = np.asarray(rgba_data)

    # 检查数据范围并归一化到 [0, 1]
    if rgba_data.dtype == np.uint8 or np.max(rgba_data) > 1.0:
        rgba_data = rgba_data.astype(float) / 255.0

    # 创建 figure 和 axis，关闭坐标轴
    fig, ax = plt.subplots(figsize=(rgba_data.shape[1] / 100, rgba_data.shape[0] / 100), dpi=100)
    ax.axis('off')  # 不显示坐标轴

    # 显示 RGBA 图像
    ax.imshow(rgba_data)

    # 调整布局，去除空白边距
    plt.tight_layout(pad=0)

    if save_path is not None and len(save_path) > 0:
        # 保存图像（bbox_inches='tight' 确保保存完整内容）
        plt.savefig(save_path, bbox_inches='tight', pad_inches=0, dpi='figure')

    plt.show()

    # 关闭图形，释放内存
    plt.close(fig)
