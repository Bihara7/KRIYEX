import sys

from kriyex.app.bootstrap import create_application, create_services
from kriyex.gui.main_window import MainWindow


def main() -> int:
    app = create_application()

    window = MainWindow(create_services())
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
