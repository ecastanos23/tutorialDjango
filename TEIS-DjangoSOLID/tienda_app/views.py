from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views import View

from .infra.factories import PaymentFactory
from .models import Libro
from .services import CompraRapidaService, CompraService


class CompraView(View):
    """
    CBV: Vista Basada en Clases.
    Actúa como un "Portero": recibe la petición y delega al servicio.
    """

    template_name = 'tienda_app/compra.html'

    def setup_service(self):
        gateway = PaymentFactory.get_processor()
        return CompraService(procesador_pago=gateway)

    def get(self, request, libro_id):
        servicio = self.setup_service()
        contexto = servicio.obtener_detalle_producto(libro_id)
        return render(request, self.template_name, contexto)

    def post(self, request, libro_id):
        servicio = self.setup_service()
        try:
            usuario = request.user if request.user.is_authenticated else None
            resultado = servicio.ejecutar_compra(libro_id, cantidad=1, usuario=usuario)
            return render(
                request,
                self.template_name,
                {
                    'mensaje_exito': f"¡Gracias por su compra! Total: ${resultado['total']}",
                    'total': resultado['total'],
                    'stock': resultado['stock_restante'],
                },
            )
        except (ValueError, Exception) as e:
            return render(request, self.template_name, {'error': str(e)}, status=400)


class CompraRapidaView(View):
    template_name = 'tienda_app/compra_rapida.html'

    def setup_service(self):
        gateway = PaymentFactory.get_processor()
        return CompraRapidaService(procesador_pago=gateway)

    def get(self, request, libro_id):
        servicio = self.setup_service()
        contexto = servicio.obtener_detalle(libro_id)
        return render(request, self.template_name, contexto)

    def post(self, request, libro_id):
        servicio = self.setup_service()
        try:
            total = servicio.procesar(libro_id)
            if total is None:
                return HttpResponse("Error", status=400)
            return HttpResponse("Comprado via CBV")
        except ValueError as e:
            return HttpResponse(str(e), status=400)
