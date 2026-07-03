class ProjectNotFoundError(Exception):
    def __init__(self, project_id: str) -> None:
        self.project_id = project_id
        super().__init__(f"Project not found: {project_id}")
