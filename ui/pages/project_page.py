from ui.pages.base_page import BasePage

class ProjectPage(BasePage):
    """Generic project page."""
    
    def __init__(self, parent, project_name):
        super().__init__(
            parent=parent,
            title=project_name,
            description=f"{project_name} content will appear here."
        )