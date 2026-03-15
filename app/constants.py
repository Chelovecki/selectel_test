

VACANCY_EXTERNAL_ID_EXISTS_RESPONSE = {
    409: {
        "description": "Vacancy with this external_id already exists",
        "content": {
            "application/json": {
                "example": {
                    "error": "vacancy_external_id_exists_handler",
                    "msg": "Vacancy with external_id '10' already exists"
                }
            }
        },
    }
}
