import datetime
import os

from ..domain.interfaces import ProcesadorPago

class BancoNacionalProcesador(ProcesadorPago):
    """
    Implementación concreta de la infraestructura.
    Simula un banco local escribiendo en un log.
    """
    def pagar(self, monto: float) -> bool:
        archivo_log = os.getenv("AUDIT_LOG_FILE", "pagos_locales_EMMANUEL_CASTANO.log")

        # Simulamos una operación de red o persistencia externa
        with open(archivo_log, "a") as f:
            f.write(f"[{datetime.datetime.now()}] BANCO NACIONAL - Cobro procesado: ${monto}\n")
        return True