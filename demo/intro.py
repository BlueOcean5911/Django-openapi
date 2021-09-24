from os import path
from hashlib import md5
from datetime import datetime
from typing import List, Optional
from django.urls import path as url_path

try:
    from django import setup as django_setup
except ImportError:

    def django_setup():
        pass


from django.http import HttpResponseRedirect
from django.conf.urls import url
from pydantic import BaseModel, Field
from django_mini_fastapi import (
    OpenAPI,
    Path,
    Body,
    Query,
    Form,
    File,
    UploadFile,
    Cookie,
    Header,
)


"""
A minimal working demo of Django App
"""

DEBUG = True
SECRET_KEY = "canukeepasecret"
ROOT_URLCONF = __name__

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
    }
}


django_setup()


def redirect_to_doc(request):
    return HttpResponseRedirect(
        "/intro/rapidoc#tag--1.-Setup-your-first-OpenAPI-endpoint"
    )


api = OpenAPI(
    title="OpenAPI Test",
    version="0.1",
    description="Just a Test",
    root_path="/intro",
)

urlpatterns = [
    url(r"^$", redirect_to_doc),
    api.as_django_url_pattern(),
]


class IntroResponse1(BaseModel):
    arg1: str
    arg2: str


class IntroResponse2(BaseModel):
    arg1: str = Field(min_length=3, max_length=10)
    arg2: int = Field(ge=0, le=10)
    arg3: bool = Field(False)


@api.get(
    "/basic_get_request",
    tags=["1. Setup your first OpenAPI endpoint"],
    summary="Get start & create a simple http GET route",
)
def basic_get_request():
    """
    For start using django-mini-fastapi, in your Django project

    * import OpenAPI from django_mini_fastapi
    * create an OpenAPI object
    * put it into your urlpatterns
    * start define api endpoints using api OpenAPI object


    ```python
    from django_mini_fastapi import OpenAPI

    api = OpenAPI(
        title='OpenAPI Test',
        version='0.1',
        description='Just a Test',
        root_path='/intro'
    )

    urlpatterns = [
        api.as_django_url_pattern()
    ]

    @api.get('/basic_get_request')
    def basic_get_request():
        return {'hello': 'world'}
    ```
    """
    return {"hello": "world"}


@api.get(
    "/test_path_and_query_parameters/{arg1}",
    tags=["1. Basic HTTP requests"],
    summary="Define path & query parameters",
    response_model=IntroResponse1,
)
def test_path_and_query_parameters(
    arg1,
    arg2,
):
    """
    Use same arg name as the one in path for receiving path args
    For those args which names not matched path arg names, will be parsed as query parameter

    ```python
    from django_mini_fastapi import Path

    @api.get('/test_path_and_query_parameters/{arg1}')
    def test_path_and_query_parameters(arg1, arg2):
        return dict(arg1=arg1, arg2=arg2)
    ```
    """
    return dict(arg1=arg1, arg2=arg2)


@api.get(
    "/basic_check_on_path_or_query_parameter/{arg1}",
    tags=["1. Basic HTTP requests"],
    summary="Define query string parameters",
    response_model=IntroResponse1,
)
def basic_check_on_path_or_query_parameter(
    arg1: int = Path(..., ge=0), arg2: str = Query("default", min_length=3)
):
    """
    Use `Query()` or `Path()` to tell API how to parse and check constraints of parameters

    ```python
    from django_mini_fastapi import Query, Path

    @api.get('/basic_check_on_path_or_query_parameter/{arg1}')
    def basic_check_on_path_or_query_parameter(arg1: int=Path(..., ge=0), arg2: str=Query('default')):
        return dict(arg1=arg1, arg2=arg2)
    ```
    """
    return dict(arg1=arg1, arg2=arg2)


@api.get(
    "/get_request_with_json_schema_query_args",
    tags=["1. Basic HTTP requests"],
    summary="Auto parameter validation via JSON schema fields",
    response_model=IntroResponse2,
)
def get_request_with_json_schema_query_args(
    arg1: str = Query(..., min_length=3, max_length=10),
    arg2: int = Query(..., ge=0, le=10),
    arg3: bool = Query(False),
):
    """
    ```python
    from django_mini_fastapi import Query
    from django_mini_fastapi.schema import StringField, NumberField, BooleanField

    @api.get('/get_request_with_json_schema_query_args')
    def get_request_with_json_schema_query_args(
        arg1: str = Query(..., min_length=3, max_length=10),
        arg2: int = Query(ge=0, le=10),
        arg3: bool = Query(False),
    ):
        return dict(arg1=arg1, arg2=arg2, arg3=arg3)
    ```
    """
    return dict(arg1=arg1, arg2=arg2, arg3=arg3)


@api.post(
    "/post_request_with_json_schema_form_args",
    tags=["1. Basic HTTP requests"],
    summary="Define Form parameters",
    response_model=IntroResponse2,
)
def post_request_with_json_schema_form_args(
    arg1: str = Form(..., min_length=3, max_length=10),
    arg2: int = Form(..., ge=0, le=10),
    arg3: bool = Form(False),
):
    """
    Now we use the same JSON schema field definitions, but in Form() format.

    ```python
    from django_mini_fastapi import Form
    from django_mini_fastapi.schema import StringField, NumberField, BooleanField

    @api.post('/post_request_with_json_schema_form_args')
    def post_request_with_json_schema_form_args(
        arg1: str = Form(..., min_length=3, max_length=10),
        arg2: int = Form(..., ge=0, le=10),
        arg3: bool = Form(False),
    ):
        return dict(arg1=arg1, arg2=arg2, arg3=arg3)
    ```
    """
    return dict(arg1=arg1, arg2=arg2, arg3=arg3)


@api.post(
    "/post_request_file_upload",
    tags=["1. Basic HTTP requests"],
    summary="Define File Upload",
)
def post_request_file_upload(
    upload_file: UploadFile = File(...),
    md5_hash: Optional[str] = Form(None, description="md5 of uploaded file"),
):
    """
    Now let's try building an endpoint for user file upload.

    ```python
    from hashlib import md5
    from django_mini_fastapi import UploadedFile, Form, File
    from django_mini_fastapi.schema import StringField, NumberField, BooleanField

    @api.post('/post_request_file_upload')
    def post_request_file_upload(
        upload_file: UploadedFile = File(...),
        md5_hash: Optional[str] = Form(None, description="md5 of uploaded file"),
    ):
        return {
            'submitted_md5': md5_hash,
            'file': {
                'name': upload_file.name,
                'size': upload_file.size,
                'md5': md5(upload_file.read()).hexdigest,
            },
        }
    ```
    """
    return {
        "submitted_md5": md5_hash,
        "file": {
            "name": upload_file.name,
            "size": upload_file.size,
            "md5": md5(upload_file.read()).hexdigest(),
        },
    }


class SamplePayload(BaseModel):
    arg1: str = Field(..., min_length=3, max_length=10)
    arg2: int = Field(..., ge=0, le=10)
    arg3: bool = Field(..., default_value=False)


class SampleResponse(BaseModel):
    obj: SamplePayload
    ary: List[SamplePayload]


@api.post(
    "/post_request_with_json_schema_body",
    tags=["1. Basic HTTP requests"],
    summary="Define body parameters via JSON schema model",
    response_model=SampleResponse,
)
def post_request_with_json_schema_body(payload: SamplePayload):
    """
    The JSON schema fields could also be used for describing JSON body format,
    all you need is declearing a class inherited from BaseModel class.

    ```python
    from pydantic import BaseModel, Field

    class SamplePayload(BaseModel):
        arg1: str = Field(..., min_length=3, max_length=10)
        arg2: int = Field(..., ge=0, le=10)
        arg3: bool = Field(..., default_value=False)


    class SampleResponse(BaseModel):
        obj: SamplePayload
        ary: List[SamplePayload]


    @api.post(
        '/post_request_with_json_schema_body',
        response_model=SampleResponse,  # you can also put json schema model here for declearing response model
    )
    def post_request_with_json_schema_body(
        payload: SamplePayload,
    ):
        return payload
    ```
    """
    return {"obj": payload, "ary": [payload, payload]}


# @api.post(
#     '/some_special_variables_by_name',
#     tags=['1. Basic HTTP requests'],
#     summary='Some special variables',
# )
# def some_special_variables_by_name(request, session, cookie_jar):
#     '''
# You could access some special variables via your function parameter name.

# * `request`

#   * the django `HttpRequest` object

# * `session`

#   * the session object binded on request

# * `cookie_jar`

#   * if you want to set/del cookies on the response object, you must use cookie_jar
#   * cookie_jar is a proxy object to real HttpResponse object. The `set_cookie()`, `delete_cookie()` functions on it have the same signatures of HttpResonse.

# ```python
# @api.get(
#     '/some_special_variables_by_name',
# )
# def some_special_variables_by_name(request, session, cookie_jar):

#     # this has the same signature as django HTTPResponse.set_cookie() function
#     cookie_jar.set_cookie('test_cookie', str(datetime.now()))

#     return {
#         'request': request,
#         'session': session,
#     }
# ```
#     '''

#     # this has the same signature as django HTTPResponse.set_cookie() function
#     cookie_jar.set_cookie('test_cookie', str(datetime.now()))

#     return {
#         'request': repr(request),
#         'session': session,
#     }


# @api.post(
#     '/other_argument_data_sources',
#     tags=['1. Basic HTTP requests'],
#     summary='Other argument data sources',
# )
# def other_argument_data_sources(
#     test_cookie=Cookie(), content_type=Header(), http_referer=Header()
# ):
#     '''
# You can also get your request arguments from other data sources.

# Like: `Header()`, `Cookie()`

# * *Note: While accessing via `Header()`, all variable name will converted to uppercase as http header key name*
# * *e.g.: `content_type` -> `CONTENT_TYPE`

# ```python
# @api.post(
#     '/other_argument_data_sources',
# )
# def other_argument_data_sources(
#     test_cookie=Cookie(), content_type=Header(), http_referer=Header()
# ):
#     return {
#         'test_cookie': test_cookie,
#         'content_type': content_type,
#         'referrer': http_referer,
#     }
# ```
#     '''
#     return {
#         'test_cookie': test_cookie,
#         'content_type': content_type,
#         'referrer': http_referer,
#     }
