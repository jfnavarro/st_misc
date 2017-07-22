import argparse
import sys

from PySide import QtGui
from PySide.QtCore import Qt, Signal

from PIL import Image

class ImageSection(QtGui.QMainWindow):
    def __init__(self, large_image, pt1, pt2, sizes):
        super(ImageSection, self).__init__()

        self.setWindowTitle("Homography - Pick feature")

        self.image_label = QtGui.QLabel()
        self.image_label.setBackgroundRole(QtGui.QPalette.Base)


        p1x = int(pt1.x() / float(sizes[0]) * large_image.size[0])
        p1y = int(pt1.y() / float(sizes[1]) * large_image.size[1])
        p2x = int(pt2.x() / float(sizes[0]) * large_image.size[0])
        p2y = int(pt2.y() / float(sizes[1]) * large_image.size[1])

        left = min(p1x, p2x)
        top = min(p1y, p2y)
        bottom = max(p1y, p2y)
        right = max(p1x, p2x)

        image_section = large_image.crop((left, top, right, bottom))
        self.left = left
        self.top = top

        data = image_section.convert("RGBA").tostring("raw", "RGBA")

        image = QtGui.QImage(data, image_section.size[0], \
                             image_section.size[1], \
                             QtGui.QImage.Format_ARGB32)

        pix = QtGui.QPixmap.fromImage(image)

        self.image_label.setPixmap(pix)

        self.setCentralWidget(self.image_label)

        self.x_edit = QtGui.QLineEdit()
        self.y_edit = QtGui.QLineEdit()

        hbox_edit = QtGui.QHBoxLayout()
        hbox_edit.addStretch(1)
        hbox_edit.addWidget(self.x_edit)
        hbox_edit.addWidget(self.y_edit)

        self.x_label = QtGui.QLabel()
        self.x_label.setText("Test")
        self.y_label = QtGui.QLabel()

        hbox_labels = QtGui.QHBoxLayout()
        hbox_labels.addStretch(1)
        hbox_labels.addWidget(self.x_label)
        hbox_labels.addWidget(self.y_label)

        vbox = QtGui.QVBoxLayout(self.image_label)
        vbox.addStretch(1)
        vbox.addLayout(hbox_labels)
        vbox.addLayout(hbox_edit)

        self.setLayout(vbox)
        self.show()

    def mousePressEvent(self, event):
        self.setFocus()

        if event.button() == Qt.LeftButton:
            if event.modifiers() & Qt.ControlModifier:
                pass
            else:
                self.mdown_point = event.pos()
                self.x_edit.setText(str(self.left + self.mdown_point.x()))
                print("Press:")
                print(self.mdown_point)


class ImagePreview(QtGui.QMainWindow):
    def __init__(self, img_file_name):
        super(ImagePreview, self).__init__()
        self.setWindowTitle("Homography - Pick corner areas")

        self.file_name = img_file_name
        self.image_label = QtGui.QLabel()
        self.image_label.setBackgroundRole(QtGui.QPalette.Base)

        pix = self.file_to_pixmap()
        self.image_label.setPixmap(pix)

        self.setCentralWidget(self.image_label)


    def file_to_pixmap(self, preview_size=400):
        self.large_image = Image.open(self.file_name)

        width_fraction = preview_size / float(self.large_image.size[0])
        height = int(float(self.large_image.size[1]) * width_fraction)

        preview_image = self.large_image.resize((preview_size, height))

        self.small_size = preview_image.size

        data = preview_image.convert("RGBA").tostring("raw", "RGBA")

        image = QtGui.QImage(data, preview_image.size[0], \
                             preview_image.size[1], \
                             QtGui.QImage.Format_ARGB32)

        pix = QtGui.QPixmap.fromImage(image)

        return pix

    def mousePressEvent(self, event):
        self.setFocus()

        if event.button() == Qt.LeftButton:
            if event.modifiers() & Qt.ControlModifier:
                pass
            else:
                self.mdown_point = event.pos()
                print("Press:")
                print(self.mdown_point)


    def mouseReleaseEvent(self, event):
        self.setFocus()

        if event.button() == Qt.LeftButton:
            if event.modifiers() & Qt.ControlModifier:
                pass
            else:
                self.mup_point = event.pos()
                print("Release:")
                print(self.mup_point)

                self.image_section_window = ImageSection(self.large_image, \
                                                         self.mdown_point, \
                                                         self.mup_point, \
                                                         self.small_size)

                self.image_section_window.show()


def main(img_file_name, preview_size=400):
    app = QtGui.QApplication([])

    image_preview = ImagePreview(img_file_name)
    image_preview.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("img_file_name", \
        help="Image file to estimate homography from")

    args = parser.parse_args()

    main(args.img_file_name)
