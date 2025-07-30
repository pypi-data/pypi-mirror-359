# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2020 ifm electronic gmbh
#
# THE PROGRAM IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND.
#

"""
This module provides the Configuration GUI service of the nexxT framework.
"""
import logging
import nexxT.shiboken
import nexxT.Qt
from nexxT.Qt.QtCore import (Qt, QSettings, QByteArray, QDataStream, QIODevice, QTimer)
from nexxT.Qt.QtGui import QIcon, QKeySequence, QAction
from nexxT.Qt.QtWidgets import (QTreeView, QStyle, QApplication, QFileDialog, QAbstractItemView, QMessageBox,
                               QHeaderView, QMenu, QDockWidget, QInputDialog)
from nexxT.interface import Services, FilterState
from nexxT.core.Configuration import Configuration
from nexxT.core.Application import Application
from nexxT.core.Variables import Variables
from nexxT.core.Utils import assertMainThread, MethodInvoker, mainThread, handleException
from nexxT.services.SrvConfiguration import MVCConfigurationBase, ConfigurationModel, ITEM_ROLE
from nexxT.services.gui.PropertyDelegate import PropertyDelegate
from nexxT.services.gui.GraphEditor import GraphScene
from nexxT.services.gui.GraphEditorView import GraphEditorView

logger = logging.getLogger(__name__)

class MVCConfigurationGUI(MVCConfigurationBase):
    """
    GUI implementation of MVCConfigurationBase
    """

    def __init__(self, configuration):
        super().__init__(configuration)
        assertMainThread()
        srv = Services.getService("MainWindow")
        srv.aboutToClose.connect(self._aboutToClose)
        confMenu = srv.menuBar().addMenu("&Configuration")
        toolBar = srv.getToolBar()

        configuration.configNameChanged.connect(self._configNameChanged)
        configuration.dirtyChanged.connect(self._dirtyChanged)

        style = QApplication.style()
        self.actLoad = QAction(QIcon.fromTheme("document-open", style.standardIcon(QStyle.SP_DialogOpenButton)),
                               "Open config", self)
        self.actLoad.triggered.connect(self._execLoad)
        self.actSave = QAction(QIcon.fromTheme("document-save", style.standardIcon(QStyle.SP_DialogSaveButton)),
                               "Save config", self)
        self.actSave.triggered.connect(self._execSaveConfig)
        self.actSaveWithGuiState = QAction(QIcon.fromTheme("document-save",
                                                           style.standardIcon(QStyle.SP_DialogSaveButton)),
                                           "Save config sync gui state", self)
        self.actSaveWithGuiState.triggered.connect(self._execSaveConfigWithGuiState)
        self.actNew = QAction(QIcon.fromTheme("document-new", style.standardIcon(QStyle.SP_FileIcon)),
                              "New config", self)
        self.actNew.triggered.connect(self._execNew)

        self.actReload = QAction(QIcon.fromTheme("browser-reload", style.standardIcon(QStyle.SP_BrowserReload)),
                                 "Reload python", self)
        self.actReload.setShortcut(QKeySequence(Qt.CTRL | Qt.Key_P))
        self.actReload.triggered.connect(self._execReload)

        self.actActivate = QAction(QIcon.fromTheme("arrow-up", style.standardIcon(QStyle.SP_ArrowUp)),
                                   "Initialize", self)
        self.actActivate.triggered.connect(self.activate)
        self.actActivate.setShortcut(QKeySequence(Qt.CTRL | Qt.Key_I))
        self.actDeactivate = QAction(QIcon.fromTheme("arrow-down", style.standardIcon(QStyle.SP_ArrowDown)),
                                     "Deinitialize", self)
        self.actDeactivate.setShortcut(QKeySequence(Qt.CTRL | Qt.Key_D))
        self.actDeactivate.triggered.connect(self.deactivate)

        confMenu.addAction(self.actLoad)
        confMenu.addAction(self.actSave)
        confMenu.addAction(self.actSaveWithGuiState)
        confMenu.addAction(self.actReload)
        confMenu.addAction(self.actNew)
        confMenu.addAction(self.actActivate)
        confMenu.addAction(self.actDeactivate)
        toolBar.addAction(self.actLoad)
        toolBar.addAction(self.actSave)
        toolBar.addAction(self.actReload)
        toolBar.addAction(self.actNew)
        toolBar.addAction(self.actActivate)
        toolBar.addAction(self.actDeactivate)

        self.recentConfigs = [QAction() for i in range(10)]
        self.recentConfigs[0].setShortcut(QKeySequence(Qt.CTRL | Qt.Key_R))
        confMenu.addSeparator()
        recentMenu = confMenu.addMenu("Recent")
        for a in self.recentConfigs:
            a.setVisible(False)
            a.triggered.connect(self._openRecent)
            recentMenu.addAction(a)

        self.mainWidget = srv.newDockWidget("Configuration", None, Qt.LeftDockWidgetArea)
        self.treeView = QTreeView(self.mainWidget)
        self.treeView.setHeaderHidden(False)
        self.treeView.setSelectionMode(QAbstractItemView.NoSelection)
        self.treeView.setEditTriggers(self.treeView.EditTrigger.EditKeyPressed|self.treeView.EditTrigger.AnyKeyPressed)
        self.treeView.setAllColumnsShowFocus(True)
        self.treeView.setExpandsOnDoubleClick(False)
        self.treeView.setDragEnabled(True)
        self.treeView.setDropIndicatorShown(True)
        self.treeView.setDragDropMode(QAbstractItemView.DragOnly)
        self.mainWidget.setWidget(self.treeView)
        self.treeView.setModel(self.model)
        self.treeView.header().setStretchLastSection(False)
        self.treeView.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.treeView.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self.treeView.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.treeView.doubleClicked.connect(self._onItemDoubleClicked)
        self.treeView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(self._execTreeViewContextMenu)
        # expand applications by default
        self.treeView.setExpanded(self.model.index(1, 0), True)
        self.delegate = PropertyDelegate(self.model, ITEM_ROLE, ConfigurationModel.PropertyContent, self.treeView)
        self.treeView.setItemDelegate(self.delegate)

        self.restoreState()
        srv.aboutToClose.connect(self.saveState)
        # a list of dock widgets displaying subgraphs
        self._graphViews = []
        # make sure that the graph views are closed when the config is closed
        self._configuration.subConfigRemoved.connect(self._subConfigRemoved)
        self._waitForActivated = None
        self._waitForOpenState = None

    def _execLoad(self):
        assertMainThread()
        if self._checkDirty():
            return
        fn, _ = QFileDialog.getOpenFileName(self.mainWidget, "Load configuration", self.cfgfile, filter="*.json")
        if fn is not None and fn != "":
            logger.debug("Loading config file %s", fn)
            try:
                self.loadConfig(fn)
            except Exception as e: # pylint: disable=broad-except
                logger.exception("Error while loading configuration %s: %s", fn, str(e))
                QMessageBox.warning(self.mainWidget, "Error while loading configuration", str(e))

    def _openRecent(self):
        """
        Called when the user clicks on a recent config.

        :return:
        """
        if self._checkDirty():
            return
        action = self.sender()
        fn = action.data()
        try:
            self.loadConfig(fn)
        except Exception as e: # pylint: disable=broad-except
            # catching general exception is wanted here.
            logger.exception("Error while loading configuration %s: %s", fn, str(e))
            QMessageBox.warning(self.mainWidget, "Error while loading configuration", str(e))

    def _checkDirty(self):
        if self._configuration.dirty():
            ans = QMessageBox.question(None, "Save changes?",
                                       "There are unsaved changes. Do you want to save them?",
                                       buttons=QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                                       defaultButton=QMessageBox.Save)
            if ans == QMessageBox.Save:
                self.saveConfig()
                return False
            if ans == QMessageBox.Cancel:
                return True
        return False

    def _aboutToClose(self, mainWindow):
        if self._checkDirty():
            mainWindow.ignoreCloseEvent()

    def _execNew(self):
        assertMainThread()
        if self._checkDirty():
            return
        fn, _ = QFileDialog.getSaveFileName(self.mainWidget, "New configuration", ".", filter="*.json")
        if fn is not None and fn != "":
            logger.debug("Creating config file %s", fn)
            self.newConfig(fn)

    def _execReload(self):
        self.reload()

    def _execSaveConfig(self):
        if self.configuration().filename() is None:
            self._execSaveConfigAs()
        else:
            self.saveConfig()

    def _execSaveConfigWithGuiState(self):
        if self.configuration().filename() is None:
            self._execSaveConfigAs()
        else:
            self.saveConfigWithGuiState()

    def _execSaveConfigAs(self):
        """
        Opens a file dialog to get the save file name and calls saveConfig.

        :return:
        """
        assertMainThread()
        fn, _ = QFileDialog.getSaveFileName(self.mainWidget, "Save configuration as", ".", "*.json")
        if fn is not None and fn != "":
            self.saveConfigAs(fn)

    def _addGraphView(self, subConfig):
        g = subConfig.getGraph()
        # remove already deleted graph views from internal list
        valid_graphViews = []
        for gv in self._graphViews:
            if nexxT.shiboken.isValid(gv): # pylint: disable=no-member
                valid_graphViews.append(gv)
        self._graphViews = valid_graphViews
        # check if graph view is already there
        for gv in self._graphViews:
            if gv.widget().scene().graph == g:
                logger.info("Graph view already exists.")
                return
        # create new graph view
        srv = Services.getService("MainWindow")
        graphDw = srv.newDockWidget(f"Graph ({subConfig.getName()})", parent=None,
                                    defaultArea=Qt.RightDockWidgetArea,
                                    allowedArea=Qt.RightDockWidgetArea | Qt.BottomDockWidgetArea)
        graphDw.setAttribute(Qt.WA_DeleteOnClose, True)
        assert isinstance(graphDw, QDockWidget)
        graphView = GraphEditorView(graphDw)
        graphView.setScene(GraphScene(subConfig.getGraph(), graphDw))
        graphDw.setWidget(graphView)
        self._graphViews.append(graphDw)
        graphDw.visibleChanged.connect(self._removeGraphViewFromList)

    def _subConfigRemoved(self, subConfigName, configType):
        self._subConfigRemovedImpl(subConfigName, configType)

    @handleException
    def _subConfigRemovedImpl(self, subConfigName, configType):
        g = self._configuration.subConfigByNameAndTye(subConfigName, configType).getGraph()
        if nexxT.shiboken.isValid(g):
            for gv in self._graphViews:
                if not nexxT.shiboken.isValid(gv):
                    continue
                if (not nexxT.shiboken.isValid(gv.widget()) or
                        not nexxT.shiboken.isValid(gv.widget().scene()) or
                        not nexxT.shiboken.isValid(gv.widget().scene().graph) or
                        gv.widget().scene().graph == g):
                    logger.debug("deleting graph view for subconfig %s", subConfigName)
                    gv.deleteLater()

    def _removeGraphViewFromList(self, visible):
        if visible:
            return
        gv = self.sender()
        try:
            self._graphViews.remove(gv)
            logger.debug("removed graphview from list")
        except ValueError:
            logger.debug("graphview not in list, ignored")

    def _execTreeViewContextMenu(self, point):
        index = self.treeView.indexAt(point)
        item = self.model.data(index, ITEM_ROLE)
        if isinstance(item, ConfigurationModel.SubConfigContent):
            m = QMenu()
            a1 = QAction("Edit graph")
            m.addAction(a1)
            a1.triggered.connect(lambda: self._addGraphView(item.subConfig))
            a1d5 = QAction(f"Remove {'app' if self.model.isApplication(index) else 'composite'} ...")
            a1d5.triggered.connect(lambda: self._removeSubConfig(item.subConfig))
            m.addAction(a1d5)
            if self.model.isApplication(index):
                a2 = QAction("Select Application")
                a2.triggered.connect(lambda: self.changeActiveApp(self.model.data(index, Qt.DisplayRole)))
                a3 = QAction("Init Application")
                a3.triggered.connect(lambda: self._changeActiveAppAndInit(self.model.data(index, Qt.DisplayRole)))
                m.addActions([a2, a3])
                pbsrv = Services.getService("PlaybackControl")
                m2 = m.addMenu("Init and load sequence")
                m3 = m.addMenu("Init, load and play")
                s1 = []
                s2 = []
                for a in pbsrv.recentSeqs:
                    assert isinstance(a, QAction)
                    if a.isVisible():
                        # pylint: disable=cell-var-from-loop
                        # the below statements are tested and work
                        aseq = QAction(a.text())
                        aseq.triggered.connect(lambda arg1=a.data(), seq=a.data(): self._changeActiveAppInitAndLoad(
                            self.model.data(index, Qt.DisplayRole), seq, False))
                        s1.append(aseq)
                        aseq = QAction(a.text())
                        aseq.triggered.connect(lambda arg1=a.data(), seq=a.data(): self._changeActiveAppInitAndLoad(
                            self.model.data(index, Qt.DisplayRole), seq, True))
                        # pylint: enable=cell-var-from-loop
                        s2.append(aseq)
                m2.addActions(s1)
                m3.addActions(s2)
            nexxT.Qt.call_exec(m, self.treeView.mapToGlobal(point))
            return
        if self.model.isSubConfigParent(index) == Configuration.CONFIG_TYPE_APPLICATION:
            m = QMenu()
            a = QAction("Add application")
            m.addAction(a)
            point = self.treeView.mapToGlobal(point)
            a = nexxT.Qt.call_exec(m, point)
            if a is not None:
                self._configuration.addNewApplication()
            return
        if self.model.isSubConfigParent(index) == Configuration.CONFIG_TYPE_COMPOSITE:
            m = QMenu()
            a = QAction("Add composite filter")
            m.addAction(a)
            a = nexxT.Qt.call_exec(m, self.treeView.mapToGlobal(point))
            if a is not None:
                self._configuration.addNewCompositeFilter()
            return
        if isinstance(item, Variables):
            m = QMenu()
            a = QAction("Add variable ...")
            m.addAction(a)
            a = nexxT.Qt.call_exec(m, self.treeView.mapToGlobal(point))
            if a is not None:
                vname, ok = QInputDialog.getText(
                    self.treeView, "Add Variable", "Variable Name", text="VARIABLE",
                    inputMethodHints=Qt.InputMethodHint.ImhUppercaseOnly|Qt.InputMethodHint.ImhLatinOnly)
                variables = item
                if ok and vname is not None and vname != "" and vname not in variables.keys():
                    variables[vname] = ""
            return
        if isinstance(item, ConfigurationModel.VariableContent):
            if not item.variables.isReadonly(item.name):
                m = QMenu()
                a = QAction("Remove variable")
                m.addAction(a)
                a = nexxT.Qt.call_exec(m, self.treeView.mapToGlobal(point))
                if a is not None:
                    del item.variables[item.name]
            return

    def _removeSubConfig(self, subConfig):
        ans = QMessageBox.question(self.mainWidget, "Confirm to remove",
                                   f"Do you really want to remove {subConfig.getName()}?")
        if ans is QMessageBox.StandardButton.Yes:
            try:
                self._configuration.removeSubConfig(subConfig)
            except RuntimeError as e:
                QMessageBox.warning(self.mainWidget, "Warning", f"Deletion failed: {e}")

    def _configNameChanged(self, cfgfile):
        logger.debug("_configNameChanged: %s", cfgfile)
        assertMainThread()
        self.cfgfile = cfgfile
        self._dirtyChanged(self._configuration.dirty())
        if cfgfile is not None:
            foundIdx = None
            for i, a in enumerate(self.recentConfigs):
                if a.data() == cfgfile:
                    foundIdx = i
            if foundIdx is None:
                foundIdx = len(self.recentConfigs)-1
            for i in range(foundIdx, 0, -1):
                self.recentConfigs[i].setText(self.recentConfigs[i-1].text())
                self.recentConfigs[i].setData(self.recentConfigs[i-1].data())
                self.recentConfigs[i].setVisible(self.recentConfigs[i-1].data() is not None)
            self.recentConfigs[0].setText(cfgfile)
            self.recentConfigs[0].setData(cfgfile)
            self.recentConfigs[0].setVisible(True)

    def _dirtyChanged(self, dirty):
        srv = Services.getService("MainWindow")
        if self.cfgfile is None:
            title = "nexxT: <unnamed>"
        else:
            title = "nexxT: " + self.cfgfile
        if dirty:
            title += " *"
        self.actSave.setEnabled(dirty)
        srv.setWindowTitle(title)

    def _onItemDoubleClicked(self, index):
        assertMainThread()
        if self.model.isApplication(index):
            app = self.model.data(index, Qt.DisplayRole)
            self.changeActiveApp(app)
        else:
            self.treeView.edit(index)

    def _changeActiveAppAndInit(self, app):
        """
        Call this slot to activate and init an application

        :param app: can be either an Application instance or the name of an application
        :return:
        """
        assertMainThread()
        inProcessEvents = mainThread().property("processEventsRunning")
        if inProcessEvents:
            logging.getLogger(__name__).debug(
                "_changeActiveAppAndInit waiting for inProcessEvents to be finished inProcessEvents=%s",
                inProcessEvents)
            MethodInvoker(dict(object=self, method="_changeActiveAppAndInit", thread=mainThread()),
                          Qt.QueuedConnection, app)
            return
        if isinstance(app, str):
            app = self.configuration().applicationByName(app)
        currentApp = Application.activeApplication
        if currentApp is not None:
            currentApp = currentApp.getApplication()
        self._waitForActivated = app
        self.changeActiveApp(app.getName())

    def _changeActiveAppInitAndLoad(self, app, sequence, startPlay):
        self._waitForOpenState = (app, sequence, startPlay)
        self._changeActiveAppAndInit(app)

    def appActivated(self, name, app): # pylint: disable=unused-argument
        """
        Called when the application is activated.

        :param name: the application name
        :param app: An ActiveApplication instance.
        :return:
        """
        assertMainThread()
        if app is not None:
            self.activeAppStateChange(app.getState())
            app.stateChanged.connect(self.activeAppStateChange)
            if self._waitForActivated == app.getApplication():
                MethodInvoker(self.activate, Qt.QueuedConnection)
        else:
            self.actActivate.setEnabled(False)
            self.actDeactivate.setEnabled(False)
        self._waitForActivated = None

    def _disconnectSingleShotPlay(self):
        assertMainThread()
        pbsrv = Services.getService("PlaybackControl")
        try:
            pbsrv.playbackPaused.disconnect(self._singleShotPlay)
        except (RuntimeError, AttributeError):
            # we are already disconnected.
            pass

    def _singleShotPlay(self):
        assertMainThread()
        pbsrv = Services.getService("PlaybackControl")
        MethodInvoker(pbsrv.startPlayback, Qt.QueuedConnection)
        self._disconnectSingleShotPlay()

    def activeAppStateChange(self, newState):
        """
        Called when the active application changes its state.

        :param newState: the new application's state (see FilterState)
        :return:
        """
        assertMainThread()
        logger.debug("activeAppStateChange(%s)", FilterState.state2str(newState))
        if newState == FilterState.CONSTRUCTED:
            self.actActivate.setEnabled(True)
        else:
            self.actActivate.setEnabled(False)
        if newState == FilterState.ACTIVE:
            if self._waitForOpenState is not None:
                app, pbfile, startPlay = self._waitForOpenState
                self._waitForOpenState = None
                if app == Application.activeApplication.getApplication().getName():
                    pbsrv = Services.getService("PlaybackControl")
                    if startPlay:
                        pbsrv.playbackPaused.connect(self._singleShotPlay)
                        QTimer.singleShot(2000, self._disconnectSingleShotPlay)
                    MethodInvoker(pbsrv.browser.setActive, Qt.QueuedConnection, pbfile)
            self.actDeactivate.setEnabled(True)
            self.actSaveWithGuiState.setEnabled(False)
        else:
            self.actDeactivate.setEnabled(False)
            self.actSaveWithGuiState.setEnabled(True)

    def restoreState(self):
        """
        Restore the state of the configuration gui service (namely the recently
        open config files). This is saved in QSettings because it is used
        across config files.

        :return:
        """
        logger.debug("restoring config state ...")
        settings = QSettings()
        v = settings.value("ConfigurationRecentFiles")
        if v is not None and isinstance(v, QByteArray):
            ds = QDataStream(v)
            recentFiles = ds.readQStringList()
            idx = 0
            for f in recentFiles:
                if f != "" and f is not None:
                    self.recentConfigs[idx].setData(f)
                    self.recentConfigs[idx].setText(f)
                    self.recentConfigs[idx].setVisible(True)
                    idx += 1
                    if idx >= len(self.recentConfigs):
                        break
        logger.debug("restoring config state done")

    def saveState(self):
        """
        Save the state of the configuration gui service (namely the recently
        open config files). This is saved in QSettings because it is used
        across config files.

        :return:
        """
        logger.debug("saving config state ...")
        settings = QSettings()
        b = QByteArray()
        ds = QDataStream(b, QIODevice.WriteOnly)
        l = [rc.data() for rc in self.recentConfigs if rc.isVisible() and rc.data() is not None and rc.data() != ""]
        ds.writeQStringList(l)
        settings.setValue("ConfigurationRecentFiles", b)
        logger.debug("saving config state done (%s)", l)
