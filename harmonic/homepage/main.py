from homepage_ui import Ui_mw_home
from PySide6 import QtWidgets


class HomeWindow(QtWidgets.QMainWindow, Ui_mw_home):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.w_dock.setWindowTitle("podscale")
        self.w_dock.setFixedWidth(50)
        self.setStatusBar(None)

        # sidebar select
        self.bt_home.clicked.connect(lambda: self.switch_view(0))
        self.bt_chat.clicked.connect(lambda: self.switch_view(1))
        self.bt_brandperformance.clicked.connect(lambda: self.switch_view(2))

        # Home page
        revenue = 2349.342
        spend_goal = 100_000
        current_spend = 75_678
        self.actionclose.triggered.connect(self.close)
        self.current_month_revenue.setText(f"${round(revenue)}")
        self.current_spend_goal.setValue((current_spend/spend_goal)*100)

        
        # chat page
        self.bt_submitchat.clicked.connect(self.handle_chat_submit)

        # brand brand page
        self.cb_brandfilter.addItems(["All", "Lume", "Mando", "Cuts"])


    def switch_view(self, index):
        self.stackedWidget.setCurrentIndex(index)

    def handle_chat_submit(self):
        in_text = self.te_chatinput.toPlainText()
        self.te_chathistory.setHtml(f"<p>{in_text}</p>")
        self.te_chatinput.clear()


if __name__ == "__main__":
    app = QtWidgets.QApplication()
    window = HomeWindow()
    window.show()
    app.exec()