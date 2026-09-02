import logging
from django.shortcuts import render
from django.http import JsonResponse

logger = logging.getLogger(__name__)


def handler500(request, exception=None):
    """
    Tratamento customizado para erro 500.
    Detecta se o erro é relacionado ao banco de dados e retorna uma página amigável.
    """
    if exception:
        exc_name = exception.__class__.__name__
        exc_module = exception.__class__.__module__
        exc_str = str(exception)

        logger.error(
            'Error 500 na requisição %s %s: %s.%s - %s',
            request.method,
            request.path,
            exc_module,
            exc_name,
            exc_str,
        )

        # Detecta erros de banco de dados
        is_db_error = (
            'psycopg' in exc_module or
            'database' in exc_str.lower() or
            'connection' in exc_str.lower() or
            'connect' in exc_name.lower() or
            'operational' in exc_name.lower() or
            'interface' in exc_name.lower() or
            'timeout' in exc_str.lower()
        )

        if is_db_error:
            message = 'O banco de dados está indisponível no momento. Tente novamente em alguns instantes.'

            is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
            is_json = request.content_type == 'application/json'
            if is_ajax or is_json:
                return JsonResponse({
                    'success': False,
                    'message': message,
                    'error': 'database_unavailable',
                }, status=503)

            return render(
                request,
                'error/database_unavailable.html',
                {'message': message},
                status=503,
            )

    # Erro genérico 500
    return render(request, 'error/500.html', status=500)
