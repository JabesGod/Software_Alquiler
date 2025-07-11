# alquiler/serializers.py
from rest_framework import serializers
from .models import Cliente, Alquiler, Pago, Equipo

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'

class AlquilerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alquiler
        fields = '__all__'

class PagoSerializer(serializers.ModelSerializer):
    alquiler_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Pago
        fields = [
            'alquiler_id', 'monto', 'metodo_pago', 
            'referencia_transaccion', 'comprobante_pago'
        ]
        extra_kwargs = {
            'monto': {'min_value': 0.01},
            'referencia_transaccion': {'required': False},
            'comprobante_pago': {'required': False}
        }

class PagoDetalleSerializer(serializers.ModelSerializer):
    alquiler = serializers.StringRelatedField()
    cliente = serializers.SerializerMethodField()
    aprobado_por = serializers.StringRelatedField()
    estado_display = serializers.SerializerMethodField()
    metodo_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Pago
        fields = [
            'id', 'alquiler', 'cliente', 'monto', 'metodo_pago', 'metodo_display',
            'estado_pago', 'estado_display', 'fecha_pago', 'fecha_vencimiento',
            'referencia_transaccion', 'aprobado_por', 'factura_generada',
            'comprobante_pago', 'notas'
        ]
    
    def get_cliente(self, obj):
        return obj.alquiler.cliente.nombre
    
    def get_estado_display(self, obj):
        return obj.get_estado_pago_display()
    
    def get_metodo_display(self, obj):
        return obj.get_metodo_pago_display()

class EquipoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipo
        fields = '__all__'
