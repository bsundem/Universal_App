from ui.pages.base_page import BasePage

class HomePage(BasePage):
    """Home page of the application."""
    
    def __init__(self, parent):
        super().__init__(
            parent=parent,
            title="Welcome to Universal App",
            description="This is the central hub for all projects. Select a project from the sidebar to begin."
        )