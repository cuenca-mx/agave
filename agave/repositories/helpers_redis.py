from rom import Column


class String(Column):
    """
    No utilizo la clase String de rom porque todo lo maneja en bytes
    codificado en latin-1.
    """

    _allowed = str

    def _to_redis(self, value):
        return value.encode('utf-8')

    def _from_redis(self, value):
        return value.decode('utf-8')
