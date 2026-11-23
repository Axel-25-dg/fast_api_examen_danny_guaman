# app/materias.py — primera parte
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.datos import RUTAS
from app.esquemas import Ruta, RutaActualizar, RutaCrear, ProyeccionIngresos, CoberturaConductor

router = APIRouter(prefix="/rutas", tags=["rutas"])


def obtener_ruta(codigo: str) -> dict:
    """Devuelve el diccionario de la ruta o lanza 404."""
    for ruta in RUTAS:
        if ruta["codigo"] == codigo.upper():
            return ruta
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No existe la ruta'{codigo}'",
    )


RutaEncontrada = Annotated[dict, Depends(obtener_ruta)]


@router.get("", response_model=list[Ruta])
def listar_rutas(
    zona: Annotated[int | None, Query(ge=1, le=8)] = None,
    nocturna: bool = False,
) -> list[dict]:
    resultado = RUTAS
    if zona is not None:
        resultado = [m for m in resultado if m["zona"] == zona]
    if nocturna:
        resultado = [m for m in resultado if m["nocturna"]]
    return resultado

@router.get("/proyeccion-ingresos", response_model=ProyeccionIngresos)
def calcular_proyeccion_ingresos(
frecuencias: Annotated[int, Query(ge=1, le=20)],
zona: Annotated[int | None, Query(ge=1, le=8)] = None,
) -> dict:
    seleccion = RUTAS if zona is None else [r for r in RUTAS if r["zona"] == zona]
    
    if not seleccion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay rutas que coincidan con el filtro aplicado",
            )
        suma_tarifas_base = 0
        suma_tarifas_con_recargo = 0.0
        rutas_con_recargo = 0
        
    for ruta in seleccion:
        tarifa = ruta["tarifa"]
        suma_tarifas_base += tarifa
        if ruta["nocturna"]:
           suma_tarifas_con_recargo += tarifa * 1.20
           rutas_con_recargo += 1
        else:
            suma_tarifas_con_recargo += tarifa


    cantidad = len(seleccion)
    tarifa_promedio = round(suma_tarifas_base / cantidad, 2)
    ingreso_diario = round(suma_tarifas_con_recargo * frecuencias, 2)
    porcentaje_nocturnas = round((rutas_con_recargo / cantidad) * 100, 1)


    return {
        "rutas": cantidad,
        "frecuencias": frecuencias,
        "tarifa_promedio": tarifa_promedio,
        "ingreso_diario": ingreso_diario,
        "rutas_con_recargo": rutas_con_recargo,
        "porcentaje_nocturnas": porcentaje_nocturnas,
        }


@router.get("/cobertura-conductor", response_model=CoberturaConductor)
def calcular_cobertura_conductor(
    asignadas: Annotated[list[str] | None, Query()] = None,
) -> dict:
    if not RUTAS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No existen rutas registradas",
        )


    codigos_asignados: set[str] = (
        {cod.upper() for cod in asignadas} if asignadas else set()
    )


    total = 0
    coincidencias = 0
    pendientes = 0
    tarifa_pendiente_total = 0
    pendiente_mas_cara: str | None = None
    mayor_tarifa_pendiente = -1


    for ruta in RUTAS:
        total += 1
        codigo = ruta["codigo"]
        tarifa = ruta["tarifa"]


        if codigo in codigos_asignados:
            coincidencias += 1
        else:
            pendientes += 1
            tarifa_pendiente_total += tarifa
        if tarifa > mayor_tarifa_pendiente:
            mayor_tarifa_pendiente = tarifa
            pendiente_mas_cara = codigo


    porcentaje_cobertura = round((coincidencias / total) * 100, 1)


    return {
        "total": total,
        "asignadas": coincidencias,
        "pendientes": pendientes,
        "porcentaje_cobertura": porcentaje_cobertura,
        "tarifa_pendiente_total": tarifa_pendiente_total,
        "pendiente_mas_cara": pendiente_mas_cara,
    }

@router.post("", response_model=Ruta, status_code=status.HTTP_201_CREATED)
def crear_rutas(nueva: RutaCrear) -> dict:
    if any(m["codigo"] == nueva.codigo for m in RUTAS):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"La ruta '{nueva.codigo}' ya existe",
        )
    RUTAS.append(nueva.model_dump())
    return RUTAS[-1]


@router.get("/{codigo}", response_model=Ruta)
def ver_ruta(ruta: RutaEncontrada) -> dict:
    return ruta


@router.put("/{codigo}", response_model=Ruta)
def actualizar_ruta(cambios: RutaActualizar, ruta: RutaEncontrada) -> dict:
    ruta.update(cambios.model_dump(exclude_unset=True))
    return ruta


@router.delete("/{codigo}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_ruta(ruta: RutaEncontrada) -> None:
    RUTAS.remove(ruta)