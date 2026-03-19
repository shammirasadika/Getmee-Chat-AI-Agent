from models.system_model import SystemStatusResponse


def get_system_status() -> SystemStatusResponse:
    return SystemStatusResponse(
        status="GetMee Chat Backend Running"
    )