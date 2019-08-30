# -*- coding: utf-8 -*-
"""
Created on Thu May 18 10:54:13 2017

@author: eschneid
https://www.tutorialspoint.com/pyqt/pyqt_database_handling.htm
"""

from PyQt5 import QtCore,  QtWidgets, QtSql

import traceback

def createConnection():
    db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
    #db.setDatabaseName(':memory:')
    db.setDatabaseName('datenbank.db')
    if not db.open():
        QtWidgets.QMessageBox.critical(None, "Cannot open database",
                "Unable to establish a database connection.\n"
                "Click Cancel to exit.",
                QtWidgets.QMessageBox.Cancel)
        return False
    else:
        return db

class Buttons():
    def __init__(self, caller):
        self.caller = caller
        self.model = caller.model
        self.view = caller.view
        self.tr = caller.tr

        addButton = QtWidgets.QPushButton(self.tr("Add"))
        submitButton = QtWidgets.QPushButton(self.tr("Save"))
        #submitButton.setDefault(True)
        revertButton = QtWidgets.QPushButton(self.tr("&Cancel"))
        delButton = QtWidgets.QPushButton(self.tr("Delete"))
        tButton = QtWidgets.QPushButton(self.tr("Test"))

        buttonBox = QtWidgets.QDialogButtonBox(QtCore.Qt.Horizontal)
        self.buttonBox = buttonBox
        buttonBox.addButton(addButton, QtWidgets.QDialogButtonBox.ActionRole)
        buttonBox.addButton(submitButton, QtWidgets.QDialogButtonBox.ActionRole)
        buttonBox.addButton(revertButton, QtWidgets.QDialogButtonBox.ActionRole)
        buttonBox.addButton(delButton, QtWidgets.QDialogButtonBox.ActionRole)
        buttonBox.addButton(tButton, QtWidgets.QDialogButtonBox.ActionRole)

        revertButton.clicked.connect(self.model.revertAll)
        submitButton.clicked.connect(self.submit)
        addButton.clicked.connect(self.addrow)
        delButton.clicked.connect(self.delrow)
        tButton.clicked.connect(lambda: self.model.removeRow(self.view.currentIndex().row()))
        tButton.hide() #Hack
        
    def addrow(self):
        try:
            self.model.insertRows(self.model.rowCount(),1)
            self.view.resizeColumnsToContents()
        except:
            traceback.print_exc()
        
    def delrow(self):
        r = QtWidgets.QMessageBox.warning(self.caller, self.tr("Delete Record"),
                    self.tr("Really Delete Record?"),
                    QtWidgets.QMessageBox.Cancel | QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Cancel)
        if r==QtWidgets.QMessageBox.Ok:
            self.model.removeRow(self.view.currentIndex().row())
            self.submit()
        
    def submit(self):
        self.model.database().transaction()
        if self.model.submitAll():
            self.model.database().commit()
            self.view.resizeColumnsToContents()
        else:
            self.model.database().rollback()
            QtWidgets.QMessageBox.warning(self.caller, "Cached Table",
                        "The database reported an error: %s" % self.model.lastError().text())

class PersonEditor(QtWidgets.QDialog):
    def __init__(self, tableName, newDB, parent=None):
        super(PersonEditor, self).__init__(parent)

        if newDB:
            self.createTable()
        
        #self.model = QtSql.QSqlTableModel(self)
        self.model = QtSql.QSqlRelationalTableModel(self)
        self.model.setTable(tableName)
        self.model.setEditStrategy(QtSql.QSqlTableModel.OnManualSubmit)
        #self.model.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)

        self.model.setRelation(3, QtSql.QSqlRelation('gender', 'id', 'name'))
        
        for c in range(self.model.columnCount()):
            self.model.setHeaderData(c, QtCore.Qt.Horizontal, self.tr(self.model.record().fieldName(c)))

        self.model.select()

        self.view = QtWidgets.QTableView()
        self.view.setModel(self.model)
        self.view.setItemDelegate(QtSql.QSqlRelationalDelegate(self.view))

        self.view.resizeColumnsToContents()

        buttons = Buttons(self)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.view)
        mainLayout.addWidget(buttons.buttonBox)
        self.setLayout(mainLayout)

    def createTable(self):
        query = QtSql.QSqlQuery()
        query.exec_("create table person(id integer primary key autoincrement, "
                                            "firstname varchar(20),"
                                            "lastname varchar(20),"
                                            "gender int check(gender in (0,1,2))"
                ")")
        query.exec_("insert into person (firstname, lastname, gender) values('Test', 'Testperson', 1)")
    
        query.exec_("create table gender(id integer primary key, "
                                            "name varchar(6) check(name in ('none','female','male'))"
                ")")
        query.exec_("insert into gender (id, name) values(0, 'none')")
        query.exec_("insert into gender (id, name) values(1, 'female')")
        query.exec_("insert into gender (id, name) values(2, 'male')")
        
class ProcessEditor(QtWidgets.QDialog):
    def __init__(self, tableName, newDB, parent=None):
        super(ProcessEditor, self).__init__(parent)
        
        if newDB:
            self.createTable()
        
        self.model = QtSql.QSqlRelationalTableModel(self)
        self.model.setTable(tableName)
        self.model.setEditStrategy(QtSql.QSqlTableModel.OnManualSubmit)
        
        self.model.setRelation(2, QtSql.QSqlRelation('measure', 'id', 'name'))
        
        for c in range(self.model.columnCount()):
            self.model.setHeaderData(c, QtCore.Qt.Horizontal, self.tr(self.model.record().fieldName(c)))
        
        self.model.select()
        
        self.view = QtWidgets.QTableView()
        self.view.setModel(self.model)
        self.view.setItemDelegate(QtSql.QSqlRelationalDelegate(self.view))
        
        self.view.resizeColumnsToContents()
        
        buttons = Buttons(self)
        
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.view)
        mainLayout.addWidget(buttons.buttonBox)
        self.setLayout(mainLayout)

    def createTable(self):
        query = QtSql.QSqlQuery()
        query.exec_("create table process(id integer primary key autoincrement, "
                                            "person int check(person > 0),"
                                            "measure int check(measure >0),"
                                            "result varchar(20)"
                ")")
        query.exec_("insert into process (person, measure, result) values(1, 1, 'None')")
        query.exec_("insert into process (person, measure, result) values(2, 1, 'None')")
    
        query.exec_("create table measure(id integer primary key autoincrement, "
                                            "name varchar(128)"
                ")")
        query.exec_("insert into measure (name) values('Sometest')")
        query.exec_("insert into measure (name) values('Othertest')")
        


class DBEditor():
    def __init__(self):
        self.db = createConnection()
        if not self.db:
            return
        self.newDB = False
        if len(self.db.tables()) == 0:
            self.newDB = True
        self.person = PersonEditor("person", self.newDB)
        self.process = ProcessEditor("process", self.newDB)

    
if __name__ == '__main__':

    class MainWindow(QtWidgets.QMainWindow):
        def __init__(self, **kwargs):
            super(MainWindow, self).__init__(**kwargs)
            self.tabs = QtWidgets.QTabWidget()
            self.setCentralWidget(self.tabs)
            
            self.editor = DBEditor()
            self.tabs.addTab(self.editor.person, self.tr('Patient'))
            self.tabs.addTab(self.editor.process, self.tr('Process'))
    
    import sys
    app = QtCore.QCoreApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    app.references = set()
    
    win = MainWindow()
    win.setWindowTitle("Test Database Editor")
    app.references.add(win)
    win.show()
    win.raise_()
    app.exec_()
