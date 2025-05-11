"""
Home page of the application using composition.
"""
from ui.pages.content_page import ContentPage
from utils.logging import get_logger

logger = get_logger(__name__)

class HomePage(ContentPage):
    """Home page of the application using ContentPage composition."""
    
    def __init__(self, parent, controller=None):
        super().__init__(
            parent=parent,
            title="Welcome to Universal App",
            description="This is the central hub for all projects. Select a project from the sidebar to begin."
        )
        self.controller = controller
        logger.debug("HomePage initialized")