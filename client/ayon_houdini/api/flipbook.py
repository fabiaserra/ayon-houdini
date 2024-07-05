import os
import logging

from qtpy import QtWidgets, QtGui
import hou

from ayon_deadline.lib import publish

from ayon_core.lib import path_tools


log = logging.getLogger(__name__)


class FlipbookDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)

        self.scene_viewer = hou.ui.paneTabOfType(hou.paneTabType.SceneViewer)

        # other properties
        self.setWindowTitle("Flipbook")

        # define general layout
        layout = QtWidgets.QVBoxLayout()
        groupLayout = QtWidgets.QVBoxLayout()

        # output toggles
        self.outputToMplay = QtWidgets.QCheckBox("MPlay Output", self)
        self.outputToMplay.setChecked(True)

        self.beautyPassOnly = QtWidgets.QCheckBox("Beauty Pass", self)
        self.useMotionblur = QtWidgets.QCheckBox("Motion Blur", self)

        # description widget
        self.descriptionLabel = QtWidgets.QLabel("Description")
        self.description = QtWidgets.QLineEdit()

        resolution = self.get_default_resolution()

        # resolution sub-widgets x
        self.resolutionX = QtWidgets.QWidget()
        resolutionXLayout = QtWidgets.QVBoxLayout()
        self.resolutionXLabel = QtWidgets.QLabel("Width")
        self.resolutionXLine = QtWidgets.QLineEdit(resolution[0])
        resolutionXLayout.addWidget(self.resolutionXLabel)
        resolutionXLayout.addWidget(self.resolutionXLine)
        self.resolutionX.setLayout(resolutionXLayout)

        # resolution sub-widgets y
        self.resolutionY = QtWidgets.QWidget()
        resolutionYLayout = QtWidgets.QVBoxLayout()
        self.resolutionYLabel = QtWidgets.QLabel("Height")
        self.resolutionYLine = QtWidgets.QLineEdit(resolution[1])
        resolutionYLayout.addWidget(self.resolutionYLabel)
        resolutionYLayout.addWidget(self.resolutionYLine)
        self.resolutionY.setLayout(resolutionYLayout)

        output_path = self.get_output_path()
        self.outputLabel = QtWidgets.QLabel(
            f"Flipbooking to: {output_path}"
        )

        # resolution group
        self.resolutionGroup = QtWidgets.QGroupBox("Resolution")
        resolutionGroupLayout = QtWidgets.QHBoxLayout()
        resolutionGroupLayout.addWidget(self.resolutionX)
        resolutionGroupLayout.addWidget(self.resolutionY)
        self.resolutionGroup.setLayout(resolutionGroupLayout)

        # frame range widget
        self.frameRange = QtWidgets.QGroupBox("Frame range")
        frameRangeGroupLayout = QtWidgets.QHBoxLayout()

        # frame range start sub-widget
        self.frameRangeStart = QtWidgets.QWidget()
        frameRangeStartLayout = QtWidgets.QVBoxLayout()
        self.frameRangeStartLabel = QtWidgets.QLabel("Start")
        self.frameRangeStartLine = QtWidgets.QLineEdit("$RFSTART")

        frameRangeStartLayout.addWidget(self.frameRangeStartLabel)
        frameRangeStartLayout.addWidget(self.frameRangeStartLine)
        self.frameRangeStart.setLayout(frameRangeStartLayout)
        frameRangeGroupLayout.addWidget(self.frameRangeStart)

        # frame range end sub-widget
        self.frameRangeEnd = QtWidgets.QWidget()
        frameRangeEndLayout = QtWidgets.QVBoxLayout()
        self.frameRangeEndLabel = QtWidgets.QLabel("End")
        self.frameRangeEndLine = QtWidgets.QLineEdit("$RFEND")

        frameRangeEndLayout.addWidget(self.frameRangeEndLabel)
        frameRangeEndLayout.addWidget(self.frameRangeEndLine)
        self.frameRangeEnd.setLayout(frameRangeEndLayout)
        frameRangeGroupLayout.addWidget(self.frameRangeEnd)

        # TODO: add support to publish framework for step size
        # # frame range step size
        # self.frameStepSize = QtWidgets.QWidget()
        # frameStepSizeLayout = QtWidgets.QVBoxLayout()
        # self.frameStepSizeLabel = QtWidgets.QLabel("Step")
        # self.frameStepSizeLine = QtWidgets.QLineEdit("1")

        # frameStepSizeLayout.addWidget(self.frameStepSizeLabel)
        # frameStepSizeLayout.addWidget(self.frameStepSizeLine)
        # self.frameStepSize.setLayout(frameStepSizeLayout)
        # frameRangeGroupLayout.addWidget(self.frameStepSize)

        self.frameRange.setLayout(frameRangeGroupLayout)

        # copy to path widget
        self.copyPathButton = QtWidgets.QPushButton("Copy Path to Clipboard")

        # options group
        self.optionsGroup = QtWidgets.QGroupBox("Flipbook options")
        groupLayout.addWidget(self.outputToMplay)
        groupLayout.addWidget(self.beautyPassOnly)
        groupLayout.addWidget(self.useMotionblur)
        groupLayout.addWidget(self.copyPathButton)
        self.optionsGroup.setLayout(groupLayout)

        # button box buttons
        self.cancelButton = QtWidgets.QPushButton("Cancel")
        self.startButton = QtWidgets.QPushButton("Start Flipbook")
        self.publishButton = QtWidgets.QPushButton("Submit to Publish")
        self.publishButton.setEnabled(
            os.path.exists(hou.expandString(output_path))
        )

        # lower right button box
        buttonBox = QtWidgets.QDialogButtonBox()
        buttonBox.addButton(self.startButton, QtWidgets.QDialogButtonBox.ActionRole)
        buttonBox.addButton(self.cancelButton, QtWidgets.QDialogButtonBox.ActionRole)
        buttonBox.addButton(self.publishButton, QtWidgets.QDialogButtonBox.ActionRole)

        # widgets additions
        layout.addWidget(self.outputLabel)
        layout.addWidget(self.descriptionLabel)
        layout.addWidget(self.description)
        layout.addWidget(self.frameRange)
        layout.addWidget(self.resolutionGroup)
        layout.addWidget(self.optionsGroup)
        layout.addWidget(buttonBox)

        # connect button functionality
        self.cancelButton.clicked.connect(self.close_window)
        self.startButton.clicked.connect(self.start_flipbook)
        self.publishButton.clicked.connect(self.submit_to_publish)
        self.copyPathButton.clicked.connect(self.copy_path_to_clipboard)
        self.description.textChanged.connect(self.update_output_path)

        # finally, set layout
        self.setLayout(layout)

    def close_window(self):
        self.close()

    def update_output_path(self):
        output_path = self.get_output_path()
        self.outputLabel.setText(f"Flipbooking to: {output_path}")
        self.publishButton.setEnabled(
            os.path.exists(hou.expandString(output_path))
        )

    # get a flipbook settings object and return with given inputs
    def get_flipbook_settings(self, input_settings):
        settings = self.scene_viewer.flipbookSettings().stash()
        log.info("Using '%s' object", settings)

        # standard settings
        settings.outputToMPlay(input_settings["mplay"])
        settings.output(input_settings["output"])
        settings.useResolution(True)
        settings.resolution(input_settings["resolution"])
        settings.cropOutMaskOverlay(True)
        settings.frameRange(input_settings["frameRange"])
        # TODO: add support for it
        # settings.frameIncrement(input_settings["frameStep"])
        settings.beautyPassOnly(input_settings["beautyPass"])
        settings.antialias(hou.flipbookAntialias.HighQuality)
        settings.sessionLabel(input_settings["sessionLabel"])
        settings.useMotionBlur(input_settings["motionBlur"])

        return settings

    def get_output_path(self, expand=False):
        description = self.description.text().replace(" ", "_")
        path = "$HIP/flipbook/$HIPNAME/flipbook{}.$F4.jpg".format(
            f"_{description}" if description else ""
        )
        if expand:
            path = hou.expandString(path)

        return path

    def get_default_resolution(self):
        cam = self.scene_viewer.curViewport().camera()
        if not cam:  # Use the main render_cam if no viewport cam
            cam = hou.node("/obj/render_cam")

        if cam:
            x = cam.parm("resx").eval()
            y = float(cam.parm("resy").eval())
            pixel_ratio = cam.parm("aspect").eval()
            return (str(x), str(int(y / pixel_ratio)))

        return ("$RESX", "$RESY")

    def start_flipbook(self):

        inputSettings = {}

        # validation of inputs
        inputSettings["frameRange"] = self.get_frame_range()
        # TODO: add support for step size
        # inputSettings["frameStep"] = int(self.frameStepSizeLine.text())
        inputSettings["resolution"] = self.get_resolution()
        inputSettings["mplay"] = self.outputToMplay.isChecked()
        inputSettings["beautyPass"] = self.beautyPassOnly.isChecked()
        inputSettings["motionBlur"] = self.useMotionblur.isChecked()

        outputPath = self.get_output_path()
        inputSettings["output"] = outputPath
        inputSettings["sessionLabel"] = outputPath

        log.info("Using the following settings, %s", inputSettings)

        base_dir = os.path.dirname(hou.expandString(outputPath))
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        # retrieve full settings object
        settings = self.get_flipbook_settings(inputSettings)

        # run the actual flipbook
        try:
            with hou.InterruptableOperation(
                "Flipbooking",
                long_operation_name="Creating a flipbook",
                open_interrupt_dialog=True,
            ) as operation:
                operation.updateLongProgress(0.25, "Starting Flipbook")
                hou.SceneViewer.flipbook(self.scene_viewer, settings=settings)
                operation.updateLongProgress(1, "Flipbook successful")
                # self.close_window()

        except Exception as e:
            log.error("Oops, something went wrong!")
            log.error(e)
            return

        self.publishButton.setEnabled(
            os.path.exists(hou.expandString(outputPath))
        )

    def submit_to_publish(self):
        output_path = self.get_output_path(expand=True)
        product_name = os.path.basename(output_path).split(".")[0]
        # Add task name suffix to product name
        product_name = f"{product_name}_{os.getenv('AYON_TASK_NAME')}"

        if not os.path.exists(output_path):
            hou.ui.displayMessage(
                f"Flipbook path {output_path} does not exist, generate it first.",
                title="Path does not exist",
                severity=hou.severityType.Error,
            )

        button_idx, values = hou.ui.readMultiInput(
            "Publish Input",
            input_labels=("Comment", "Version (optional)"),
            buttons=("Submit", "Cancel"),
            default_choice=0,
            close_choice=1,
            initial_contents=(
                "",
                path_tools.get_version_from_path(hou.hipFile.basename())
            )
        )

        if button_idx:
            return

        comment, version = values

        publish_data = {"out_colorspace": "rec709"}
        
        if comment:
            publish_data["comment"] = comment

        if version:
            publish_data["version"] = int(version)

        message, success = publish.publish_version(
            os.getenv("AYON_PROJECT_NAME"),
            os.getenv("AYON_FOLDER_PATH"),
            os.getenv("AYON_TASK_NAME"),
            "review",
            product_name,
            {"jpg": output_path},
            publish_data=publish_data,
            overwrite_version=True if values[1] else False,
        )
        if success:
            hou.ui.displayMessage(
                message,
                title="Submission successful",
                severity=hou.severityType.Message,
            )
        else:
            hou.ui.displayMessage(
                message,
                title="Submission error",
                severity=hou.severityType.Error,
            )

    # copyPathButton callback
    # copy the output path to the clipboard
    def copy_path_to_clipboard(self):
        path = self.get_output_path(expand=True)
        log.info("Copying path to clipboard: %s", path)
        QtGui.QGuiApplication.clipboard().setText(path)

    def get_frame_range(self):
        return (
            int(hou.expandString(self.frameRangeStartLine.text())),
            int(hou.expandString(self.frameRangeEndLine.text())),
        )

    def get_resolution(self):
        return (
            int(hou.expandString(self.resolutionXLine.text())),
            int(hou.expandString(self.resolutionYLine.text())),
        )


def show_dialog(parent):
    dialog = FlipbookDialog(parent)
    dialog.show()
