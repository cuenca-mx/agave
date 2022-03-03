import mimetypes
from typing import Any, Optional, Type, cast
from urllib.parse import urlencode

from chalice import Blueprint, NotFoundError, Response
from cuenca_validations.types import QueryParams
from mongoengine import DoesNotExist, Q
from pydantic import BaseModel, ValidationError

from .decorators import copy_attributes


class RestApiBlueprint(Blueprint):
    def get(self, path: str, **kwargs):
        return self.route(path, methods=['GET'], **kwargs)

    def post(self, path: str, **kwargs):
        return self.route(path, methods=['POST'], **kwargs)

    def patch(self, path: str, **kwargs):
        return self.route(path, methods=['PATCH'], **kwargs)

    def delete(self, path: str, **kwargs):
        return self.route(path, methods=['DELETE'], **kwargs)

    @property
    def current_user_id(self):
        return self.current_request.user_id

    @property
    def current_platform_id(self):
        return self.current_request.platform_id

    def user_id_filter_required(self):
        """
        This method is required to be implemented with your own business logic.
        You are responsible of determining when `user_id` filter is required.
        """
        raise NotImplementedError(
            'this method should be override'
        )  # pragma: no cover

    def platform_id_filter_required(self):
        """
        This method is required to be implemented with your own business logic.
        You are responsible of determining when `user_id` filter is required.
        """
        raise NotImplementedError(
            'this method should be override'
        )  # pragma: no cover

    def retrieve_object(self, resource_class: Any, resource_id: str) -> Any:
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
            data = resource_class.model.objects.get(query)
        except DoesNotExist:
            raise NotFoundError('Not valid id')
        return data

    def validate(self, validation_type: Type[BaseModel]):
        """This decorator validate the request body using a custom pydantyc model
        If validation fails return a BadRequest response with details

        @app.validate(MyPydanticModel)
        def my_method(request: MyPydanticModel):
            ...
        """

        def decorator(func):
            def wrapper(*args, **kwargs):
                try:
                    request = validation_type(**self.current_request.json_body)
                except ValidationError as e:
                    return Response(e.json(), status_code=400)
                return func(*args, request, **kwargs)

            return wrapper

        return decorator

    def resource(self, path: str):
        """Decorator to transform a class in Chalice REST endpoints

        @app.resource('/my_resource')
        class Items(Resource):
            model = MyMongoModel
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

            """ POST /resource
            Create a chalice endpoint using the method "create"
            If the method receive body params decorate it with @validate
            """
            if hasattr(cls, 'create'):
                route = self.post(path)
                route(cls.create)

            """ DELETE /resource/{id}
            Use "delete" method (if exists) to create the chalice endpoint
            This method only validate if exists the object and retrieve it.
            The logic to delete / deactivate is completely your responsibility.
            """
            if hasattr(cls, 'delete'):
                route = self.delete(path + '/{id}')

                @copy_attributes(cls)
                def delete(id: str):
                    model = self.retrieve_object(cls, id)
                    return cls.delete(model)

                route(delete)

            """ PATCH /resource/{id}
            Enable PATCH method if Resource.update method exist. It validates
            body data using `Resource.update_validator` but update logic is
            completely your responsibility.
            """
            if hasattr(cls, 'update'):
                route = self.patch(path + '/{id}')

                @copy_attributes(cls)
                def update(id: str):
                    params = self.current_request.json_body or dict()
                    try:
                        data = cls.update_validator(**params)
                    except ValidationError as e:
                        return Response(e.json(), status_code=400)

                    model = self.retrieve_object(cls, id)
                    return cls.update(model, data)

                route(update)

            @self.get(path + '/{id}')
            @copy_attributes(cls)
            def retrieve(id: str):
                """GET /resource/{id}
                :param id: Object Id
                :return: Model object

                If exists "retrieve" method return the result of that, else
                use "id" param to retrieve the object of type "model" defined
                in the decorated class.

                The most of times this implementation is enough and is not
                necessary define a custom "retrieve" method
                """
                obj = self.retrieve_object(cls, id)

                # This case is when the return is not an application/$
                # but can be some type of file such as image, xml, zip or pdf
                if hasattr(cls, 'download'):
                    file = cls.download(obj)
                    mimetype = cast(
                        str, self.current_request.headers.get('accept')
                    )
                    extension = mimetypes.guess_extension(mimetype)
                    filename = f'{cls.model._class_name}.{extension}'
                    result = Response(
                        body=file.read(),
                        headers={
                            'Content-Type': mimetype,
                            'Content-Disposition': (
                                'attachment; ' f'filename={filename}'
                            ),
                        },
                        status_code=200,
                    )
                elif hasattr(cls, 'retrieve'):
                    result = cls.retrieve(obj)
                else:
                    result = obj.to_dict()

                return result

            @self.get(path)
            @copy_attributes(cls)
            def query():
                """GET /resource
                Method for queries in resource. Use "query_validator" type
                defined in decorated class to validate the params.

                The "get_query_filter" method defined in decorated class
                should provide the way that the params are used to filter data

                If param "count" is True return the next response
                {
                    count:<count>
                }

                else the response is like this
                {
                    items = [{},{},...]
                    next_page = <url_for_next_items>
                }
                """
                params = self.current_request.query_params or dict()
                try:
                    query_params = cls.query_validator(**params)
                except ValidationError as e:
                    return Response(e.json(), status_code=400)

                if self.platform_id_filter_required() and hasattr(
                    cls.model, 'platform_id'
                ):
                    query_params.platform_id = self.current_platform_id

                if self.user_id_filter_required() and hasattr(
                    cls.model, 'user_id'
                ):
                    query_params.user_id = self.current_user_id

                filters = cls.get_query_filter(query_params)
                if (
                    hasattr(query_params, 'active')
                    and query_params.active is not None
                ):
                    filters &= Q(
                        deactivated_at__exists=not query_params.active
                    )
                if query_params.count:
                    result = _count(filters)
                elif hasattr(cls, 'query'):
                    result = cls.query(_all(query_params, filters))
                else:
                    result = _all(query_params, filters)
                return result

            def _count(filters: Q):
                count = cls.model.objects.filter(filters).count()
                return dict(count=count)

            def _all(query: QueryParams, filters: Q):
                if query.limit:
                    limit = min(query.limit, query.page_size)
                    query.limit = max(0, query.limit - limit)  # type: ignore
                else:
                    limit = query.page_size
                items = (
                    cls.model.objects.order_by("-created_at")
                    .filter(filters)
                    .limit(limit)
                )
                item_dicts = [i.to_dict() for i in items]

                has_more: Optional[bool] = None
                if wants_more := query.limit is None or query.limit > 0:
                    # only perform this query if it's necessary
                    has_more = items.limit(limit + 1).count() > limit

                next_page_uri: Optional[str] = None
                if wants_more and has_more:
                    query.created_before = item_dicts[-1]['created_at']
                    path = self.current_request.context['resourcePath']
                    params = query.dict()
                    if self.user_id_filter_required():
                        params.pop('user_id')
                    if self.platform_id_filter_required():
                        params.pop('platform_id')
                    next_page_uri = f'{path}?{urlencode(params)}'
                return dict(items=item_dicts, next_page_uri=next_page_uri)

            return cls

        return wrapper_resource_class
