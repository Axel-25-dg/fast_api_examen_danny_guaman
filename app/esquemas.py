from pydantic import BaseModel, Field


from pydantic import BaseModel, Field


class RutaBase(BaseModel):
    nombre: str = Field(min_length=3, max_length=60)
    tarifa: int = Field(ge=1, le=100)
    zona: int = Field(ge=1, le=8)
    nocturna: bool = False


class RutaCrear(RutaBase):
    # Tres letras mayúsculas + tres dígitos: MAT101, PRG201...
    codigo: str = Field(pattern=r"^[A-Z]{3}\d{3}$")


class RutaActualizar(BaseModel):
    # Todos opcionales: en un PUT parcial, lo que no se envía no se toca.
    nombre: str | None = Field(default=None, min_length=3, max_length=60)
    tarifa: int | None = Field(default=None, ge=1, le=100)
    zona: int | None = Field(default=None, ge=1, le=8)
    nocturna: bool | None = None


class Ruta(RutaCrear):
    """Lo que la API devuelve: los cinco campos completos."""

class ProyeccionIngresos(BaseModel):
    rutas: int
    frecuencias: int
    tarifa_promedio: float
    ingreso_diario: float
    rutas_con_recargo: int
    porcentaje_nocturnas: float


class CoberturaConductor(BaseModel):
    total: int
    asignadas: int
    pendientes: int
    porcentaje_cobertura: float
    tarifa_pendiente_total: int
    pendiente_mas_cara: str | None