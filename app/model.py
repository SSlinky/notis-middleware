"""The data models for the application."""
from pydantic import BaseModel


class HoursSubTotal(BaseModel):
    """Model for the subtotal of hours."""
    total: float = 0.0
    service: str
    project: str

    # def __init__(self, service: str, project: str):
    #     super().__init__()
    #     self.service = service
    #     self.project = project

    def add_minutes(self, minutes: float):
        """Add minutes to the total hours."""
        self.total += minutes / 60


class ResponseModel(BaseModel):
    """Response model for the /hours endpoint."""
    response_message: str = None
    services: dict[str, dict[str, str]] = {}
    data: dict[str, HoursSubTotal] = {}

    def get_service(self, service_id: str):
        """Get the service name for a given service ID."""
        svc = self.services.get(service_id)
        name = svc.get("name", "Unknown") if svc else "Unknown"
        project = svc.get("deal", "Unknown") if svc else "Unknown"
        return {
            "name": name,
            "project": project
        }
