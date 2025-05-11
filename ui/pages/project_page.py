"""
Generic project page using composition.
"""
from ui.pages.content_page import ContentPage
from utils.logging import get_logger

logger = get_logger(__name__)

class ProjectPage(ContentPage):
    """Generic project page using ContentPage composition."""
    
    def __init__(self, parent, project_name, controller=None):
        super().__init__(
            parent=parent,
            title=project_name,
            description=f"{project_name} content will appear here."
        )
        self.controller = controller
        self.project_name = project_name
        logger.debug(f"ProjectPage initialized for {project_name}")