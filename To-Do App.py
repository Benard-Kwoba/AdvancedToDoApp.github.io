# ______________________________________________ ADVANCED TO-DO LIST: VERSION 1.1 _____________________________________
import sys
import sqlite3 as sql # we will use database storage in later versions
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QListWidget,
                             QLabel, QAbstractItemView, QToolTip, QMenu, QMessageBox, QAction, QColorDialog,
                             QListWidgetItem, QTableWidget, QTableWidgetItem, QFrame, QProgressBar, QTreeView, QComboBox,
                             QHeaderView, QDateEdit, QStyledItemDelegate, QTextEdit, QCalendarWidget, QTabWidget)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QTime, QDateTime, QDate
from PyQt5.QtGui import QIcon, QKeyEvent, QBrush, QColor, QPixmap
import datetime
import json
import matplotlib.pyplot as plt
from io import BytesIO
# Creating a custom line edit class:  subclassing a widget
class CustomLineEdit(QLineEdit):
    def __init__(self, parent=None):  # constructor method for the CustomLineEdit class, default parent widget: None
        super().__init__(parent)  # calls the constructor of the superclass (i.e., the parent class) of CustomLineEdit.
        # super(): returns a proxy object that allows you to call methods of the superclass

    def keyPressEvent(self, event):
        # Handling the key press event for Escape key
        if event.key() == Qt.Key_Escape:
            self.clear()  # Clear the text when Escape key is pressed
        else:
            super().keyPressEvent(event)
class ReadOnlyDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        return None  #  By returning None, we effectively prevent any editor from being created for the cell.

class ShiftScheduleApp(QWidget):
    global dark_mode_requested
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("AGL🌍 Shift Schedule".upper())
        self.setStyleSheet('background-color: #05161a;')
        self.setWindowIcon(QIcon("agl_shifts_icon.png"))
        self.resize(400, 200)

        # Create layout
        layout = QVBoxLayout()

        # Create date label
        self.date_label = QLabel("Select a Date".upper())
        self.date_label.setStyleSheet("""
            background-color: #000; 
            color: #ccc; 
            padding-left: 120px; 
            padding-top: 5px;
            border: 1px solid #c1e8ff; 
            padding-bottom: 5px;
            """)
        layout.addWidget(self.date_label)

        # Create calendar widget
        self.calendar = QCalendarWidget()
        self.calendar.setStyleSheet('background-color: #6da5c0;')
        self.calendar.setSelectedDate(QDate.currentDate())
        self.calendar.selectionChanged.connect(self.update_output)  # Connect signal to update_output method
        layout.addWidget(self.calendar)

        # Create output label
        self.output_label = QLabel("")
        self.output_label.setStyleSheet("""
            background-color: #000; 
            padding-left: 120px; 
            padding-top: 5px; 
            padding-bottom: 5px; 
            border: 1px solid #c1e8ff; 
            color: yellow;
            """)
        layout.addWidget(self.output_label)

        self.setLayout(layout)
        self.update_output()

    def update_output(self):
        selected_date = self.calendar.selectedDate()
        shifts = self.get_shift(selected_date)
        self.output_label.setText("\n".join(shifts))
        self.update_date_label(selected_date)

    def update_date_label(self, selected_date):
        if selected_date.isValid():
            self.date_label.setText(f"Selected date\n".upper() + f"{selected_date.toString('dd MMMM yyyy')}")
        else:
            self.date_label.setText("Select a Date")

    def get_shift(self, selected_date):
        shifts = ['A', 'B', 'C']
        shift_day_types = []
        start_date = QDate(2024, 4, 30)
        days_since_start = start_date.daysTo(selected_date)  # Calculate days since start date
        for shift in shifts:
            shift_index = shifts.index(shift)
            day_type_index = (days_since_start + shift_index * 2) % 6
            day_type = ['DAY\t☀', 'NIGHT\t🌙', 'OFF\t🍕'][day_type_index // 2]  # Each type repeats every 2 days
            shift_day_types.append(f"{shift}: {day_type}")
        return shift_day_types


class Performance_Window(QFrame):
    global dark_mode_requested
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Your Performance")
        self.resize(800, 700)
        self.performance_initUI()
        self.setWindowIcon(QIcon('todo_performance_trend-img.ico'))  # convert to .ico file if image is not showing

    def performance_initUI(self):
        # Create a QVBoxLayout to hold the widgets
        layout = QVBoxLayout()

        # Add a QTableWidget
        # Add a QTableWidget to the layout
        self.table_widget = QTableWidget()  # or you can explicitly set rows and columns e.g QTableWidget(12, 7)
        self.reference_label = QLabel()
        self.save_button = QPushButton('Save')
        self.save_button.setToolTip('Save Changes')


        self.save_button.setStyleSheet('''
            QPushButton {
                background-color: #000; color: white; border: 2px solid greenyellow; border-radius: 10px;
            }
            QPushButton::hover {
                background-color: green; color: white
            }
        ''')
        self.save_button.setFixedSize(50, 30)
        self.refresh_button = QPushButton('Refresh')

        self.table_widget.setRowCount(12)  # Assuming 7 days in a week
        self.table_widget.setColumnCount(7)  # Two columns: Day and Percentage Completed

        # Set headers for the table; try for table_widget.verticalHeader()
        table_headers = ["Pending\nTasks", "Completion\nDeadline", "Days\nRemaining",
                                                "Completed\nTasks", "Task\nType", "Task\nPriority", "Your\nComments"]
        self.table_widget.setHorizontalHeaderLabels(table_headers)
        self.table_widget.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # for columns to stretch out
        self.table_widget.horizontalHeader().setHighlightSections(True)
        self.table_widget.horizontalHeader().setSectionsClickable(True)
        self.table_widget.cellClicked.connect(self.on_cell_clicked)
        self.table_widget.cellPressed.connect(self.on_cell_pressed)
        self.table_widget.cellActivated.connect(self.on_cell_activated)
        self.save_button.clicked.connect(self.save_changes)

        """
        # How to merge cells
        num_rows = self.table_widget.rowCount()

        # Merge cells in the success rate column (assuming it's the 3rd column, index 2)
        self.table_widget.setSpan(0, 4, num_rows, 1)
        """
        self.populate_table()

        # set background colors for days remaining for existing data before populating
        for i in range(self.table_widget.rowCount()):
            item = self.table_widget.item(i, 2)
            if item:
                value = int(item.text())
                if value < 0:
                    item.setBackground(QColor('red'))
                elif value == 0:
                    item.setBackground(QColor('green'))
                else:
                    item.setBackground(QColor('yellow'))
        # Set header background color, text color, and font properties
        header = self.table_widget.horizontalHeader()
        header.setStyleSheet("""
            QHeaderView::section { 
                background-color: green; color:white; font-weight: bold; 
            }
            """)
        if dark_mode_requested:
            header.setStyleSheet("""
                QHeaderView::section { 
                    background-color: #0077b6; color:white; font-weight: bold; 
                }
            """)
        # Set vertical header background color, text color, and font properties
        vertical_header = self.table_widget.verticalHeader()
        vertical_header.setStyleSheet("""
                    QHeaderView::section { 
                        background-color: #3c3c3c; 
                        color: white; 
                        font-weight: bold; 
                    }
                """)
        # Set cell background color, text color, and font properties
        self.table_widget.setStyleSheet("""
                    QTableWidget { 
                        background-color: #edfbff; 
                        color: black;
                    }
                """)
        if dark_mode_requested:
            self.setStyleSheet("""
                QFrame { background-color: #021024;}
            """)
            self.table_widget.setStyleSheet("""
                QTableWidget { 
                    background-color: #a3aabe; 
                    color: black;
                }
            """)
        pending_tasks = TodoApp().pending_tasks
        completed_tasks = TodoApp().completed_tasks
        recyclebin_tasks = Recycle_Bin_Window().recycle_bin_tasks

        layout.addWidget(self.table_widget)
        layout.addWidget(self.reference_label)
        layout.addWidget(self.save_button)

        # Add a QTreeView: For Visualization of success rate
        self.tab_widget = QTabWidget()
        # Add tabs
        self.pending_tasks_tab = QWidget()
        self.completed_tasks_tab = QWidget()
        self.recycled_items_tab = QWidget()
        self.analytics_tab = QWidget()

        self.tab_widget.addTab(self.pending_tasks_tab, "Pending Tasks")
        self.tab_widget.addTab(self.completed_tasks_tab, "Completed Tasks")
        self.tab_widget.addTab(self.recycled_items_tab, "Recycle Bin Tasks")
        self.tab_widget.addTab(self.analytics_tab, "Analytics")
        self.tab_widget.setCurrentWidget(self.analytics_tab)

        # Create layouts for each tab
        pending_tasks_layout = QVBoxLayout()
        completed_tasks_layout = QVBoxLayout()
        recycled_items_layout = QVBoxLayout()
        analytics_layout = QVBoxLayout()

        # Add widgets to tab layouts
        # Display pending tasks in the "Pending Tasks" tab
        pending_tasks_label = QLabel()
        pending_tasks_text = "\n".join(pending_tasks)  # Convert the list of tasks to a string with line breaks
        pending_tasks_label.setText(pending_tasks_text)
        pending_tasks_layout.addWidget(pending_tasks_label)

        completed_tasks_label = QLabel()
        completed_tasks_text = "\n".join(completed_tasks)  # Convert the list of tasks to a string with line breaks
        completed_tasks_label.setText(completed_tasks_text)
        completed_tasks_layout.addWidget(completed_tasks_label)

        recyclebin_label = QLabel()
        recyclebin_text = "\n".join(recyclebin_tasks)  # Convert the list of tasks to a string with line breaks
        recyclebin_label.setText(recyclebin_text)
        recycled_items_layout.addWidget(recyclebin_label)

        # analytics label
        analytics_label = QLabel('')
        analytics_layout.addWidget(analytics_label)
        # Calculate percentages for each component
        total_tasks = len(pending_tasks) + len(completed_tasks) + len(recyclebin_tasks)
        pending_percentage = (len(pending_tasks) / total_tasks) * 100
        completed_percentage = (len(completed_tasks) / total_tasks) * 100
        recycled_percentage = (len(recyclebin_tasks) / total_tasks) * 100

        # Create bar chart
        labels = ['Pending', 'Completed', 'Recycled']
        percentages = [pending_percentage, completed_percentage, recycled_percentage]
        colors = ['#FCF55F', 'green', '#465362']

        plt.figure(figsize=(4, 3), facecolor='#f2f2f2')  # Set figure size
        plt.bar(labels, percentages, color=colors)
        plt.ylabel('Percentage')
        plt.title('Task Distribution')

        # Convert the Matplotlib figure to a QPixmap
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        pixmap = QPixmap()
        pixmap.loadFromData(buffer.getvalue())
        buffer.close()

        # Set the QPixmap to the QLabel
        analytics_label.setPixmap(pixmap)
        analytics_label.setScaledContents(True)  # Scale contents to fit the label

        # Set layouts for each tab
        self.pending_tasks_tab.setLayout(pending_tasks_layout)
        self.completed_tasks_tab.setLayout(completed_tasks_layout)
        self.recycled_items_tab.setLayout(recycled_items_layout)
        self.analytics_tab.setLayout(analytics_layout)

        self.tab_widget.setStyleSheet("""
            QTabBar::tab:selected {
                background-color: #468faf; color: #ccc;
            }
            QTabBar::tab {
                background-color: #000; color: #ccc;
            }
            QTabBar {color: #fff;}

        """)
        completed_tasks_label.setStyleSheet("background-color: green;padding:10px;color: #fff;")
        pending_tasks_label.setStyleSheet('background-color: #FCF55F; color: #000;padding:10px;')
        recyclebin_label.setStyleSheet('background-color: #465362; color: #fff;padding:10px;')
        analytics_label.setStyleSheet('background-color: #000; color: #fff;padding:10px;')

        layout.addWidget(self.tab_widget)

        # Add a QProgressBar
        progress_bar = QProgressBar()
        layout.addWidget(progress_bar)
        # Set the layout for the QFrame
        self.setLayout(layout)

    def on_cell_clicked(self, row, column):
        reference_text = f"Selected Cell: ({row + 1}, {column + 1})"
        self.reference_label.setText(reference_text)
        if dark_mode_requested:
            self.reference_label.setStyleSheet('color: white;')
    def on_cell_pressed(self, row, column):
        global dark_mode_requested
        if column == 0 or column == 2 or column == 3:
            # Show a popup indicating that the field is not editable
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Not Editable")
            msg_box.setText("This Field is ReadOnly!")
            msg_box.show()
            timer = QTimer(self)
            timer.singleShot(800, msg_box.close)
            if dark_mode_requested:
                msg_box.setStyleSheet('background-color: white;')

    def save_changes(self):
        todo_completed_items = TodoApp().completed_tasks
        self.task_data = []

        for row in range(self.table_widget.rowCount()):
            task_name_item = self.table_widget.item(row, 0)
            deadline_item = self.table_widget.cellWidget(row, 1)
            task_type_combo = self.table_widget.cellWidget(row, 4)
            task_priority_combo = self.table_widget.cellWidget(row, 5)
            user_comment_widget = self.table_widget.cellWidget(row, 6)
            if task_name_item and deadline_item:
                task_name = task_name_item.text()
                deadline = deadline_item.date().toString(Qt.ISODate)
                task_type = task_type_combo.currentText()
                task_priority = task_priority_combo.currentText()
                user_comment = user_comment_widget.toPlainText()
                # Check if the task name is not in the completed column (column 3)
                if task_name not in todo_completed_items:
                    # Task not in completed list, add it to task data
                    self.task_data.append({"task_name": task_name,
                                           "deadline": deadline,
                                           "task_type": task_type,
                                           "task_priority": task_priority,
                                           "user_comment": user_comment
                                           })

        with open("user_performance.json", "w") as f:
            json.dump(self.task_data, f, indent=4)
        self.populate_table()
        for i in range(self.table_widget.rowCount()):
            item = self.table_widget.item(i, 2)
            if item:
                value = int(item.text())
                if value < 0:
                    item.setBackground(QColor('red'))
                elif value == 0:
                    item.setBackground(QColor('green'))
                else:
                    item.setBackground(QColor('yellow'))

    def on_cell_activated(self, row, column, event: QKeyEvent):  # specifying the type of parameter is optional
        # Get the item at the clicked cell
        item = self.table_widget.item(row, column)
        if item is not None:
            modifiers = QApplication.keyboardModifiers()
            if event.key() == Qt.Key_Delete:
                self.table_widget.setItem(row, column, QTableWidgetItem())
                event.accept()  # it accepts the event to indicate that it has been processed.

    # overiding keypress event to allow for deletion of ALL SELECTED ITEMS in the window
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Delete:
            selected_items = self.table_widget.selectedItems()
            for item in selected_items:
                item.setText("")
            event.accept()

    def populate_table(self):
        # Load data from the JSON file
        with open("user_performance.json", "r") as file:
            self.task_data = json.load(file)

        # Get pending tasks from todoapp.pending_tasks
        pending_tasks = TodoApp().pending_tasks
        completed_tasks = TodoApp().completed_tasks

        # Add pending tasks to JSON file with today's date if they don't exist
        for task in pending_tasks:
            if not any(item["task_name"] == task for item in self.task_data):
                self.task_data.append({"task_name": task,
                                       "deadline": QDate.currentDate().toString(Qt.ISODate)
                                       })
        # Iterate over a copy of the task_data list to safely remove items during iteration
        for item in self.task_data.copy():
            # If the task name in the item is not in the pending_tasks list
            if item["task_name"] not in pending_tasks:
                # Remove the item from the task_data list
                self.task_data.remove(item)
        for c_row, c_task_data in enumerate(completed_tasks):
            c_item = QTableWidgetItem(str(c_task_data))
            self.table_widget.setItem(c_row, 3, c_item)
            c_item.setBackground(QColor('green'))
            c_item.setForeground(QColor('#ccc'))
        # Populate table with data from JSON file
        for row, task_info in enumerate(self.task_data):
            task_name = task_info["task_name"]
            deadline = task_info["deadline"]
            task_type = task_info.get("task_type", "Other")  # Get task type or default to "Other"
            task_priority = task_info.get("task_priority", "Average")  # Get task priority or default to "Average"
            user_comment = task_info.get("user_comment", "")  # Get user comment or default to empty string

            # Add task name to the table
            p_item = QTableWidgetItem(task_name)
            self.table_widget.setItem(row, 0, p_item)
            p_item.setForeground(QColor('#ccc'))
            p_item.setBackground(QColor('#000'))

            # Add completion deadline to the table
            date_edit = QDateEdit()
            date_edit.setStyleSheet('background-color: #ccc;')
            deadline_date = QDate.fromString(deadline, Qt.ISODate)
            date_edit.setDate(deadline_date)
            date_edit.setCalendarPopup(True)
            if dark_mode_requested:
                date_edit.setStyleSheet('background-color: #ccc')
            date_edit.dateChanged.connect(lambda date, row=row: self.update_days_remaining(date, row))
            self.table_widget.setCellWidget(row, 1, date_edit)  # Column 1 corresponds to "Completion Deadline"
            # Set task type and task priority in the respective comboboxes
            task_type_combo = QComboBox()
            task_type_combo.setStyleSheet('background-color: #ccc;')
            task_type_combo.addItems(["Work", "Business", "Leisure", "Programming", "Other"])
            task_type_combo.setCurrentText(task_type)
            if dark_mode_requested:
                task_type_combo.setStyleSheet('background-color: #ccc;')
            self.table_widget.setCellWidget(row, 4, task_type_combo)

            task_priority_combo = QComboBox()
            task_priority_combo.addItems(["High", "Medium", "Low", "Average"])
            task_priority_combo.setCurrentText(task_priority)
            task_priority_combo.setStyleSheet('background-color: #ccc;')
            self.table_widget.setCellWidget(row, 5, task_priority_combo)

            # Set user comment in the QTextEdit widget
            user_comment_widget = QTextEdit()
            user_comment_widget.setPlainText(user_comment)
            user_comment_widget.setStyleSheet('background-color: #ccc;')
            self.table_widget.setCellWidget(row, 6, user_comment_widget)
            # Calculate days remaining
            days_remaining = QDate.currentDate().daysTo(deadline_date)
            # Set the days remaining in the "Days Remaining" column
            days_remaining_item = QTableWidgetItem(str(days_remaining))
            self.table_widget.setItem(row, 2, days_remaining_item)  # Column 2 corresponds to "Days Remaining"

        # Set items in the "Pending Tasks" column uneditable
        delegate = ReadOnlyDelegate()
        # Columns for which you want to set the delegate
        columns = [0, 2, 3]  # Replace with the column indices you want

        # Set the delegate for each column
        for column in columns:
            self.table_widget.setItemDelegateForColumn(column, delegate)
    def update_days_remaining(self, date, row):
        deadline = date
        days_remaining = QDate.currentDate().daysTo(deadline)
        days_remaining_item = QTableWidgetItem(str(days_remaining))
        self.table_widget.setItem(row, 2, days_remaining_item)
        # Style the background color based on the value of days_remaining)
        if days_remaining < 0:
            days_remaining_item.setBackground(QColor("red"))
        else:
            days_remaining_item.setBackground(QColor("yellow"))

    def calculate_success_rate(self):
        todo_pending_tasks = TodoApp().pending_tasks
        todo_completed_tasks = TodoApp().completed_tasks
        # Get the number of pending tasks
        num_pending_tasks = len(self.todo_pending_tasks)

        # Get the number of completed tasks
        num_completed_tasks = len(self.todo_completed_tasks)

        # Calculate the success rate
        if num_pending_tasks == 0:
            success_rate = 100  # All pending tasks are completed
        else:
            success_rate = (num_completed_tasks / num_pending_tasks) * 100

        return success_rate


class Recycle_Bin_Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #000;")
        self.setWindowTitle("Recycle Bin")
        self.resize(280, 400)
        self.setWindowIcon(QIcon("to-do-list recycle bin.ico"))
        self.recycle_bin_tasks = []
        self.recycle_bin_label = QLabel('RECYCLED ITEMS')
        self.recycle_bin_listbox = QListWidget()
        self.recycle_bin_listbox.setSelectionMode(QAbstractItemView.ExtendedSelection)  # see MultipleSelection
        self.recycle_bin_listbox.setToolTip('-Use CTRL + Selection to Select Item(s)')
        self.restore_button = QPushButton("Restore to Completed Tasks")
        self.restore_button.clicked.connect(self.restore_tasks)
        self.permanent_deletion_button = QPushButton("Permanently Delete Item")
        self.permanent_deletion_button.setToolTip('Note, this action is irreversible!')
        self.permanent_deletion_button.clicked.connect(self.permanent_deletion)
        self.recycle_bin_initUI()
        # stylesheets
        self.recycle_bin_label.setStyleSheet("""
            QLabel {
                background-color: #ffcc00;
                padding: 5px;
                color: black;
                font-weight:bold;
                justify-content: center;
            }
        """)
        self.recycle_bin_listbox.setStyleSheet("""
            QListWidget {
            background-color: #000; padding-left: 3px; padding-top: 1px;
            color: white; 
            background-image: url('to-do-list recycle bin background-img.jpg');
            }
            QListWidget::item:selected {
                background-color: black;
            }
        """)
        self.restore_button.setStyleSheet("""
            QPushButton {
                background-color: #ccc;
                border: 2px solid #4CAF50;
                border-radius: 10px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: green;
                color: white;

            }
        """)
        self.permanent_deletion_button.setStyleSheet("""
            QPushButton {
                background-color: #ccc;
                border: 2px solid #4CAF50;
                border-radius: 10px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #ff0000;
                color: white;

            }
        """)
        self.load_recycle_bin_items()
    def recycle_bin_initUI(self):
        # Create a QVBoxLayout to hold the widgets
        layout = QVBoxLayout()

        layout.addWidget(self.recycle_bin_label)
        layout.addWidget(self.recycle_bin_listbox)
        layout.addWidget(self.restore_button)
        layout.addWidget(self.permanent_deletion_button)
        self.setLayout(layout)

    def load_recycle_bin_items(self):
        try:
            with open("PyQt5_tasks_recycle_bin.txt", "r") as file:
                lines = file.readlines()
                self.recycle_bin_tasks = []
                for line in lines:
                    line = line.strip()
                    self.recycle_bin_tasks.append(line)

                self.update_recycle_bin_listbox()

        except FileNotFoundError:
            return 'PyQt5_tasks_recycle_bin.txt is missing'


    def update_recycle_bin_listbox(self):
        self.recycle_bin_listbox.clear()
        for task in self.recycle_bin_tasks:
            self.recycle_bin_listbox.addItem(task)
        self.save_recycled_items()

    def save_recycled_items(self):
        with open("PyQt5_tasks_recycle_bin.txt", "w") as file:
            for task in self.recycle_bin_tasks:
                file.write(task + "\n")

    def restore_tasks(self):
        selected_tasks_indexes = self.recycle_bin_listbox.selectedIndexes()
        selected_tasks_indexes.sort(reverse=True,
                                    key=lambda x: x.row())  # Reverse sorting to avoid issues when removing items
        todo_instance = TodoApp()  # Instantiate the TodoApp
        for index in selected_tasks_indexes:
            selected_task_index = index.row()
            restored_task = self.recycle_bin_tasks.pop(selected_task_index)

            if (restored_task not in todo_instance.completed_tasks) and (
                    restored_task not in todo_instance.pending_tasks):
                todo_instance.completed_tasks.append(restored_task)
            # Save the updated tasks
            todo_instance.save_tasks()
            self.update_recycle_bin_listbox()


    def permanent_deletion(self):
        selected_items = self.recycle_bin_listbox.selectedItems()
        for item in selected_items:
            self.recycle_bin_tasks.remove(item.text())
            self.recycle_bin_listbox.takeItem(self.recycle_bin_listbox.row(item))
        self.save_recycled_items()

dark_mode_requested = False
class TodoApp(QWidget):
    # define custom signals if any; i.e class variables
    closed = pyqtSignal()  # closed signal is defined as a class-level attribute
    allTasksCompleted = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # define instance variables
        self.setWindowTitle("To Do List App")
        self.setWindowIcon(QIcon("todo_icon.ico"))
        self.resize(900, 700)  # see self.setGeometry(600, 600, 400, 300)
        self.pending_tasks = []
        self.completed_tasks = []

        # Create layouts
        main_layout = QHBoxLayout(
            self)  # creates a QHBoxLayout instance named main_layout, setting self (the TodoApp instance) as its parent widget.
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()
        performance_layout = QVBoxLayout()

        # Left Frame
        left_label = QLabel("PENDING TASKS")
        self.pending_tasks_listbox = QListWidget()
        self.pending_tasks_listbox.setSelectionMode(QAbstractItemView.ExtendedSelection)  # see MultipleSelection
        self.pending_tasks_listbox.keyPressEvent = self.pending_tasks_keypress
        self.pending_tasks_listbox.setToolTip('-Use Delete Key or Ctrl + D\non Selection(s) To Delete\nan item(s)' \
                                              '\n-Double click to copy')
        self.pending_tasks_listbox.setContextMenuPolicy(Qt.CustomContextMenu)
        self.pending_tasks_listbox.customContextMenuRequested.connect(self.pendingTasksContextMenu)
        self.pending_tasks_listbox.itemDoubleClicked.connect(self.pending_task_doubleclickToCopy)
        self.pending_tasks_listbox.setDragEnabled(True)
        self.pending_tasks_listbox.setAcceptDrops(True)
        self.pending_tasks_listbox.viewport().installEventFilter(self)

        self.task_entry = CustomLineEdit()
        self.task_entry.setEchoMode(0)  # 2 for password entries
        self.task_entry.setPlaceholderText("ADD TASK")
        self.task_entry.setToolTip(
            "Press ESC key to reset entry\nOnce Done Click\n'Add a Task' Button Or Press Enter Key")
        self.task_entry.returnPressed.connect(self.add_tasks)

        add_task_button = QPushButton("Add a Task")  # add_task_button.setText('Add a Task')
        add_task_button.clicked.connect(self.add_tasks)
        complete_task_button = QPushButton("Mark selected task(s) as completed")
        complete_task_button.clicked.connect(self.complete_task)

        left_layout.addWidget(left_label)
        left_layout.addWidget(self.pending_tasks_listbox)
        left_layout.addWidget(self.task_entry)
        left_layout.addWidget(add_task_button)
        left_layout.addWidget(complete_task_button)

        # right pane
        right_label = QLabel("COMPLETED TASKS")
        self.completed_tasks_listbox = QListWidget()
        self.completed_tasks_listbox.setToolTip('Use CTRL+Selection\nfor multiple item selection')
        self.completed_tasks_listbox.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.completed_tasks_listbox.setDragEnabled(True)
        self.completed_tasks_listbox.setAcceptDrops(True)  # Enable dropping here
        self.completed_tasks_listbox.viewport().installEventFilter(self)

        clear_completed_task_button = QPushButton("Clear all completed tasks")
        clear_completed_task_button.setToolTip('Clear all tasks')
        clear_completed_task_button.clicked.connect(self.clear_completed_tasks)
        clear_a_completed_task_button = QPushButton("Clear selected completed task(s)")
        clear_a_completed_task_button.clicked.connect(self.clear_a_completed_task)

        right_layout.addWidget(right_label)
        right_layout.addWidget(self.completed_tasks_listbox)
        right_layout.addWidget(clear_a_completed_task_button)
        right_layout.addWidget(clear_completed_task_button)

        # progress pane
        # Create mode selection with combo box
        self.agl_shifts_button = QPushButton('AGL Shifts')
        self.agl_shifts_button.setStyleSheet("""
            QPushButton {background-color: #29343d; color: #ccc;}
            QPushButton::hover {background-color: green;}
        """)
        self.agl_shifts_button.clicked.connect(self.agl_shiftScheduler)
        self.mode_combo = QComboBox()  # Create a combo box for selecting mode
        self.mode_combo.addItems(["Dark Mode", "Light Mode"])  # Add mode options
        self.mode_combo.setStyleSheet('background-color: #f2f2f2;')
        self.mode_combo.setCurrentIndex(1)
        self.mode_combo.currentIndexChanged.connect(self.change_mode)  # Connect signal to mode change method
        self.refresh_button = QPushButton('Refresh')
        self.refresh_button.clicked.connect(self.refresh)
        self.refresh_button.setIcon(QIcon('todo_refresh.ico'))
        self.current_time_button = QPushButton()
        self.current_time_button.setStyleSheet("text-align: left; background-color: #f2f2f2;")
        # Create a QTimer to update the current time button every second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time_button)
        self.timer.start(1000)  # Update every 1000 milliseconds (1 second)
        # Variable to keep track of elapsed time in seconds
        self.elapsed_time_seconds = 0
        self.update_time_button()
        self.performance_button = QPushButton('Your Performance')
        self.performance_button.clicked.connect(self.progress_window)
        self.recycle_bin_button = QPushButton('Recycle Bin')
        self.recycle_bin_button.clicked.connect(self.open_recycle_bin_window)
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: black;
                color: white;
                letter-spacing: 1px; font-family: Georgia, san-serif; padding: 5px 1px; margin: 0; border-color: white;
            }
            QPushButton:hover {
                background-color: black; cursor: pointer;
                color: green;
            }
        """)
        self.performance_button.setStyleSheet("""
            QPushButton {
                background-color: black;
                color: white;
            }
            QPushButton:hover {
                background-color: green;
            }
        """)
        self.recycle_bin_button.setStyleSheet("""
            QPushButton {
                background-color: #4d4dff;
                color: white;
            }
            QPushButton:hover {
                background-color: green;
                color: white;
                
            }
        """)
        performance_layout.addWidget(self.agl_shifts_button)
        performance_layout.addWidget(self.mode_combo)
        performance_layout.addWidget(self.refresh_button)
        performance_layout.addWidget(self.current_time_button)
        performance_layout.addWidget(self.performance_button)
        performance_layout.addWidget(self.recycle_bin_button)

        # Add layouts to main layout
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
        main_layout.addLayout(performance_layout)

        # Set background colors
        self.setStyleSheet("""
            QWidget {
                background-color: #05161a;
            }
            QLabel {
                background-color: #ffcc00; padding: 5px; color: black; font-weight:bold; font-family: Arial,sans-serif;
            }
            /*For multiple element style use e.g QListWidget, QLineEdit */
            QListWidget {
                background-color: #e4e7eb;
            }
            QLineEdit {
                background-color: white;
                color: black;
                font-weight: bold;
            }
            QPushButton {
                background-color: #98FB98;
                border: 1px solid #4CAF50;
                border-radius: 10px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: yellow;
            }
            QPushButton:pressed {
                background-color: #FF0000;
            }
            QToolTip {
                border: 2px solid black; /* Border color and width */
                border-radius: 7px; /* Border radius to make it circular */
                background-color: grey; /* Background color */
                color: yellow; /* Text color */
                padding: 8px; /* Padding inside the tooltip */
                overflow: hidden;
            }
            QMenu {
                background-color: None;
            }
            QMessageBox {
                background-color: #000; 
            }
            QMessageBox QPushButton {
                background-color: #000;
                color: white;
            }
            QMessageBox QPushButton:hover {
                background-color: #00ff00;
                color: white;
            }
            QMessageBox QLabel {
                background-color: #000;
                color: white;
            }
        """)

        self.load_tasks()

        # Connect the allTasksCompleted signal to the congrats_slot
        self.allTasksCompleted.connect(self.congrats_slot)
    def agl_shiftScheduler(self):
        self.agl_shifts = ShiftScheduleApp()
        self.agl_shifts.show()
    def change_mode(self, index):  # for mode selection
        global dark_mode_requested
        if index == 0:
            dark_mode_requested = True
            self.set_dark_mode()  # Dark mode
        else:
            dark_mode_requested = False
            self.set_light_mode()  # Light mode

    def set_dark_mode(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #021024;
            }
            QLabel {
                background-color: #5483b3;padding: 5px;
                color: white;
            }
            /*For multiple element style use e.g QListWidget, QLineEdit */
            QListWidget {
                background-color: #29343d; color: #ccc;
            }
            QListWidget::item:selected {
                background-color: #0f969c; color: #c1e8ff;
            }
            QLineEdit {
                background-color: #c1ebff;
            }
            QPushButton {
                background-color: #5483b3;
                border: 1px solid #4CAF50;
                border-radius: 10px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: green; color: white;
            }
            QPushButton:pressed {
                background-color: #FF0000;
            }
            QComboBox {
                background-color: #c1ebff;
                color: white;
            }
            QMenu {background-color: #29343d; color: #ccc;}
        """)
        self.current_time_button.setStyleSheet("""
            QPushButton:hover {
                    background-color: #021024; border-color: #021024; color: #021024;
            }
            QPushButton {
                    background-color: #021024; border-color: #021024; color: yellow;
            }
        """)
    def set_light_mode(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #05161a;
            }
            QLabel {
                background-color: #ffcc00;
                padding: 5px;
                color: black;
                font-weight:bold;
            }
            /*For multiple element style use e.g QListWidget, QLineEdit */
            QListWidget {
                background-color: #e4e7eb;
            }
            QLineEdit {
                background-color: white;
                color: black;
                font-weight: bold;
            }
            QPushButton {
                background-color: #98FB98;
                border: 1px solid #4CAF50;
                border-radius: 10px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: yellow;
            }
            QPushButton:pressed {
                background-color: #FF0000;
            }
            QToolTip {
                border: 2px solid black; /* Border color and width */
                border-radius: 7px; /* Border radius to make it circular */
                background-color: grey; /* Background color */
                color: yellow; /* Text color */
                padding: 8px; /* Padding inside the tooltip */
                overflow: hidden;
            }
            QMessageBox {
                background-color: #000; 
            }
            QMessageBox QPushButton {
                background-color: #000;
                color: white;
            }
            QMessageBox QPushButton:hover {
                background-color: #00ff00;
                color: white;
            }
            QMessageBox QLabel {
                background-color: #000;
                color: white;
            }
            QMenu {background-color: #e4e7eb; color: #000;}
        """)
    def refresh(self):
        self.load_tasks()

    def update_time_button(self):
        # Get the current time
        current_datetime = QDateTime.currentDateTime().time()

        # Calculate the new time by adding the elapsed time
        new_time = current_datetime.addSecs(self.elapsed_time_seconds)

        # Format the new time as a string
        new_time_str = new_time.toString("hh:mm:ss")

        # Update the text of the current time button with the new time
        self.current_time_button.setText(f"Live Time: {new_time_str}")

        # Increment elapsed time in seconds
        self.elapsed_time_seconds += 0

    def pending_task_doubleclickToCopy(self, item):
        clipboard = QApplication.clipboard()
        clipboard.setText(item.text())
    def pendingTasksContextMenu(self, pos):
        context_menu = QMenu(self)
        # sub menu
        context_menu_submenu = context_menu.addMenu("More")
        change_text_color_action = context_menu_submenu.addAction("Change Text Color")
        change_background_color_action = context_menu_submenu.addAction("Change Background Color")
        change_text_color_action.triggered.connect(self.context_menu_submenu_changeTextColor)
        change_background_color_action.triggered.connect(self.context_menu_submenu_changeBackgroundColor)
        context_menu.addSeparator()
        # context_menu.setEnabled(False) to disable
        complete_task_action = context_menu.addAction("Complete Task")
        context_menu.addSeparator()
        delete_action = context_menu.addAction("Delete            Delete")
        select_all_action = context_menu.addAction("Select All      Ctrl+A")
        copy_action = context_menu.addAction("Copy            Ctrl+C")
        action = context_menu.exec_(self.mapToGlobal(pos))
        if action == delete_action:
            self.pendingTasksContextMenu_DeleteTask()
        elif action == complete_task_action:
            self.complete_task()
        elif action == select_all_action:
            self.pendingTasksContextMenu_SelectAll()
        elif action == copy_action:
            self.pendingTasksContextMenu_Copy()

    def pendingTasksContextMenu_DeleteTask(self):
        selected_items = self.pending_tasks_listbox.selectedItems()
        for item in selected_items:
            # remove selected item's text from the self.pending_tasks list
            self.pending_tasks.remove(item.text())
        # remove the item itself from the self.pending_tasks_listbox
        self.update_pending_tasks_listbox()
        self.save_tasks()

    def pendingTasksContextMenu_SelectAll(self):
        self.pending_tasks_listbox.selectAll()

    def pendingTasksContextMenu_Copy(self):
        selected_items = self.pending_tasks_listbox.selectedItems()
        if selected_items:
            clipboard_text = "\n".join(item.text() for item in selected_items)
            QApplication.clipboard().setText(clipboard_text)
    def pending_tasks_keypress(self, event):
        modifiers = QApplication.keyboardModifiers()
        if event.key() == Qt.Key_D and modifiers == Qt.ControlModifier:
            # Ctrl + D pressed, delete selected items
            self.pendingTasksContextMenu_DeleteTask()
        elif event.key() == Qt.Key_Delete:  # Delete is not used with modifiers like Ctrl, Alt, Shift, Meta keys(windows)
            # Delete pressed, delete selected items
            self.pendingTasksContextMenu_DeleteTask()
        elif event.key() == Qt.Key_A and modifiers == Qt.ControlModifier:
            # Ctrl + A pressed, select all items
            self.pending_tasks_listbox.selectAll()
        elif event.key() == Qt.Key_C and modifiers == Qt.ControlModifier:
            selected_items = self.pending_tasks_listbox.selectedItems()
            if selected_items:
                clipboard_text = "\n".join(item.text() for item in selected_items)
                QApplication.clipboard().setText(clipboard_text)
        else:
            # Pass other key events to the default implementation
            super().keyPressEvent(event)

    def context_menu_submenu_changeTextColor(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.pending_tasks_listbox.setStyleSheet(f"color: {color.name()}")

    def context_menu_submenu_changeBackgroundColor(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.pending_tasks_listbox.setStyleSheet(f"background-color: {color.name()}")

    def add_tasks(self):
        task = self.task_entry.text().upper()
        if task:
            if task in self.completed_tasks:
                # create a custom message box; note, you must execute it using msg_box.exec_()
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.setText("You already completed this task!")
                if dark_mode_requested:
                    msg_box.setStyleSheet('background-color: #000')
                msg_box.setWindowTitle("Completed Task")
                msg_box.setStandardButtons(QMessageBox.Ok)
                disclaimer_text = (
                    "Please note that no duplicates are allowed. "
                    "You already completed the task."
                    "To set it again, mark the existing task as completed"
                )
                msg_box.setDetailedText(disclaimer_text)
                msg_box.exec_()  # show() displays the widget non-modally; control returns to the caller immediately
            elif task in self.pending_tasks:
                # create a custom message box; note, you must execute it using msg_box.exec_()
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.setText("Task already exists in the pending tasks list.")
                msg_box.setWindowTitle("Duplicate Task")
                msg_box.setStandardButtons(QMessageBox.Ok)
                disclaimer_text = (
                    "Please note that no duplicates are allowed. "
                    "Avoiding duplicates is crucial for maintaining data integrity and "
                    "ensuring accurate results. Please review your entries carefully to "
                    "prevent duplication."
                )
                msg_box.setDetailedText(disclaimer_text)
                msg_box.exec_()  # show() displays the widget non-modally; control returns to the caller immediately
            else:
                self.pending_tasks.append(task)
                self.update_pending_tasks_listbox()
                self.task_entry.clear()
                self.save_tasks()

    def eventFilter(self, obj, event):
        #  The viewport is the area where the items of the list are displayed.
        if obj is self.completed_tasks_listbox.viewport() and event.type() == event.DragEnter:
            event.accept()  #  marks the event as processed but allows further handling by subsequent filters or default handlers.
        elif obj is self.completed_tasks_listbox.viewport() and event.type() == event.Drop:
            mime_data = event.mimeData()  # contains the data being transferred during the drag-and-drop operation.
            items = mime_data.text().split('\n')  #  dragged data is formatted as a newline-separated list of items
            if items:
                # Only call complete_task() if there are items dropped
                self.complete_task()  # Call complete_task function only once
                return True  # Return True to indicate that the event was handled
        elif obj is self.pending_tasks_listbox.viewport() and event.type() == event.DragEnter:
            event.accept()
        elif obj is self.pending_tasks_listbox.viewport() and event.type() == event.Drop:
            mime_data = event.mimeData()
            items = mime_data.text().split('\n')
            if items:
                selected_tasks_to_clear = self.completed_tasks_listbox.selectedIndexes()
                selected_tasks_to_clear.sort(reverse=True,
                                             key=lambda
                                                 x: x.row())  # Reverse sorting to avoid issues when removing items
                for index in selected_tasks_to_clear:
                    selected_task_index = index.row()
                    cleared_task = self.completed_tasks.pop(selected_task_index)
                    self.pending_tasks.append(cleared_task)
                    self.pending_tasks_listbox.addItem(cleared_task)

                self.update_completed_tasks_listbox()
                self.save_tasks()
                return True  # Return True to indicate that the event was handled

        return super().eventFilter(obj, event)

    def completed_tasks_keypress(self, event):
        modifiers = QApplication.keyboardModifiers()
        if event.key() == Qt.Key_C and modifiers == Qt.ControlModifier:
            selected_items = self.completed_tasks_listbox.selectedItems()
            if selected_items:
                clipboard_text = "\n".join(item.text() for item in selected_items)
                QApplication.clipboard().setText(clipboard_text)
        else:
            # Pass other key events to the default implementation
            super().keyPressEvent(event)

    def complete_task(self):
        selected_tasks_indexes = self.pending_tasks_listbox.selectedIndexes()
        selected_tasks_indexes.sort(reverse=True,
                                    key=lambda x: x.row())  # Reverse sorting to avoid issues when removing items
        if selected_tasks_indexes:
            for index in selected_tasks_indexes:
                selected_task_index = index.row()
                completed_task = self.pending_tasks.pop(selected_task_index)
                if completed_task not in self.completed_tasks:
                    self.completed_tasks.append(completed_task)
        else:
            QMessageBox.information(self, "No Selection", "You have not selected item", QMessageBox.Ok)

        self.update_pending_tasks_listbox()
        self.update_completed_tasks_listbox()
        self.save_tasks()

        # Check if all tasks are completed
        if not self.pending_tasks:
            self.allTasksCompleted.emit()

    def congrats_slot(self):
        # This slot will be called when all tasks are completed
        QMessageBox.information(self, "Congratulations!", "You've completed all tasks! 🎉", QMessageBox.Ok)
    def clear_a_completed_task(self):
        selected_tasks_to_clear = self.completed_tasks_listbox.selectedIndexes()
        selected_tasks_to_clear.sort(reverse=True,
                                     key=lambda x: x.row())  # Reverse sorting to avoid issues when removing items
        if selected_tasks_to_clear:
            for index in selected_tasks_to_clear:
                selected_task_index = index.row()
                cleared_task = self.completed_tasks.pop(selected_task_index)
                # Create an instance of Recycle_Bin_Window if not already created
                self.recycle_bin = Recycle_Bin_Window()
                # Append the cleared task to the recycle_bin_tasks list
                self.recycle_bin.recycle_bin_tasks.append(cleared_task)
        else:
            QMessageBox.information(self, "No Selection", "No item selected!", QMessageBox.Ok)
            return

        # Update recycle bin listbox before saving recycled items
        self.recycle_bin.save_recycled_items()
        self.recycle_bin.update_recycle_bin_listbox()

        self.update_completed_tasks_listbox()
        self.save_tasks()

    def clear_completed_tasks(self):
        # implement logic to populate recycle bin listbox
        all_items = [self.completed_tasks_listbox.item(index).text() for index in range(self.completed_tasks_listbox.count())]
        self.recycle_bin = Recycle_Bin_Window()
        # Append the cleared task to the recycle_bin_tasks list
        if all_items:
            self.recycle_bin.recycle_bin_tasks.extend(all_items)
        else:
            QMessageBox.information(self, "No Selection", "You have no items!", QMessageBox.Ok)
        self.recycle_bin.save_recycled_items()

        self.completed_tasks = []
        self.update_completed_tasks_listbox()
        self.save_tasks()

    def update_pending_tasks_listbox(self):
        self.pending_tasks_listbox.clear()
        for task in self.pending_tasks:
            self.pending_tasks_listbox.addItem(task)

    def update_completed_tasks_listbox(self):
        self.completed_tasks_listbox.clear()
        for task in self.completed_tasks:
            self.completed_tasks_listbox.addItem(task)

    def progress_window(self):
        self.Performance_Window = Performance_Window()
        self.Performance_Window.show()

    def open_recycle_bin_window(self):
        self.recycle_bin = Recycle_Bin_Window()
        self.recycle_bin.show()

    def closeEvent(self, event):
        # Override the closeEvent method to emit the closed signal when the window is closed
        # allow other windows or components of the application to perform necessary cleanup or actions when the
        # main window is closed.
        self.closed.emit()
        event.accept()

    def load_tasks(self):
        try:
            with open("PyQt5_tasks.txt", "r") as file:
                lines = file.readlines()
                self.pending_tasks = []
                self.completed_tasks = []

                pending_section = True
                for line in lines:
                    line = line.strip()
                    if line == "Completed Tasks:":
                        pending_section = False
                    elif pending_section and line != "Pending Tasks:":
                        self.pending_tasks.append(line)
                    elif not pending_section:
                        self.completed_tasks.append(line)

                self.update_pending_tasks_listbox()
                self.update_completed_tasks_listbox()

        except FileNotFoundError:
            return 'PyQt5_tasks.txt is missing'

    def save_tasks(self):
        with open("PyQt5_tasks.txt", "w") as file:
            file.write("Pending Tasks:\n")
            for task in self.pending_tasks:
                file.write(task + "\n")

            file.write("Completed Tasks:\n")
            for task in self.completed_tasks:
                file.write(task + "\n")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    todo_app = TodoApp()
    todo_app.show()
    # Connect the closed signal of TodoApp to close the PerformanceWindow
    todo_app.closed.connect(Performance_Window.close)
    # Connect the closed signal of TodoApp to close the Recycle_Bin_Window
    todo_app.closed.connect(Recycle_Bin_Window.close)
    todo_app.closed.connect(ShiftScheduleApp.close)
    sys.exit(app.exec_())
