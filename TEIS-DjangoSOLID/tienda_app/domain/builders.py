from decimal import Decimal

from ..models import Orden


class OrdenBuilder:
    """Ensambla una Orden paso a paso (patron Builder)."""

    def __init__(self):
        self.reset()

    def reset(self):
        self._usuario = None
        self._items = []
        self._direccion = ""

    def con_usuario(self, usuario):
        self._usuario = usuario
        return self  # Permite Fluent Interface

    def con_productos(self, productos):
        self._items = productos
        return self

    def para_envio(self, direccion):
        self._direccion = direccion
        return self

    def build(self) -> Orden:
        if not self._usuario or not self._items:
            raise ValueError("Datos insuficientes para crear la orden.")

        # Encapsulamos la logica de calculo
        subtotal = sum((Decimal(str(p.precio)) for p in self._items), Decimal("0"))
        total_con_iva = subtotal * Decimal("1.19")

        orden = Orden.objects.create(
            usuario=self._usuario,
            # El modelo actual liga la orden a un libro; usamos el primero de la lista
            libro=self._items[0],
            total=total_con_iva,
            direccion_envio=self._direccion,
        )
        self.reset()
        return orden
