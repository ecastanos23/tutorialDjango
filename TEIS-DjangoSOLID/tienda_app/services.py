import logging

from django.shortcuts import get_object_or_404

from .domain.builders import OrdenBuilder
from .domain.logic import CalculadorImpuestos
from .models import Inventario, Libro

logger_compras = logging.getLogger('compras')


class CompraService:
    """
    SERVICE LAYER: Orquesta la interacción entre el dominio,
    la infraestructura y la base de datos.
    """

    def __init__(self, procesador_pago):
        self.procesador_pago = procesador_pago
        self.builder = OrdenBuilder()

    def obtener_detalle_producto(self, libro_id):
        libro = get_object_or_404(Libro, id=libro_id)
        # Consulta fresca a la BD en cada request: no se cachea el queryset.
        inv = Inventario.objects.filter(libro=libro).first()
        total = CalculadorImpuestos.obtener_total_con_iva(libro.precio)
        return {"libro": libro, "total": total, "stock": inv.cantidad if inv else 0}

    def ejecutar_compra(self, libro_id, cantidad=1, direccion="", usuario=None):
        libro = get_object_or_404(Libro, id=libro_id)
        inv = get_object_or_404(Inventario, libro=libro)

        if inv.cantidad < cantidad:
            raise ValueError("No hay suficiente stock para completar la compra.")

        # Representamos la cantidad como una lista de productos para el Builder
        lista_productos = [libro] * cantidad
        orden = (
            self.builder
            .con_usuario(usuario)
            .con_productos(lista_productos)
            .para_envio(direccion)
            .build()
        )

        if not self.procesador_pago.pagar(orden.total):
            orden.delete()
            raise Exception("Error en la pasarela de pagos.")

        inv.cantidad -= cantidad
        inv.save()

        logger_compras.info(
            "producto=%s cantidad=%s usuario=%s orden_id=%s stock_restante=%s",
            libro.titulo, cantidad, usuario if usuario else 'anonimo', orden.id, inv.cantidad,
        )

        return {
            "orden_id": orden.id,
            "libro_id": libro.id,
            "cantidad": cantidad,
            "total": orden.total,
            "stock_restante": inv.cantidad,
        }

    def ejecutar_proceso_compra(self, usuario, lista_productos, direccion):
        # Uso del Builder: Semantica clara y validacion interna
        orden = (
            self.builder
            .con_usuario(usuario)
            .con_productos(lista_productos)
            .para_envio(direccion)
            .build()
        )

        # Uso del Factory (inyectado): Cambio de comportamiento sin cambio de codigo
        if self.procesador_pago.pagar(orden.total):
            return f"Orden {orden.id} procesada exitosamente."

        orden.delete()
        raise Exception("Error en la pasarela de pagos.")


class CompraRapidaService:
    def __init__(self, procesador_pago):
        self.procesador_pago = procesador_pago

    def obtener_detalle(self, libro_id):
        libro = Libro.objects.get(id=libro_id)
        total = CalculadorImpuestos.obtener_total_con_iva(libro.precio)
        return {"libro": libro, "total": total}

    def procesar(self, libro_id):
        libro = Libro.objects.get(id=libro_id)
        inv = Inventario.objects.get(libro=libro)

        if inv.cantidad <= 0:
            raise ValueError("No hay existencias.")

        total = CalculadorImpuestos.obtener_total_con_iva(libro.precio)

        if self.procesador_pago.pagar(total):
            inv.cantidad -= 1
            inv.save()
            return total

        return None
