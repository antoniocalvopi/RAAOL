from rest_framework.response import Response
from rest_framework import status

def _error_response(message, status=status.HTTP_400_BAD_REQUEST):
        """ Devuelve mensaje de error.

        Args:
            message (str): mensaje de error a devolver

        Returns:
            Response: devuelve codigo de error HTTP 400 junto con JSON, con el mensaje de error.
        """
        return Response({"error": message}, status=status)