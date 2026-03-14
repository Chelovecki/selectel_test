class VacancyExternalIdExistsError(Exception):
    """Raised when trying to update a vacancy with the same external ID already exists."""

    def __init__(self, external_id: int):
        self.external_id = external_id
        super().__init__(f"Vacancy with external_id '{external_id}' already exists")
