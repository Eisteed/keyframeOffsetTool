# Keyframe Offset Tool for Maya

A small Maya utility that offsets animation keys for selected objects in
selection order. Dragging the slider previews the offset interactively, and
each complete slider drag is stored as one Maya undo action.

## Compatibility

- Maya 2025 and newer through PySide6
- Older Maya releases that provide PySide2

## Installation

### Drag and drop

1. Download or clone this repository.
2. In Maya, drag `Drag'n Drop Install.py` into the viewport.
3. The installer creates a **Kot** button on the currently selected shelf.

### Manual installation

Place the `keyframeOffsetTool` directory in a Maya scripts directory, then run:

```python
import keyframeOffsetTool
keyframeOffsetTool.show()
```

## Usage

1. Select animated objects in the order in which they should be offset.
2. Optionally select attributes in the Channel Box.
3. Set the timeline range and offset step.
4. Drag the offset slider.

If a range is highlighted in Maya's Time Slider, that range takes precedence
over the **In** and **Out** values in the tool.

Press **Ctrl+Z** once after releasing the slider to undo the complete drag.

