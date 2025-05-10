from ui.pages.base_page import BasePage

class SettingsPage(BasePage):
    """Settings page of the application."""
    
    def __init__(self, parent):
        super().__init__(
            parent=parent,
            title="Settings",
            description="Application settings will appear here."
        )