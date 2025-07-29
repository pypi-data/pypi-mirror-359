# cyborgdb_service/utils/error_handler.py

from fastapi import HTTPException, status

def handle_exception(e: Exception, context: str = "Operation failed"):
    """
    Convert Python exceptions into structured HTTPException responses.
    
    Args:
        e (Exception): The caught exception.
        context (str): A custom prefix message to add context for different API endpoints.

    Raises:
        HTTPException: A properly formatted FastAPI error response.
    """

    exception_mapping = {
        # 400 Bad Request (Client Errors)
        ValueError: (status.HTTP_400_BAD_REQUEST, "Invalid input"),
        TypeError: (status.HTTP_400_BAD_REQUEST, "Type error in request"),
        KeyError: (status.HTTP_400_BAD_REQUEST, "Missing required key"),
        IndexError: (status.HTTP_400_BAD_REQUEST, "Index out of range"),
        AttributeError: (status.HTTP_400_BAD_REQUEST, "Invalid attribute access"),
        AssertionError: (status.HTTP_400_BAD_REQUEST, "Assertion failed"),

        # 401 Unauthorized (Authentication Errors)
        PermissionError: (status.HTTP_401_UNAUTHORIZED, "Permission denied"),

        # 404 Not Found (Missing Resources)
        FileNotFoundError: (status.HTTP_404_NOT_FOUND, "File not found"),
        ModuleNotFoundError: (status.HTTP_404_NOT_FOUND, "Module not found"),

        # 405 Method Not Allowed (Invalid HTTP Method)
        NotImplementedError: (status.HTTP_405_METHOD_NOT_ALLOWED, "Method not allowed"),

        # 408 Request Timeout (Slow Requests)
        TimeoutError: (status.HTTP_408_REQUEST_TIMEOUT, "Request timeout"),

        # 409 Conflict (Conflict Errors)
        FileExistsError: (status.HTTP_409_CONFLICT, "File already exists"),
        InterruptedError: (status.HTTP_409_CONFLICT, "Process interrupted"),

        # 422 Unprocessable Entity (Validation Errors)
        UnicodeDecodeError: (status.HTTP_422_UNPROCESSABLE_ENTITY, "Unicode decoding error"),
        UnicodeEncodeError: (status.HTTP_422_UNPROCESSABLE_ENTITY, "Unicode encoding error"),
        ZeroDivisionError: (status.HTTP_422_UNPROCESSABLE_ENTITY, "Cannot divide by zero"),

        # 500 Internal Server Error (General Server Errors)
        RuntimeError: (status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal error"),
        RecursionError: (status.HTTP_500_INTERNAL_SERVER_ERROR, "Recursion depth exceeded"),
        MemoryError: (status.HTTP_500_INTERNAL_SERVER_ERROR, "Memory allocation failed"),
        SystemError: (status.HTTP_500_INTERNAL_SERVER_ERROR, "Python interpreter error"),
        ImportError: (status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to import module"),
        OSError: (status.HTTP_500_INTERNAL_SERVER_ERROR, "Operating system error"),
    }

    for exception_type, (http_status, message) in exception_mapping.items():
        if isinstance(e, exception_type):
            raise HTTPException(status_code=http_status, detail=f"{context}: {message}: {str(e)}") from e

    # If exception type is not mapped, return a generic internal server error
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"{context}: Unexpected server error: {str(e)}"
    ) from e
