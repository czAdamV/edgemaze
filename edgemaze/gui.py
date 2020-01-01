from PyQt5 import QtWidgets, QtCore, QtGui, QtSvg, uic
from .edgemaze import analyze

import numpy


VALUE_ROLE = QtCore.Qt.UserRole
SVG_GRASS = QtSvg.QSvgRenderer('edgemaze/graphics/grass.svg')
SVG_WALL = QtSvg.QSvgRenderer('edgemaze/graphics/wall.svg')
SVG_CASTLE = QtSvg.QSvgRenderer('edgemaze/graphics/castle.svg')
SVG_V_WALL = QtSvg.QSvgRenderer('edgemaze/graphics/wall_vertical.svg')
SVG_H_WALL = QtSvg.QSvgRenderer('edgemaze/graphics/wall_horizontal.svg')
SVG_DUDES = [
    QtSvg.QSvgRenderer(f'edgemaze/graphics/dude{i}.svg') for i in range(1, 6)
]
SVG_LINES = [
    QtSvg.QSvgRenderer(f'edgemaze/graphics/lines/{i}.svg') for i in range(1, 16)
]
SVG_ARROWS = [
    QtSvg.QSvgRenderer(f'edgemaze/graphics/arrows/{i}.svg') for i in
    ['down', 'left', 'right', 'up']
]


class GridWidget(QtWidgets.QWidget):
    def __init__(self, array):
        super().__init__()
        self.array = array
        self.solution = None
        self.paths = None
        self.arrows = None
        self.cell_size = 48
        self.resize_logical(*array.shape)
        self.refresh_path()

    def resize_logical(self, rows, cols):
        size = self.logical_to_pixels(rows, cols)
        self.setMinimumSize(*size)
        self.setMaximumSize(*size)
        self.resize(*size)

    def pixels_to_logical(self, x, y):
        return y // self.cell_size, x // self.cell_size

    def logical_to_pixels(self, row, column):
        return column * self.cell_size, row * self.cell_size

    def iterate_path(self, tile):
        direction = self.solution.directions[tile]
        next = None
        arrow = None
        path_in = None
        path_out = None

        if direction == b'>':
            next = (tile[0], tile[1] + 1)
            arrow = 3
            path_in = 2
            path_out = 8

        if direction == b'v':
            next = (tile[0] + 1, tile[1])
            arrow = 1
            path_in = 1
            path_out = 4

        if direction == b'<':
            next = (tile[0], tile[1] - 1)
            arrow = 2
            path_in = 8
            path_out = 2

        if direction == b'^':
            next = (tile[0] - 1, tile[1])
            arrow = 4
            path_in = 4
            path_out = 1

        return next, path_in, path_out, arrow

    def refresh_path(self):
        self.solution = analyze(self.array)
        self.paths = numpy.full_like(self.array, 0, dtype=numpy.uint8)
        self.arrows = numpy.full_like(self.array, 0, dtype=numpy.uint8)

        for dude in zip(*numpy.where(self.array & 0b11111000)):
            now = dude
            path_in = None
            while True:
                if path_in:
                    self.paths[now] |= path_in

                next, path_in, path_out, arrow = self.iterate_path(now)

                if not next:
                    break

                self.paths[now] |= path_out

                if self.arrows[now] != 0:
                    break

                self.arrows[now] = arrow

                if next == 'X':
                    break

                now = next


    def mousePressEvent(self, event):
        x, y = event.x(), event.y()
        row, column = self.pixels_to_logical(x, y)

        # Quadrant names:
        #  _____________
        # |\     0     /|
        # |  \       /  |
        # |    \   /    |
        # | 2    X    1 |
        # |    /   \    |
        # |  /       \  |
        # |/     3     \|
        #  ¯¯¯¯¯¯¯¯¯¯¯¯¯ 

        x_cell = x % self.cell_size
        y_cell = y % self.cell_size

        if self.selected == -1:
            quadrant = 0

            if y_cell > x_cell:
                quadrant |= 0b10

            if y_cell > -x_cell + self.cell_size:
                quadrant |= 0b01

            if quadrant == 0 or quadrant == 3:
                tile = 0b100
            else:
                tile = 0b010

            if quadrant == 1:
                column += 1

            if quadrant == 3:
                row += 1

            if quadrant == 0 and row == 0:
                row -= 1 # Go out of bounds to prevent wall palcement

            if quadrant == 2 and column == 0:
                column -= 1 # Same as above

        else:
            tile = self.selected


        # Update only within the matrix bounds
        if 0 <= row < self.array.shape[0] and \
            0 <= column < self.array.shape[1]:

            if not tile & 0b110 and \
                self.array[row, column] & 0b11111001 != tile & 0b11111001:

                self.array[row, column] &= 0b110

            self.array[row, column] ^= tile

        self.refresh_path()
        self.update()


    def paintEvent(self, event):
        rect = event.rect()

        row_min, col_min = self.pixels_to_logical(rect.left(), rect.top())
        row_min = max(row_min, 0)
        col_min = max(col_min, 0)
        row_max, col_max = self.pixels_to_logical(rect.right(), rect.bottom())
        row_max = min(row_max + 1, self.array.shape[0])
        col_max = min(col_max + 1, self.array.shape[1])

        painter = QtGui.QPainter(self)

        half = self.cell_size // 2

        for row in range(row_min, row_max):
            for column in range(col_min, col_max):
                x, y = self.logical_to_pixels(row, column)
                rect = QtCore.QRectF(x, y, self.cell_size, self.cell_size)

                array = self.array[row, column]
                path = self.paths[row, column]
                arrow = self.arrows[row, column]

                # Paint grass
                SVG_GRASS.render(painter, rect)

                # Paint paths
                if path != 0:
                    SVG_LINES[path - 1].render(painter, rect)

                # Paint arrows
                if arrow != 0 and array <= 7:
                    SVG_ARROWS[arrow - 1].render(painter, rect)

                # Paint castle
                if array & 1:
                    SVG_CASTLE.render(painter, rect)

                # Paint dudes
                elif array > 7:
                    SVG_DUDES[(array >> 3) - 1] .render(painter, rect)

                # Paint wall left
                if array & 2:
                    SVG_V_WALL.render(painter,
                                      rect.adjusted(-half, 0, -half, 0))

                # Paint wall up
                if array & 4:
                    SVG_H_WALL.render(painter,
                                      rect.adjusted(0, -half, 0, -half))



class Main:
    def __init__(self):
        self.app = QtWidgets.QApplication([])
        self.window = QtWidgets.QMainWindow()

        with open('edgemaze/qt/mainwindow.ui') as f:
            uic.loadUi(f, self.window)

        # získáme oblast s posuvníky z Qt Designeru
        scroll_area = self.window.findChild(
            QtWidgets.QScrollArea,
            'scrollArea'
        )

        # dáme do ní náš grid
        self.grid = GridWidget(numpy.zeros((10, 10), dtype=numpy.int8))
        scroll_area.setWidget(self.grid)

        self.palette = self.window.findChild(QtWidgets.QListWidget, 'palette')

        self.add_to_pallete('Wall', -1, 'edgemaze/graphics/wall.svg')
        self.add_to_pallete('Castle', 1, 'edgemaze/graphics/castle.svg')
        for i in range(1, 6):
            self.add_to_pallete(f'Dude {i}', i << 3,
                                f'edgemaze/graphics/dude{i}.svg')
        self.add_to_pallete('Erase', 0, 'edgemaze/graphics/grass.svg')

        self.palette.itemSelectionChanged.connect(self.item_activated)
        self.palette.setCurrentRow(1)

        actionNew = self.window.findChild(QtWidgets.QAction, 'actionNew')
        actionNew.triggered.connect(self.new_dialog)

        actionLoad = self.window.findChild(QtWidgets.QAction, 'actionLoad')
        actionLoad.triggered.connect(self.load)

        actionLoad = self.window.findChild(QtWidgets.QAction, 'actionSave_As')
        actionLoad.triggered.connect(self.save_as)

        actionAbout = self.window.findChild(QtWidgets.QAction, 'actionAbout')
        actionAbout.triggered.connect(self.show_about)

        actionAbout = self.window.findChild(QtWidgets.QAction, 'actionZoom_in')
        actionAbout.triggered.connect(self.zoom_in)

        actionAbout = self.window.findChild(
            QtWidgets.QAction, 'actionZoom_out'
        )
        actionAbout.triggered.connect(self.zoom_out)

    def add_to_pallete(self, name, value, icon=None):
        item = QtWidgets.QListWidgetItem(name)

        if icon:
            icon = QtGui.QIcon(icon)
            item.setIcon(icon)

        item.setData(VALUE_ROLE, value)

        self.palette.addItem(item)

    def new_dialog(self):
        dialog = QtWidgets.QDialog(self.window)

        with open('edgemaze/qt/newmaze.ui') as f:
            uic.loadUi(f, dialog)

        result = dialog.exec()

        if result == QtWidgets.QDialog.Rejected:
            return

        cols = dialog.findChild(QtWidgets.QSpinBox, 'widthBox').value()
        rows = dialog.findChild(QtWidgets.QSpinBox, 'heightBox').value()

        self.grid.array = numpy.zeros((rows, cols), dtype=numpy.int8)
        self.grid.resize_logical(rows, cols)
        self.grid.refresh_path()

    def item_activated(self):
        for item in self.palette.selectedItems():
            self.grid.selected = item.data(VALUE_ROLE)

    def load(self):
        filename = QtWidgets.QFileDialog.getOpenFileName()
        if filename[0] == '':
            return

        try:
            self.grid.array = numpy.loadtxt(filename[0], dtype=numpy.int8)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.window, 'Error', str(e))

        self.grid.refresh_path()
        self.grid.update()

    def save_as(self):
        filename = QtWidgets.QFileDialog.getSaveFileName()

        try:
            numpy.savetxt(filename[0], self.grid.array)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.window, 'Error', str(e))

    def show_about(self):
        with open('edgemaze/about.html', 'r') as file:
            about = file.read()
        QtWidgets.QMessageBox.about(self.window, 'About edgemaze', about)

    def zoom_in(self):
        if self.grid.cell_size <= 512:
            self.grid.cell_size = int(self.grid.cell_size * 1.5)
            self.grid.resize_logical(*self.grid.array.shape)
            self.grid.update()

    def zoom_out(self):
        if self.grid.cell_size > 9:
            self.grid.cell_size = int(self.grid.cell_size // 1.5)
            self.grid.resize_logical(*self.grid.array.shape)
            self.grid.update()

    def main(self):
        self.window.show()
        return self.app.exec()


def main():
    main = Main()
    main.main()