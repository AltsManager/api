class NotFoundError(Exception):
    def __init__(self, resource: str, resource_id: object):
        self.resource = resource
        self.resource_id = resource_id
        super().__init__(f"{resource} {resource_id} not found")


class ValidationError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)
