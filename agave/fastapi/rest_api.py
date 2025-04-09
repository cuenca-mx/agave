import mimetypes
from typing import Any, Optional
from urllib.parse import urlencode

from cuenca_validations.types import QueryParams

from ..core.loggers import get_request_model, get_sensitive_fields
from .middlewares.loggin_route import LoggingRoute

try:
    from fastapi import APIRouter, BackgroundTasks, Depends, Request, status
except ImportError:
    raise ImportError(
        "You must install agave with [fastapi] option.\n"
        "You can install it with: pip install agave[fastapi]"
    )

from fastapi.responses import JSONResponse as Response, StreamingResponse
from mongoengine import DoesNotExist, Q
from pydantic import BaseModel, Field, ValidationError
from starlette_context import context

from ..core.blueprints.decorators import copy_attributes
from ..core.exc import NotFoundError, UnprocessableEntity

SAMPLE_404 = {
    "summary": "Not found item",
    "value": {"error": "Not valid id"},
}


class RestApiBlueprint(APIRouter):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, route_class=LoggingRoute, **kwargs)

    @property
    def current_user_id(self) -> str:
        return context['user_id']

    @property
    def current_platform_id(self) -> str:
        return context['platform_id']

    @property
    def current_api_key_id(self) -> str:
        return context['api_key_id']

    def user_id_filter_required(self) -> bool:
        return context['user_id_filter_required']

    def platform_id_filter_required(self) -> bool:
        return context['platform_id_filter_required']

    def custom_filter_required(self, query_params: Any, model: Any) -> None:
        """
        Overwrite this method in order to add new context
        based on custom filter.
        set de value of your filter ex query_params.wallet = self.wallet
        """
        pass

    async def retrieve_object(
        self, resource_class: Any, resource_id: str
    ) -> Any:
        resource_id = (
            self.current_user_id if resource_id == 'me' else resource_id
        )
        query = Q(id=resource_id)
        if self.platform_id_filter_required() and hasattr(
            resource_class.model, 'platform_id'
        ):
            query = query & Q(platform_id=self.current_platform_id)

        if self.user_id_filter_required() and hasattr(
            resource_class.model, 'user_id'
        ):
            query = query & Q(user_id=self.current_user_id)

        try:
            data = await resource_class.model.objects.async_get(query)
        except DoesNotExist:
            raise NotFoundError('Not valid id')
        return data

    def resource(self, path: str):
        """Decorator to transform a class in FastApi REST endpoints

        @app.resource('/my_resource')
        class Items(Resource):
            model = MyMongoModel
            response_model = MyPydanticModel (Resource Interface)
            query_validator = MyPydanticModel

            def create(): ...
            def delete(id): ...
            def retrieve(id): ...
            def get_query_filter(): ...

        This implementation create the following endpoints

        POST /my_resource
        PATCH /my_resource
        DELETE /my_resource/id
        GET /my_resource/id
        GET /my_resource
        """

        def wrapper_resource_class(cls):
            """Wrapper for resource class
            :param cls: Resoucre class
            :return:
            """
            response_model = Any
            response_sample = {}
            include_in_schema = getattr(cls, 'include_in_schema', True)
            if hasattr(cls, 'response_model'):
                response_model = cls.response_model
                response_sample = response_model.schema().get('example')

            """ POST /resource
            Create a FastApi endpoint using the method "create"

            OR using the method "upload" to enable POST using a
            streaming multipart parser to receive files as form data. It
            validates form data using `Resource.upload_validator`.
            """
            if hasattr(cls, 'create'):
                route = self.post(
                    path,
                    summary=f'{cls.__name__} - Create',
                    response_model=response_model,
                    status_code=status.HTTP_201_CREATED,
                    include_in_schema=include_in_schema,
                )

                request_model = get_request_model(cls.create)
                cls.create.request_model = request_model
                cls.create.request_log_config_fields = get_sensitive_fields(
                    request_model
                )
                cls.create.response_log_config_fields = get_sensitive_fields(
                    response_model
                )

                route(cls.create)
            elif hasattr(cls, 'upload'):

                @self.post(
                    path,
                    summary=f'{cls.__name__} - Upload',
                    response_model=response_model,
                    include_in_schema=include_in_schema,
                    openapi_extra={
                        "requestBody": {
                            "content": {
                                "form-data": {
                                    "schema": cls.upload_validator.schema()
                                }
                            }
                        }
                    },
                )
                @copy_attributes(cls)
                async def upload(
                    request: Request, background_tasks: BackgroundTasks
                ):
                    form = await request.form()
                    try:
                        upload_params = cls.upload_validator(**form)
                    except ValidationError as exc:
                        return Response(content=exc.json(), status_code=400)

                    return await cls.upload(upload_params, background_tasks)

            """ DELETE /resource/{id}
            Use "delete" method (if exists) to create the FastApi endpoint
            """
            error_404 = json_openapi(404, 'Item not found', [SAMPLE_404])
            if hasattr(cls, 'delete'):

                @self.delete(
                    path + '/{id}',
                    summary=f'{cls.__name__} - Delete',
                    response_model=response_model,
                    responses=error_404,
                    description=(
                        f'Use id param to delete the {cls.__name__} object'
                    ),
                    include_in_schema=include_in_schema,
                )
                @copy_attributes(cls)
                async def delete(id: str, request: Request):
                    obj = await self.retrieve_object(cls, id)
                    return await cls.delete(obj, request)

            """ PATCH /resource/{id}
            Enable PATCH method if Resource.update method exist. It validates
            body data using `Resource.update_validator` but update logic is
            completely your responsibility.
            """
            if hasattr(cls, 'update'):

                request_model = get_request_model(cls.update)
                cls.update.request_model = request_model
                cls.update.request_log_config_fields = get_sensitive_fields(
                    request_model
                )
                cls.update.response_log_config_fields = get_sensitive_fields(
                    response_model
                )

                @self.patch(
                    path + '/{id}',
                    summary=f'{cls.__name__} - Update',
                    response_model=response_model,
                    responses=error_404,
                    description=(
                        f'Use id param to update the {cls.__name__} object'
                    ),
                    include_in_schema=include_in_schema,
                )
                @copy_attributes(cls)
                async def update(
                    id: str,
                    update_params: cls.update_validator,  # type: ignore
                    request: Request,
                ):
                    obj = await self.retrieve_object(cls, id)
                    try:
                        return await cls.update(obj, update_params, request)
                    except TypeError:
                        return await cls.update(obj, update_params)

            """ GET /resource/{id}
            By default GET method only fetch object from DB.
            If you need extra logic override "retrieve" or "download" methods
            """

            @self.get(
                path + '/{id}',
                summary=f'{cls.__name__} - Retrieve',
                response_model=response_model,
                responses=error_404,
                description=(
                    f'Use id param to retrieve the {cls.__name__} object'
                ),
                include_in_schema=include_in_schema,
            )
            @copy_attributes(cls)
            async def retrieve(id: str, request: Request):
                """GET /resource/{id}
                :param id: Object Id
                :return: Model object

                If exists "retrieve" method return the result of that, else
                use "id" param to retrieve the object of type "model" defined
                in the decorated class.

                The most of times this implementation is enough and is not
                necessary define a custom "retrieve" method
                """
                obj = await self.retrieve_object(cls, id)

                # This case is when the return is not an application/$
                # but can be some type of file such as image, xml, zip or pdf
                if hasattr(cls, 'download'):
                    file = await cls.download(obj)
                    mimetype = request.headers['accept']
                    extension = mimetypes.guess_extension(mimetype)
                    filename = f'{cls.model._class_name}.{extension}'
                    result = StreamingResponse(
                        file,
                        media_type=mimetype,
                        headers={
                            'Content-Disposition': (
                                'attachment; ' f'filename={filename}'
                            )
                        },
                    )
                elif hasattr(cls, 'retrieve'):
                    result = await cls.retrieve(obj)
                else:
                    result = obj.to_dict()

                return result

            retrieve.response_log_config_fields = get_sensitive_fields(
                response_model
            )

            """ GET /resource?param=value
            Use GET method to fetch and count filtered objects
            using query params.
            To Enable queries you have to define next fields
            in decorated class

            query_validator: Pydantic model to validate the params.
            get_query_filter: Method to provide the way that
            the params are used to filter data.
            """

            if not hasattr(cls, 'query_validator') or not hasattr(
                cls, 'get_query_filter'
            ):
                return cls

            query_description = (
                f'Make queries in resource {cls.__name__} and filter the '
                f'result using query parameters.  \n'
                f'The items are paginated, to iterate over them use the '
                f'`next_page_uri` included in response.  \n'  # noqa: W604
                f'If you need only a counter not the data send value `true` '
                f'in `count` param.'
            )

            # Build dynamically types for query response
            class QueryResponse(BaseModel):
                items: Optional[list[response_model]] = Field(
                    [],
                    description=(
                        f'List of {cls.__name__} that match with query '
                        f'filters'
                    ),
                )
                next_page_uri: Optional[str] = Field(
                    None, description='URL to fetch the next page of results'
                )
                count: Optional[int] = Field(
                    None,
                    description=(
                        f'Counter of {cls.__name__} objects that match with '
                        f'query filters.  \n'
                        f'If you need only a counter not the data send value '
                        f'`true` in `count` param.'  # noqa: W604
                    ),
                )

            QueryResponse.__name__ = f'QueryResponse{cls.__name__}'

            examples = [
                # If param "count" is False return the list of items
                {
                    'summary': 'Query objects',
                    'value': {
                        'items': [response_sample],
                        'next_page_uri': f'{path}?param1=value1&param2=value2',
                    },
                },
                # If param "count" is True return a counter
                {
                    'summary': 'Count objects',
                    'description': 'Sending `true` value in `count` param',
                    'value': {'count': 1},
                },
            ]

            def validate_params(request: Request):
                try:
                    return cls.query_validator(**request.query_params)
                except ValidationError as e:
                    raise UnprocessableEntity(e.json())

            @self.get(
                path,
                summary=f'{cls.__name__} - Query',
                response_model=QueryResponse,
                description=query_description,
                responses=json_openapi(200, 'Successful Response', examples),
                include_in_schema=include_in_schema,
            )
            @copy_attributes(cls)
            async def query(
                query_params: cls.query_validator = Depends(  # type: ignore
                    validate_params
                ),
            ):
                """GET /resource"""
                if self.platform_id_filter_required() and hasattr(
                    cls.model, 'platform_id'
                ):
                    query_params.platform_id = self.current_platform_id

                if self.user_id_filter_required() and hasattr(
                    cls.model, 'user_id'
                ):
                    query_params.user_id = self.current_user_id
                # Call for custom filter implemented in overwritemethod
                self.custom_filter_required(query_params, cls.model)

                filters = cls.get_query_filter(query_params)
                if query_params.count:
                    result = await _count(filters)
                elif hasattr(cls, 'query'):
                    result = await cls.query(
                        await _all(query_params, filters, path)
                    )
                else:
                    result = await _all(query_params, filters, path)
                return result

            async def _count(filters: Q):
                count = await cls.model.objects.filter(filters).async_count()
                return dict(count=count)

            async def _all(query: QueryParams, filters: Q, resource_path: str):
                if query.limit:
                    limit = min(query.limit, query.page_size)
                    query.limit = max(0, query.limit - limit)
                else:
                    limit = query.page_size
                query_set = (
                    cls.model.objects.order_by("-created_at")
                    .filter(filters)
                    .limit(limit)
                )
                items = await query_set.async_to_list()
                item_dicts = [i.to_dict() for i in items]

                has_more: Optional[bool] = None
                if wants_more := query.limit is None or query.limit > 0:
                    # only perform this query if it's necessary
                    has_more = (
                        await query_set.limit(limit + 1).async_count() > limit
                    )

                next_page_uri: Optional[str] = None
                if wants_more and has_more:
                    query.created_before = item_dicts[-1]['created_at']
                    params = query.model_dump()
                    if self.user_id_filter_required():
                        params.pop('user_id')
                    if self.platform_id_filter_required():
                        params.pop('platform_id')
                    next_page_uri = f'{resource_path}?{urlencode(params)}'
                return dict(items=item_dicts, next_page_uri=next_page_uri)

            return cls

        return wrapper_resource_class


def json_openapi(code: int, description, samples: list[dict]) -> dict:
    examples = {f'example_{i}': ex for i, ex in enumerate(samples)}
    return {
        code: {
            'description': description,
            'content': {'application/json': {'examples': examples}},
        },
    }
