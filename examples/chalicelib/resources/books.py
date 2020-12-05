from typing import List

from cuenca_validations.types import QueryParams

from ..models import Book as BookModel
from .base import app


@app.resource('/books')
class Book:
    def query(self, query_params: QueryParams) -> List[BookModel]:
        return [
            BookModel(
                name='Twenty Thousand Leagues Under the Sea',
                author='Jules Verne',
            ),
            BookModel(
                name='Journey to the Center of the Earth', author='Jules Verne'
            ),
            BookModel(
                name='Around the World in Eighty Days', author='Jules Verne'
            ),
        ]
