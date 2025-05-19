from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import Pago, Alquiler, Cliente
from ..serializers import PagoSerializer
from django.shortcuts import get_object_or_404
from utils import verificar_estado_pago_alquiler

class RegistrarPagoView(APIView):
    def post(self, request):
        id_alquiler = request.data.get('id_alquiler')
        metodo_pago = request.data.get('metodo_pago')
        monto = request.data.get('monto')

        if not all([id_alquiler, metodo_pago, monto]):
            return Response(
                {"error": "Faltan campos obligatorios."},
                status=status.HTTP_400_BAD_REQUEST
            )

        alquiler = get_object_or_404(Alquiler, id=id_alquiler)

        pago = Pago.objects.create(
            alquiler=alquiler,
            monto=monto,
            metodo_pago=metodo_pago,
            estado_pago='pagado' if float(monto) >= alquiler.precio_total else 'parcial',
        )

   
        verificar_estado_pago_alquiler(alquiler)

        return Response(PagoSerializer(pago).data, status=status.HTTP_201_CREATED)


# 2. Registrar pago parcial
class RegistrarPagoParcialView(APIView):
    def post(self, request):
        id_alquiler = request.data.get('id_alquiler')
        monto = request.data.get('monto')

        alquiler = get_object_or_404(Alquiler, id=id_alquiler)

        pago = Pago.objects.create(
            alquiler=alquiler,
            monto=monto,
            metodo_pago='transferencia',  # puedes permitirlo como parámetro
            estado_pago='parcial',
        )

        return Response(PagoSerializer(pago).data, status=status.HTTP_201_CREATED)



class PagosPendientesView(APIView):
    def get(self, request, id_cliente):
        pagos = Pago.objects.filter(alquiler__cliente__id=id_cliente, estado_pago='pendiente')
        serializer = PagoSerializer(pagos, many=True)
        return Response(serializer.data)

class GenerarFacturaView(APIView):
    def post(self, request, id_pago):
        pago = get_object_or_404(Pago, id=id_pago)
        pago.factura_generada = True
        pago.save()
        return Response({"mensaje": f"Factura generada para el pago #{pago.id}"})


class PasarelaPagoView(APIView):
    def post(self, request):
        id_cliente = request.data.get('id_cliente')
        id_alquiler = request.data.get('id_alquiler')
        monto = request.data.get('monto')
        url = f"https://fake-pasarela.com/pagar?cliente={id_cliente}&alquiler={id_alquiler}&monto={monto}"
        return Response({"url_pago": url})

def bloquear_cliente_por_pagos(id_cliente):
    pagos_pendientes = Pago.objects.filter(alquiler__cliente__id=id_cliente, estado_pago='pendiente').exists()

    if pagos_pendientes:
        cliente = Cliente.objects.get(id=id_cliente)
        cliente.estado_verificacion = 'Rechazado'  # o puedes usar un campo `activo=False`
        cliente.save()

class TotalPagadoAlquilerView(APIView):
    def get(self, request, id_alquiler):
        pagos = Pago.objects.filter(alquiler__id=id_alquiler)
        total = sum(p.monto for p in pagos)
        return Response({"alquiler": id_alquiler, "total_pagado": total})

def verificar_estado_pago_alquiler(alquiler):
    pagos = Pago.objects.filter(alquiler=alquiler)
    total_pagado = sum([p.monto for p in pagos])

    if total_pagado >= alquiler.precio_total:
        alquiler.estado_alquiler = 'Finalizado'
        alquiler.save()
        pagos.update(estado_pago='pagado')


def verificar_estado_pago_alquiler(alquiler):
    pagos = Pago.objects.filter(alquiler=alquiler)
    total_pagado = sum([p.monto for p in pagos])

    if total_pagado >= alquiler.precio_total:
        alquiler.estado_alquiler = 'Finalizado'
        alquiler.save()
        pagos.update(estado_pago='pagado')
