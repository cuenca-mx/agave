def _validate_installation():
    try:
        import pkg_resources
        
        dist = pkg_resources.get_distribution('agave')
        extras = dist.extras
        if not extras or not any(extra in extras for extra in ['chalice_support', 'fast_support']):
            raise ImportError(
                "Agave debe ser instalado con uno de los siguientes extras:\n"
                "- pip install 'agave[chalice_support]'\n"
                "- pip install 'agave[fast_support]'"
            )
    except Exception as e:
        raise ImportError(
            "Agave debe ser instalado con uno de los siguientes extras:\n"
            "- pip install 'agave[chalice_support]'\n"
            "- pip install 'agave[fast_support]'"
        ) from e

_validate_installation()
