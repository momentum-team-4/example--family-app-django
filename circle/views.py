from rest_framework.views import APIView, Response
from rest_framework.permissions import IsAuthenticated


class ExampleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"ok": True})
