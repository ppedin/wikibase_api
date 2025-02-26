"""
Main application module for the XML validation API.

This file initializes the API using FastAPI objects. 
Then, it defines two endpoints: one for health check and a root endpoint. 
Recognizes validation.router as a router. 
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.api.routes import validation
from app.schemas.error import HTTPError


# Creates the main FastAPI application instance. 
app = FastAPI(
    title="XML Schema Validation API",
    description="API for validating XML files against predefined schemas",
    version="1.0.0",
)

# Adds Cross-Origin Resource Sharing (CORS) middleware to allow requests from different origins. 
# The current configuration allows requests from any origin ("*"),
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#  This integrates your validation routes defined in app/api/routes/validation.py into the main application
#  Therefore, we can define endpoints in validation
app.include_router(validation.router)


# Custom exception handler for generic errors
#  The exception handler is an asynchronous function
#  Returns a JSONResponse object (which is a FastAPI class)
#  The decorator @app.exception_handler tells FastAPI to use this function whenever an unhandled exception occurs
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handle generic exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"An unexpected error occurred: {str(exc)}"},
    )


# Custom OpenAPI schema with appropriate documentation
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Customize the schema if needed
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# Root endpoint
#  This decorator registers a function as a route handler for GET requests:
@app.get("/", tags=["status"])
async def root():
    """Root endpoint to check if the API is running."""
    return {"status": "ok", "message": "XML Schema Validation API is up and running"}


# Health check endpoint
@app.get("/health", tags=["status"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}