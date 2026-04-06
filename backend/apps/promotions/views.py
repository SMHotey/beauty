import io
from rest_framework import viewsets, permissions, mixins, serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.http import FileResponse
from apps.promotions.models import Promotion, GiftCertificate, BlacklistedClient
from apps.promotions.serializers import (
    PromotionSerializer,
    GiftCertificateSerializer,
    GiftCertificateCreateSerializer,
    BlacklistedClientSerializer,
)


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class PromotionViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = PromotionSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['discount_percent']
    ordering_fields = ['start_date', 'end_date', 'discount_percent']
    ordering = ['-start_date']

    def get_queryset(self):
        return Promotion.objects.filter(
            start_date__lte=timezone.now().date(),
            end_date__gte=timezone.now().date(),
        ).prefetch_related('applicable_services')

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [IsAdminUser()]


class GiftCertificateViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_used']

    def get_queryset(self):
        return GiftCertificate.objects.all().order_by('-created_at')

    def get_serializer_class(self):
        if self.action == 'create':
            return GiftCertificateCreateSerializer
        return GiftCertificateSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [IsAdminUser()]

    def perform_create(self, serializer):
        certificate = serializer.save()
        return certificate

    @action(detail=True, methods=['get'], url_path='pdf')
    def pdf(self, request, pk=None):
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.lib.colors import HexColor
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER

        certificate = self.get_object()
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=40*mm)
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='CertTitle', fontSize=28, textColor=HexColor('#8B5A2B'), alignment=TA_CENTER, spaceAfter=20))
        styles.add(ParagraphStyle(name='CertNominal', fontSize=36, textColor=HexColor('#333'), alignment=TA_CENTER, spaceAfter=20))
        styles.add(ParagraphStyle(name='CertCode', fontSize=14, textColor=HexColor('#666'), alignment=TA_CENTER, spaceAfter=10))
        styles.add(ParagraphStyle(name='CertDetail', fontSize=12, textColor=HexColor('#888'), alignment=TA_CENTER))

        elements = []
        elements.append(Spacer(1, 60*mm))
        elements.append(Paragraph('ПОДАРОЧНЫЙ СЕРТИФИКАТ', styles['CertTitle']))
        elements.append(Spacer(1, 10*mm))
        elements.append(Paragraph(f'{certificate.nominal} ₽', styles['CertNominal']))
        elements.append(Spacer(1, 10*mm))
        elements.append(Paragraph(f'Код: {certificate.code}', styles['CertCode']))
        elements.append(Spacer(1, 5*mm))
        elements.append(Paragraph(f'Получатель: {certificate.recipient_email}', styles['CertDetail']))
        elements.append(Paragraph(f'Покупатель: {certificate.buyer_name}', styles['CertDetail']))

        doc.build(elements)
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=f'certificate_{certificate.code}.pdf', content_type='application/pdf')


class BlacklistedClientViewSet(viewsets.ModelViewSet):
    serializer_class = BlacklistedClientSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['client']
    search_fields = ['client__phone', 'reason']

    def get_queryset(self):
        return BlacklistedClient.objects.select_related('client').order_by('-created_at')

    def create(self, request, *args, **kwargs):
        from apps.clients.models import Client
        client_id = request.data.get('client')
        phone = request.data.get('phone')
        if client_id:
            client = Client.objects.filter(id=client_id).first()
            if not client:
                raise serializers.ValidationError({'client': 'Клиент не найден.'})
        elif phone:
            client = Client.objects.filter(phone=phone).first()
            if not client:
                raise serializers.ValidationError({'phone': 'Клиент с таким номером не найден.'})
        else:
            raise serializers.ValidationError({'client': 'Поле client или phone обязательно.'})
        if BlacklistedClient.objects.filter(client=client).exists():
            raise serializers.ValidationError({'client': 'Клиент уже в чёрном списке.'})
        entry = BlacklistedClient.objects.create(
            client=client,
            reason=request.data.get('reason', ''),
        )
        serializer = self.get_serializer(entry)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
