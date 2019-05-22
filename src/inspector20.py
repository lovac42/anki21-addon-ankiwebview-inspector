# -*- coding: utf-8 -*-
# Copyright: (c) 2019 Hikaru Y. <hkrysg@gmail.com>

# This is a modified version by lovac42 for 2.0.52 using QtWebKit


from anki.hooks import addHook
from aqt import mw
from aqt.qt import *
from PyQt4 import QtWebKit


ADDON = 'AnkiWebView Inspector'
CONTEXT_MENU_ITEM_NAME = 'Inspect'

QDOCKWIDGET_STYLE = '''
    QDockWidget::title {
        padding-top: 0;
        padding-bottom: 0;
    }
'''


class Inspector(QDockWidget):
    """
    Dockable panel with QtWebKit Developer Tools
    """

    def __init__(self, title, parent=None):
        QDockWidget.__init__(self, title, parent)
        self.setObjectName(ADDON)
        self.setAllowedAreas(
            Qt.LeftDockWidgetArea|Qt.RightDockWidgetArea|Qt.BottomDockWidgetArea)
        self.toggleViewAction().setText('Toggle Inspector')
        # make the title bar thinner
        self.setStyleSheet(QDOCKWIDGET_STYLE)
        self.web = None
        self.setup_hooks()

    def setup_hooks(self):
        # メインウィンドウ起動時にはパネルを閉じておく
        addHook('profileLoaded', self.hide)
        # プロファイル切り替え時にwebをdelete
        addHook('unloadProfile', self.delete_web)
        addHook('AnkiWebView.contextMenuEvent', self.on_context_menu_event)
        addHook('EditorWebView.contextMenuEvent', self.on_context_menu_event)
        addHook('beforeStateChange', self.on_anki_state_change)

    def on_context_menu_event(self, web, menu):
        menu.addAction(CONTEXT_MENU_ITEM_NAME, lambda: self.setup_web(web.page()))

    def setup_web(self, page):
        if self.web:
            self.web.deleteLater()
        self.web = QWebView(mw)
        self.web.setMinimumWidth(240)
        self.web.setHtml(page.mainFrame().toHtml())
        self.web.settings().setAttribute(7, True)

        inspector = QtWebKit.QWebInspector(self)
        inspector.setPage(self.web.page())
        self.setWidget(inspector)

        # make sure the panel is docked to main window when displaying
        self.setFloating(False)
        self.show()

    def on_anki_state_change(self, *_):
        """
        パネルを閉じた状態でAnkiのstateが変わったらwebをdelete
        """
        if self.isHidden():
            self.delete_web()
    
    def delete_web(self):
        if self.web:
            self.web.deleteLater()
            self.web = None





def main():
    inspector = Inspector('', mw)
    mw.addDockWidget(Qt.RightDockWidgetArea, inspector)

main()
