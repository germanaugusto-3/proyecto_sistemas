import abc
import logging
from typing import List

# ==================== CONFIGURACIÓN DE LOGS ====================
logging.basicConfig(
    filename='eventos.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

# ==================== EXCEPCIONES PERSONALIZADAS ====================
class CustomException(Exception):
    pass

class ClienteInvalidoError(CustomException):
    pass

class ServicioNoDisponibleError(CustomException):
    pass

class ReservaInvalidaError(CustomException):
    pass

class CalculoCostoError(CustomException):
    pass


# ==================== CLASE ABSTRACTA BASE ====================
class EntidadBase(abc.ABC):
    def __init__(self, id_entidad: str):
        self._id = id_entidad
    
    @abc.abstractmethod
    def obtener_info(self) -> str:
        pass


# ==================== CLIENTE ====================
class Cliente(EntidadBase):
    def __init__(self, id_cliente: str, nombre: str, email: str, telefono: str):
        super().__init__(id_cliente)
        self._nombre = self._validar_nombre(nombre)
        self._email = self._validar_email(email)
        self._telefono = self._validar_telefono(telefono)
        logging.info(f"Cliente creado exitosamente: {self._nombre} (ID: {id_cliente})")
    
    def _validar_nombre(self, nombre: str) -> str:
        if not nombre or len(nombre.strip()) < 3:
            raise ClienteInvalidoError("El nombre debe tener al menos 3 caracteres.")
        return nombre.strip()
    
    def _validar_email(self, email: str) -> str:
        if "@" not in email or "." not in email:
            raise ClienteInvalidoError("El email proporcionado no es válido.")
        return email.lower()
    
    def _validar_telefono(self, telefono: str) -> str:
        if len([c for c in telefono if c.isdigit()]) < 7:
            raise ClienteInvalidoError("El teléfono debe tener al menos 7 dígitos.")
        return telefono
    
    def obtener_info(self) -> str:
        return f"Cliente: {self._nombre} | Email: {self._email} | Tel: {self._telefono}"
    
    @property
    def nombre(self) -> str:
        return self._nombre


# ==================== SERVICIO ABSTRACTO ====================
class Servicio(abc.ABC):
    def __init__(self, id_servicio: str, nombre: str, precio_base: float):
        self._id = id_servicio
        self._nombre = nombre
        self._precio_base = max(0.0, precio_base)
    
    @abc.abstractmethod
    def calcular_costo(self, duracion: float, **kwargs) -> float:
        pass
    
    @abc.abstractmethod
    def describir(self) -> str:
        pass


class ReservaSala(Servicio):
    def __init__(self, id_servicio: str, capacidad: int = 10):
        super().__init__(id_servicio, "Reserva de Sala", 150.0)
        self.capacidad = max(1, capacidad)
    
    def calcular_costo(self, duracion: float, impuestos: float = 0.19, **kwargs) -> float:
        if duracion <= 0:
            raise CalculoCostoError("La duración debe ser mayor a 0 horas.")
        costo = self._precio_base * duracion * (1 + impuestos)
        return round(costo, 2)
    
    def describir(self) -> str:
        return f"Reserva de sala con capacidad para {self.capacidad} personas."


class AlquilerEquipo(Servicio):
    def __init__(self, id_servicio: str, tipo_equipo: str = "PC"):
        super().__init__(id_servicio, f"Alquiler de {tipo_equipo}", 75.0)
        self.tipo_equipo = tipo_equipo
    
    def calcular_costo(self, duracion: float, descuento: float = 0.0, **kwargs) -> float:
        if duracion <= 0:
            raise CalculoCostoError("La duración debe ser mayor a 0 horas.")
        desc = max(0.0, min(0.5, descuento))
        costo = self._precio_base * duracion * (1 - desc)
        return round(costo, 2)
    
    def describir(self) -> str:
        return f"Alquiler de equipo: {self.tipo_equipo}"


class AsesoriaEspecializada(Servicio):
    def __init__(self, id_servicio: str):
        super().__init__(id_servicio, "Asesoría Especializada", 220.0)
    
    def calcular_costo(self, duracion: float, **kwargs) -> float:
        if duracion < 0.5:
            raise CalculoCostoError("La asesoría debe durar mínimo 0.5 horas (30 minutos).")
        return round(self._precio_base * duracion, 2)
    
    def describir(self) -> str:
        return "Asesoría técnica especializada por experto senior."


# ==================== RESERVA ====================
class Reserva:
    def __init__(self, id_reserva: str, cliente: Cliente, servicio: Servicio, duracion: float):
        self.id_reserva = id_reserva
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = max(duracion, 1.0)
        self.estado = "PENDIENTE"
        logging.info(f"Reserva {id_reserva} creada para cliente {cliente.nombre}")
    
    def confirmar(self):
        try:
            if self.estado != "PENDIENTE":
                raise ReservaInvalidaError("Solo se pueden confirmar reservas en estado PENDIENTE.")
            self.estado = "CONFIRMADA"
            logging.info(f"Reserva {self.id_reserva} confirmada exitosamente.")
        except Exception as e:
            logging.error(f"Error al confirmar reserva {self.id_reserva}: {e}")
            raise
    
    def cancelar(self):
        try:
            if self.estado == "COMPLETADA":
                raise ReservaInvalidaError("No se puede cancelar una reserva ya completada.")
            self.estado = "CANCELADA"
            logging.info(f"Reserva {self.id_reserva} cancelada.")
        except Exception as e:
            logging.error(f"Error al cancelar reserva {self.id_reserva}: {e}")
            raise
    
    def procesar(self):
        try:
            if self.estado != "CONFIRMADA":
                raise ReservaInvalidaError("La reserva debe estar confirmada antes de procesarla.")
            costo = self.servicio.calcular_costo(self.duracion)
            self.estado = "COMPLETADA"
            logging.info(f"Reserva {self.id_reserva} procesada. Costo final: ${costo}")
            return costo
        except Exception as e:
            logging.error(f"Error procesando reserva {self.id_reserva}: {e}")
            raise


# ==================== SISTEMA PRINCIPAL ====================
class SistemaGestion:
    def __init__(self):
        self.clientes: List[Cliente] = []
        self.servicios: List[Servicio] = []
        self.reservas: List[Reserva] = []
        logging.info("=== Sistema de Gestión Software FJ iniciado correctamente ===")
    
    def registrar_cliente(self, id_cliente: str, nombre: str, email: str, telefono: str):
        try:
            cliente = Cliente(id_cliente, nombre, email, telefono)
            self.clientes.append(cliente)
            print(f"✓ Cliente registrado: {cliente.nombre}")
            return cliente
        except Exception as e:
            print(f"✗ Error al registrar cliente: {e}")
            logging.error(f"Error registrando cliente {id_cliente}: {e}")
            return None
    
    def crear_servicio(self, tipo: str, id_servicio: str, **kwargs):
        try:
            if tipo == "sala":
                serv = ReservaSala(id_servicio, **kwargs)
            elif tipo == "equipo":
                serv = AlquilerEquipo(id_servicio, **kwargs)
            elif tipo == "asesoria":
                serv = AsesoriaEspecializada(id_servicio)
            else:
                raise ServicioNoDisponibleError(f"Tipo de servicio desconocido: {tipo}")
            
            self.servicios.append(serv)
            print(f"✓ Servicio creado: {serv._nombre}")
            return serv
        except Exception as e:
            print(f"✗ Error al crear servicio: {e}")
            logging.error(str(e))
            return None
    
    def crear_reserva(self, id_reserva: str, cliente: Cliente, servicio: Servicio, duracion: float):
        try:
            if not cliente or not servicio:
                raise ReservaInvalidaError("Cliente y servicio son obligatorios.")
            reserva = Reserva(id_reserva, cliente, servicio, duracion)
            self.reservas.append(reserva)
            print(f"✓ Reserva creada: {id_reserva}")
            return reserva
        except Exception as e:
            print(f"✗ Error al crear reserva: {e}")
            logging.error(str(e))
            return None


# ==================== DEMOSTRACIÓN ====================
def main():
    print("=== SISTEMA INTEGRAL SOFTWARE FJ ===\n")
    sistema = SistemaGestion()
    
    # Operaciones de prueba
    c1 = sistema.registrar_cliente("C001", "Juan Pérez", "juan@empresa.com", "3001234567")
    sistema.registrar_cliente("C002", "A", "invalido", "123")   # Error intencional
    
    s1 = sistema.crear_servicio("sala", "S001", capacidad=20)
    s2 = sistema.crear_servicio("equipo", "S002", tipo_equipo="Laptop")
    s3 = sistema.crear_servicio("asesoria", "S003")
    
    if c1 and s1:
        r1 = sistema.crear_reserva("R001", c1, s1, 4)
        if r1:
            r1.confirmar()
            costo = r1.procesar()
            print(f"   Costo de la reserva: ${costo}")
    
    sistema.crear_reserva("R002", c1, s1, -5)   # Error intencional
    
    c2 = sistema.registrar_cliente("C003", "María López", "maria@test.com", "3109876543")
    
    if c2 and s2:
        r2 = sistema.crear_reserva("R003", c2, s2, 3)
        if r2:
            r2.confirmar()
            r2.procesar()
    
    print(f"\n--- RESUMEN FINAL ---")
    print(f"Clientes registrados : {len(sistema.clientes)}")
    print(f"Servicios creados    : {len(sistema.servicios)}")
    print(f"Reservas creadas     : {len(sistema.reservas)}")
    print("\n✅ Sistema ejecutado correctamente. Revisa el archivo 'eventos.log'")

if __name__ == "__main__":
    main()