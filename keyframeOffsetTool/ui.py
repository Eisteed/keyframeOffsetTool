try:
    # Maya 2025 and newer use Qt 6.
    from PySide6 import QtCore, QtWidgets
except ImportError:
    # Keep the tool usable in Maya versions that still ship Qt 5.
    from PySide2 import QtCore, QtWidgets

Qt = QtCore.Qt
import maya.cmds as cmds
import  keyframeOffsetTool.utils as utils


def _dpi_scale():
    """Get the OS display scale factor (e.g. 1.0, 1.25, 1.5, 2.0)."""
    try:
        screen = QtWidgets.QApplication.primaryScreen()
        return screen.logicalDotsPerInch() / 96.0
    except Exception:
        return 1.0


def _scaled(value):
    """Scale a pixel value by the DPI factor."""
    return int(value * _dpi_scale())


_keyframeOffsetRef = None
_keyframeOffsetFactor = 4.0
class KeyframeOffsetUI(QtWidgets.QMainWindow):
    
    @staticmethod
    def run():
        global _keyframeOffsetRef;
        _keyframeOffsetRef = _keyframeOffsetRef or KeyframeOffsetUI()
        _keyframeOffsetRef.show()

    def __init__(self, parent=None):
        super(KeyframeOffsetUI, self).__init__(parent = parent)
        self.setupUi()

    def setupUi(self):
        self.setObjectName("Form")
        window_stays_on_top = (
            Qt.WindowType.WindowStaysOnTopHint
            if hasattr(Qt, "WindowType")
            else Qt.WindowStaysOnTopHint
        )
        self.setWindowFlags(window_stays_on_top)

        # Apply a DPI-scaled stylesheet for inner widget padding and font size
        scale = _dpi_scale()
        font_size = _scaled(11)
        btn_pad_v = _scaled(4)
        btn_pad_h = _scaled(12)
        spin_pad = _scaled(3)
        self.setStyleSheet(
            "QWidget {{ font-size: {fs}px; }}"
            "QPushButton {{ padding: {bv}px {bh}px; }}"
            "QDoubleSpinBox {{ padding: {sp}px; }}"
            .format(fs=font_size, bv=btn_pad_v, bh=btn_pad_h, sp=spin_pad)
        )

        central = QtWidgets.QWidget(self)
        self.setCentralWidget(central)

        margin = _scaled(12)
        main_layout = QtWidgets.QVBoxLayout(central)
        main_layout.setContentsMargins(margin, margin, margin, margin)
        main_layout.setSpacing(_scaled(8))

        # Timeline label
        self.lb_timeline = QtWidgets.QLabel()
        self.lb_timeline.setObjectName("lb_timeline")
        main_layout.addWidget(self.lb_timeline)

        # Timeline row: In button | spin_in | stretch | spin_out | Out button
        timeline_row = QtWidgets.QHBoxLayout()
        timeline_row.setSpacing(_scaled(6))

        self.btn_in = QtWidgets.QPushButton()
        self.btn_in.setObjectName("btn_in")
        self.btn_in.setMinimumHeight(_scaled(28))
        timeline_row.addWidget(self.btn_in)

        self.spin_in = QtWidgets.QDoubleSpinBox()
        self.spin_in.setDecimals(1)
        self.spin_in.setMinimum(-10000.0)
        self.spin_in.setMaximum(10000.0)
        self.spin_in.setSingleStep(5.0)
        self.spin_in.setMinimumHeight(_scaled(28))
        self.spin_in.setMinimumWidth(_scaled(75))
        self.spin_in.setObjectName("spin_in")
        timeline_row.addWidget(self.spin_in)

        timeline_row.addStretch()

        self.spin_out = QtWidgets.QDoubleSpinBox()
        self.spin_out.setMinimum(-10000.0)
        self.spin_out.setMaximum(10000.0)
        self.spin_out.setSingleStep(5.0)
        self.spin_out.setMinimumHeight(_scaled(28))
        self.spin_out.setMinimumWidth(_scaled(75))
        self.spin_out.setObjectName("spin_out")
        timeline_row.addWidget(self.spin_out)

        self.btn_out = QtWidgets.QPushButton()
        self.btn_out.setObjectName("btn_out")
        self.btn_out.setMinimumHeight(_scaled(28))
        timeline_row.addWidget(self.btn_out)

        main_layout.addLayout(timeline_row)

        # Offset label
        self.lb_offset = QtWidgets.QLabel()
        self.lb_offset.setObjectName("lb_offset")
        main_layout.addWidget(self.lb_offset)

        # Slider
        self.sld_keyframe = QtWidgets.QSlider()
        self.sld_keyframe.setMinimum(-20)
        self.sld_keyframe.setMaximum(20)
        horizontal = (
            Qt.Orientation.Horizontal
            if hasattr(Qt, "Orientation")
            else Qt.Horizontal
        )
        ticks_above = (
            QtWidgets.QSlider.TickPosition.TicksAbove
            if hasattr(QtWidgets.QSlider, "TickPosition")
            else QtWidgets.QSlider.TicksAbove
        )
        self.sld_keyframe.setOrientation(horizontal)
        self.sld_keyframe.setTickPosition(ticks_above)
        self.sld_keyframe.setTickInterval(1)
        self.sld_keyframe.setMinimumHeight(_scaled(30))
        self.sld_keyframe.setObjectName("sld_keyframe")
        main_layout.addWidget(self.sld_keyframe)

        # Steps row: label | spin_steps | stretch
        steps_row = QtWidgets.QHBoxLayout()
        steps_row.setSpacing(_scaled(6))

        self.lb_steps = QtWidgets.QLabel()
        self.lb_steps.setObjectName("lb_steps")
        steps_row.addWidget(self.lb_steps)

        self.spin_steps = QtWidgets.QDoubleSpinBox()
        self.spin_steps.setDecimals(1)
        self.spin_steps.setMinimum(-10000.0)
        self.spin_steps.setMaximum(10000.0)
        self.spin_steps.setSingleStep(0.1)
        self.spin_steps.setMinimumHeight(_scaled(28))
        self.spin_steps.setMinimumWidth(_scaled(65))
        self.spin_steps.setObjectName("spin_steps")
        self.spin_steps.setValue(.5)
        steps_row.addWidget(self.spin_steps)

        steps_row.addStretch()
        main_layout.addLayout(steps_row)

        self.resize(_scaled(340), _scaled(230))
        self.setMinimumSize(QtCore.QSize(_scaled(280), _scaled(200)))

        self.globalvalue = 0
        self.is_get_time_slider_range = False
        self._undo_chunk_open = False
        self.timeline_range = self.get_timeline();
        self.retranslateUi()
        self.interact()
        

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Form", "Keyframe Offset"))
        self.btn_in.setText(_translate("Form", "In"))
        self.btn_out.setText(_translate("Form", "Out"))
        self.lb_timeline.setText(_translate("Form", "Timeline"))
        self.lb_steps.setText(_translate("Form", "Steps"))
        self.lb_offset.setText(_translate("Form", "Offset"))

    def keyframe_offset(self):
        new_value = (
            float(self.sld_keyframe.value() - self.oldvalue) * self._drag_step
        )
        previous_offset = float(self.oldvalue) * self._drag_step

        utils.keyframe_offset(
            new_value,
            self.timeline_range,
            previous_offset,
        )
        
        self.oldvalue  = self.sld_keyframe.value()

    def reset_value(self):
        try:
            self.is_get_time_slider_range = False

            if len(utils.get_selection()) > 0:
                self.globalvalue += self.sld_keyframe.value()

            self.sld_keyframe.setValue(0)
        finally:
            self._close_undo_chunk()

    def slider_pressed(self):
        self.oldvalue = self.sld_keyframe.value()
        self._drag_step = self.spin_steps.value()

        slider_range = self.get_timeline_slider()
        if slider_range is not None:
            self.is_get_time_slider_range = True
            self.timeline_range = slider_range
        else:
            self.is_get_time_slider_range = False
            self.timeline_range = [self.spin_in.value(), self.spin_out.value()]

        if not self._undo_chunk_open:
            cmds.undoInfo(openChunk=True, chunkName="Keyframe Offset")
            self._undo_chunk_open = True

    def _close_undo_chunk(self):
        if not self._undo_chunk_open:
            return

        try:
            cmds.undoInfo(closeChunk=True)
        finally:
            self._undo_chunk_open = False

    def closeEvent(self, event):
        # Avoid leaving Maya's undo queue inside an open chunk if the window is
        # closed while the slider is being dragged.
        self._close_undo_chunk()
        super(KeyframeOffsetUI, self).closeEvent(event)

    def get_timeline_slider(self):
        return utils.get_timeline_slider_range()

    def get_timeline(self):
        timeline = self.get_timeline_slider()
        
        if timeline == None:
            timeline = utils.get_timeline_range()

        return timeline 

    def update_spinners(self):
        self.spin_in.setValue(self.get_timeline()[0])
        self.spin_out.setValue(self.get_timeline()[1])

    def btn_in_clicked(self):
        self.spin_in.setValue(self.get_timeline()[0])

    def btn_out_clicked(self):
        self.spin_out.setValue(self.get_timeline()[1])

    def interact(self):
        self.oldvalue = 0
        

        self.sld_keyframe.sliderPressed.connect(self.slider_pressed)
        self.sld_keyframe.sliderMoved.connect(self.keyframe_offset)
        self.sld_keyframe.sliderReleased.connect(self.reset_value)
        self.update_spinners()

        self.btn_in.clicked.connect(self.btn_in_clicked)
        self.btn_out.clicked.connect(self.btn_out_clicked)


if __name__ == "__main__":
    KeyframeOffsetUI.run()
