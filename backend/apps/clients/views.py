from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import serializers
from apps.clients.models import Client, FavoriteMaster
from apps.clients.serializers import ClientSerializer, FavoriteMasterSerializer


class ClientProfileViewSet(viewsets.GenericViewSet):
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Client.objects.filter(user=self.request.user)

    def get_object(self):
        client = self.get_queryset().first()
        if not client:
            # Auto-create client profile for authenticated users without one
            client = Client.objects.create(user=self.request.user, phone='')
        return client

    @action(detail=False, methods=['get'])
    def me(self, request):
        client = self.get_object()
        if not client:
            return Response(
                {'detail': 'Профиль клиента не найден.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(client)
        return Response(serializer.data)

    @action(detail=False, methods=['patch'])
    def update_me(self, request):
        client = self.get_object()
        if not client:
            return Response(
                {'detail': 'Профиль клиента не найден.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(client, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class FavoriteMasterViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteMasterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        client = Client.objects.filter(user=self.request.user).first()
        if not client:
            return FavoriteMaster.objects.none()
        return FavoriteMaster.objects.filter(client=client).select_related('master__user')

    def perform_create(self, serializer):
        client = Client.objects.filter(user=self.request.user).first()
        if not client:
            raise serializers.ValidationError({'detail': 'Профиль клиента не найден.'})
        master_id = self.request.data.get('master')
        if FavoriteMaster.objects.filter(client=client, master_id=master_id).exists():
            raise serializers.ValidationError({'detail': 'Мастер уже в избранном.'})
        serializer.save(client=client)
