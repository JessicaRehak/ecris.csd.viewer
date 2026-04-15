class StatusBarSingleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StatusBarSingleton, cls).__new__(cls)
            cls._instance.status_text = "Starting up..."
            cls._instance.on_status_changed = None
        return cls._instance

    def update_status(self, info: str) -> None:
        self.status_text = info
        if self.on_status_changed:
            self.on_status_changed(info)

def update_status_bar(info: str) -> None:
    status_bar = StatusBarSingleton()
    status_bar.update_status(info)
