import maya.cmds as cmds
import maya.mel as mel

def get_timeline_range():
    start_timeline = cmds.playbackOptions(query = True, min = True)
    end_timeline = cmds.playbackOptions(query = True, max = True)
    return [start_timeline, end_timeline]

def get_channelbox_attributes():
    channelBox = mel.eval('global string $gChannelBoxName; $temp=$gChannelBoxName;')    #fetch maya's main channelbox
    attrs = cmds.channelBox(channelBox, q=True, sma=True)

    return attrs

def get_timeline_slider_range():
    aPlayBackSliderPython = mel.eval('$tmpVar=$gPlayBackSlider')

    if cmds.timeControl(aPlayBackSliderPython, query = True, rangeVisible = True):
        time_slider_range = cmds.timeControl(aPlayBackSliderPython, query = True, rangeArray = True)
        timeline_range =  list(time_slider_range)
        return timeline_range
    return None

def get_selection():
    selection = cmds.ls(sl = True)

    #return the list of objects
    return selection

def keyframe_offset(value, timeline_range, previous_offset=0.0):
    """Offset each selected object's keys in time by selection order."""
    selection = get_selection()
    attributes = get_channelbox_attributes()

    for obj_index, obj in enumerate(selection, start=1):
        previous_object_offset = obj_index * previous_offset
        current_range = (
            timeline_range[0] + previous_object_offset,
            timeline_range[1] + previous_object_offset,
        )
        edit_args = {
            "edit": True,
            "relative": True,
            "time": current_range,
            "timeChange": obj_index * value,
        }

        if attributes:
            cmds.keyframe(
                obj,
                attribute=attributes,
                **edit_args
            )
        else:
            cmds.keyframe(obj, **edit_args)
