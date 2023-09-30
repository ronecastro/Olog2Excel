import sys
import os
import re
from datetime import datetime
from datetime import timedelta

from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QDialogButtonBox,\
                            QVBoxLayout, QErrorMessage
from PyQt5.QtCore import QFile, Qt, QDateTime
from PyQt5.uic import loadUi

import download_logs
import vglobals
import threading
from time import sleep

class mainwindow(QMainWindow):
    def __init__(self):
        super(mainwindow, self).__init__()
        w = self.load_mainui()
        w.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint | Qt.CustomizeWindowHint)
        w.show()
        now = datetime.now()
        self._start_datetime = now + timedelta(days=-7)
        startDt = w.dtStart
        startDt.dateTimeChanged.connect(self._get_start_datetime)
        startDt.setDateTime(now + timedelta(days=-7))
        self._end_datetime = now
        endDt = w.dtEnd
        endDt.dateTimeChanged.connect(self._get_end_datetime)
        endDt.setDateTime(now)
        downloadBt = w.downloadBt
        downloadBt.released.connect(self._handle_click_downloadBt)
        filterBt = w.filterBt
        filterBt.released.connect(self._handle_click_filterBt)


    def load_mainui(self):
        ui = loadUi(os.path.join(os.path.dirname(__file__), 'mainform.ui'), self)
        return ui

    def _handle_click_downloadBt(self):
        vglobals.global_progressBarVal = 0
        startdt = self._start_datetime.toString('dd/MM/yyyy hh:mm')
        enddt = self._end_datetime.toString('dd/MM/yyyy hh:mm')
        fS = filterStruct()
        fS.update_fS()
        updateProgressBar = threading.Thread(target=self.uPB)
        updateProgressBar.daemon = True
        updateProgressBar.start()
        download_logs.downloaddata(startdt, enddt, fS)

    def _get_start_datetime(self, datetime):
        self._start_datetime = datetime

    def _get_end_datetime(self, datetime):
        self._end_datetime = datetime

    def _handle_click_filterBt(self):
        self.fdw = filterdialogwindow()

    def uPB(self):
        pb = self.progBar
        pb.setValue(0)
        # enable custom window hint
        #self.setWindowFlags(self.windowFlags() | Qt.CustomizeWindowHint)
        # disable (but not hide) close button
        #self.setWindowFlag(Qt.WindowCloseButtonHint, False)
        while pb.value() < 100:
            pb.setValue(vglobals.global_progressBarVal)
        #if vglobals.global_progressBarVal == 100:
            # pb.setStyleSheet("QProgressBar::chunk"
            #     "{"
            #     "background-color: red;"
            #     "}")
            #sleep(1)
            #self.setWindowFlag(Qt.WindowCloseButtonHint, True)
            #pb.setValue(0)

class filterdialogwindow(QDialog):
    def __init__(self):
        super(filterdialogwindow, self).__init__()
        w = self.load_filterdiagui()
        w.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint | Qt.CustomizeWindowHint)
        w.buttonBox.accepted.connect(self.btnOk)
        w.buttonBox.rejected.connect(self.btnCancel)
        w.cbID.stateChanged.connect(self.cbID_change)
        w.cbDescription.stateChanged.connect(self.cbDescription_change)
        w.cbLogbook.stateChanged.connect(self.cbLogbook_change)
        w.cbTag.stateChanged.connect(self.cbTag_change)
        w.exec()
    
    def load_filterdiagui(self):
        ui = loadUi(os.path.join(os.path.dirname(__file__), 'filterdialog.ui'), self)
        filterStruct.globals2zero(self)
        return ui

    def btnOk(self):
        filterStruct.updateGlobals(self)
        self.close()

    def btnCancel(self):
        filterStruct.dont_Filter(self)
        self.close()

    def cbID_change(self):
        if (self.cbID.isChecked()):
            self.leID.setEnabled(1)
            vglobals.global_doFilter = True
        else:
            self.leID.setDisabled(1)
    
    def cbDescription_change(self):
        if (self.cbDescription.isChecked()):
            self.leDescription.setEnabled(1)
            vglobals.global_doFilter = True
        else:
            self.leDescription.setDisabled(1)        

    def cbLogbook_change(self):
        if (self.cbLogbook.isChecked()):
            self.leLogbook.setEnabled(1)
            vglobals.global_doFilter = True
        else:
            self.leLogbook.setDisabled(1)

    def cbTag_change(self):
        if (self.cbTag.isChecked()):
            self.leTag.setEnabled(1)
            vglobals.global_doFilter = True
        else:
            self.leTag.setDisabled(1)
    
class filterStruct:
    doFilter = False
    leID =          None
    leDescription = None
    leLogbook =     None
    leTag =         None

    def do_Filter(self):
        vglobals.global_doFilter = True
        vglobals.doFilter = True

    def dont_Filter(self):
        vglobals.global_doFilter = False
        doFilter = False

    def updateGlobals(self):
        if self.cbID.isChecked():
            vglobals.global_leID =           filterStruct.list_str2list_int(\
                filterStruct.str2list(self.leID.text(), 'ID'))
        if self.cbDescription.isChecked():
            vglobals.global_leDescription =  filterStruct.list_item_split(\
                filterStruct.str2list(self.leDescription.text(), 'Description'))
        if self.cbLogbook.isChecked():
            vglobals.global_leLogbook =      filterStruct.list_item_split(\
                filterStruct.str2list(self.leLogbook.text(), 'Logbook'))
        if self.cbTag.isChecked():
            vglobals.global_leTag =          filterStruct.list_item_split(\
                filterStruct.str2list(self.leTag.text(), 'Tag'))
    
    def globals2zero(self):
        vglobals.global_doFilter = False
        vglobals.global_leID = ''
        vglobals.global_leDescription = ''
        vglobals.global_leLogbook = ''
        vglobals.global_leTag = ''
        vglobals.global_progressBarVal = 0

    def update_fS(self):
        self.leID =          vglobals.global_leID
        self.leDescription = vglobals.global_leDescription
        self.leLogbook =     vglobals.global_leLogbook
        self.leTag =         vglobals.global_leTag
        self.doFilter =      vglobals.global_doFilter

    def str2list(s, field):
        try:
            if field == 'ID':
                delimiters = "-",",","/"," "
                regexPattern = '|'.join(map(re.escape, delimiters))
                lista = re.split(regexPattern, s)
            else:
                delimiters = ",","/"
                regexPattern = '|'.join(map(re.escape, delimiters))
                lista = re.split(regexPattern, s)

        except:
            if field == 'ID':
                error_dialog = QErrorMessage()
                error_dialog.showMessage("Filter not recognised! Use hyphen, \
                    comma, slash or a blank space between items.")
                error_dialog.setWindowTitle("Error")
                error_dialog.exec_()
            else:
                error_dialog = QErrorMessage()
                error_dialog.showMessage("Filter not recognised! Use comma or \
                    slash between items.")
                error_dialog.setWindowTitle("Error")
                error_dialog.exec_()

            return
        return lista

    def list_str2list_int(lista):
        for i in range(len(lista)):
            try:
                lista[i] = int(lista[i].strip())
            except:
                error_dialog = QErrorMessage()
                error_dialog.showMessage('ID filter must be a interval of \
                    integer numbers!')
                error_dialog.setWindowTitle("Error")
                error_dialog.exec_()
                return
        return lista

    def list_item_split(lista):
        for i in range(len(lista)):
            lista[i] = lista[i].strip()
        return lista
        

if __name__ == "__main__":
    app = QApplication([])
    widget = mainwindow()
    sys.exit(app.exec_())