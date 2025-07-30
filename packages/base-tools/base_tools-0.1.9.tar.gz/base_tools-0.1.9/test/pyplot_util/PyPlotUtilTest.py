import unittest

import matplotlib.pyplot as plt
import numpy as np

from src.cjlutils import PyplotUtil
from src.cjlutils.PyplotUtil import GraphType


class SimpleDrawCase(unittest.TestCase):

    def test_common(self):
        figure_order = 0
        x_min = -0.2
        x_max = 1.2
        y_min = -0.2
        y_max = 1.2
        x_separators = (0.1, 0.9)
        y_separators = (0.1, 0.9)

        line_width = 1

        # 初始化画框
        plt.figure(figure_order)
        # 隐藏坐标轴
        plt.axis('off')
        plt.plot([x_min, x_max], [y_min, y_min], linewidth=line_width, color='black')
        plt.plot([x_min, x_max], [y_min, y_min], linewidth=line_width, color='black')
        plt.plot([x_min, x_max], [y_min, y_min], linewidth=line_width, color='black')
        plt.plot([x_min, x_max], [y_min, y_min], linewidth=line_width, color='black')
        plt.show()

    def test_simple(self):
        location: np.ndarray = np.array([
            [0, 0.7, ],
            [0.1, 0.9, ],
            [0.4, 0.8, ],
            [0.2, 0.5, ],
            [0.6, 0.0, ],
            [0.9, 0.9, ],
        ])
        PyplotUtil.set_figure_lim(0, -.2, 1.2, -.2, 1.2)
        PyplotUtil.simple_draw_picture(location[:, 0], location[:, 1], figure_order=0, graph_type=GraphType.SCATTER)
        PyplotUtil.finish_draw_and_show(0)

    def test_ion(self):
        plt.ion()  # 打开交互模式
        plt.xlim(0, 3)
        plt.ylim(0, 100)
        plt.axis('off')
        line, = plt.plot([1, 2, 3])
        for i in range(1000):
            line.set_ydata([i / 10, (i + 1) / 10, (i + 2) / 10])  # 更新数据
            plt.draw()  # 手动刷新
            plt.pause(0.01)  # 短暂暂停

    def test_scatter(self):
        x: np.ndarray = np.array(list(range(-10, 11)))
        y = x ** 2

        # 创建一个图形并绘制点图
        figure_index = 1
        title = '点图 Scatter Plot'
        PyplotUtil.simple_draw(x, y, figure_order=figure_index, graph_type=GraphType.SCATTER, show=True, label='line',
                               title=title, save_path=f'./img/{title}.png')

    def test_many_scatters(self):
        repeat = 10
        title = '点图 Scatters Plot'
        figure_index = 1
        for i in range(repeat):
            # 创建一个图形并绘制点图
            x: np.ndarray = np.array(list(range(-i, i + 1)))
            y = x + i
            PyplotUtil.simple_draw(x, y, figure_order=figure_index, graph_type=GraphType.SCATTER, show=False,
                                   title=title, label=f'line {i}', save_path=f'./img/{title}.png')
        plt.show()

    def test_line(self):
        x: np.ndarray = np.array(list(range(-10, 11)))
        y = x ** 2

        # 创建一个图形并绘制折线图
        figure_index = 1
        title = '折线图 Line Plot'
        PyplotUtil.simple_draw(x, y, figure_order=figure_index, graph_type=GraphType.LINE, show=True, title=title,
                               label='line', save_path=f'./img/{title}.png')

    def test_many_lines(self):
        repeat = 10
        title = '折线图 Lines Plot'
        figure_index = 1
        for i in range(repeat):
            # 创建一个图形并绘制点图
            x: np.ndarray = np.array(list(range(-10, 11)))
            y = x ** 2 - i * x
            PyplotUtil.simple_draw(x, y, figure_order=figure_index, graph_type=GraphType.LINE, show=False,
                                   title=title, label=f'line {i}', save_path=f'./img/{title}.png')
        plt.title(title)
        plt.xlabel('x')
        plt.ylabel('y')
        plt.show()

    def test_bar(self):
        x: np.ndarray = np.array(list(range(-10, 11)))
        y = x ** 2

        # 创建一个图形并绘制柱状图
        figure_index = 1
        title = '柱状图 Bar Plot'
        PyplotUtil.simple_draw(x, y, figure_order=figure_index, graph_type=GraphType.BAR, show=True, title=title,
                               label='line', save_path=f'./img/{title}.png')

    def test_pie(self):
        x: np.ndarray = np.array(list(range(-10, 11)))
        y = x ** 2

        # 创建一个图形并绘制饼图
        figure_index = 1
        title = '饼图 Pie Plot'
        PyplotUtil.simple_draw(x, y, figure_order=figure_index, graph_type=GraphType.PIE, show=True, title=title,
                               label='line', save_path=f'./img/{title}.png')

    def test_hist(self):
        x: np.ndarray = np.array(list(range(-10, 11)))
        y = x ** 2

        # 创建一个图形并绘制饼图
        figure_index = 1
        title = '直方图 Hist Plot'
        PyplotUtil.simple_draw(x, y, figure_order=figure_index, graph_type=GraphType.HIST, show=True, title=title,
                               label='line', save_path=f'./img/{title}.png')


if __name__ == '__main__':
    unittest.main()
