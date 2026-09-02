import logging

from django.db import DatabaseError
from django.db.utils import InterfaceError, OperationalError, ProgrammingError
from django.http import JsonResponse
from django.shortcuts import render

logger = logging.getLogger(__name__)


class DatabaseUnavailableMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except (OperationalError, InterfaceError, DatabaseError, ProgrammingError) as exc:
            logger.exception(
                'Banco de dados indisponível na requisição %s %s: %s',
                request.method,
                request.path,
                str(exc),
            )

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
        except Exception as exc:
            # Captura erros de conexão do psycopg2/psycopg3 que possam não ser OperationalError
            exc_name = exc.__class__.__name__
            exc_module = exc.__class__.__module__

            if 'psycopg' in exc_module or 'connection' in str(exc).lower() or 'connect' in exc_name.lower():
                logger.exception(
                    'Erro de conexão com banco de dados na requisição %s %s: %s.%s - %s',
                    request.method,
                    request.path,
                    exc_module,
                    exc_name,
                    str(exc),
                )

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

            # Se não for erro de banco, deixa passar para ser tratado normalmente
            raise
