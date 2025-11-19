"""
Simulador de Bases de Datos Municipales
Genera datos aleatorios consistentes basados en el RUT del usuario
"""
import hashlib
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List


class MunicipalDatabaseSimulator:
    """
    Simula consultas a bases de datos municipales.
    Usa el RUT como semilla para generar datos consistentes.
    """
    
    def __init__(self, rut: str):
        """
        Inicializa el simulador con un RUT específico.
        El RUT se usa como semilla para mantener consistencia.
        """
        self.rut = rut
        # Usar RUT como semilla para random (datos consistentes por usuario)
        self.seed = int(hashlib.md5(rut.encode()).hexdigest()[:8], 16)
        random.seed(self.seed)
    
    def consultar_licencia_conducir(self) -> Dict[str, Any]:
        """
        Simula consulta a base de datos de Licencias de Conducir
        """
        tiene_licencia = random.choice([True, True, True, False])  # 75% tiene licencia
        
        if not tiene_licencia:
            return {
                "tiene_licencia": False,
                "mensaje": "No se encontró registro de licencia de conducir"
            }
        
        clases = ["B", "A1", "A2", "A3", "A4", "A5", "C", "D", "E"]
        clase = random.choice(clases)
        
        # Fecha de otorgamiento (entre 1 y 10 años atrás)
        años_antigüedad = random.randint(1, 10)
        fecha_otorgamiento = datetime.now() - timedelta(days=años_antigüedad * 365)
        
        # Fecha de vencimiento (licencias vencen cada 2-6 años)
        años_vigencia = random.randint(2, 6)
        fecha_vencimiento = fecha_otorgamiento + timedelta(days=años_vigencia * 365)
        
        # Determinar si está vigente o vencida
        vigente = fecha_vencimiento > datetime.now()
        
        # Puntos (parten en 0, aumentan con multas)
        puntos = random.randint(0, 20) if random.random() > 0.7 else 0
        
        # Multas pendientes
        multas_pendientes = random.randint(0, 3) if random.random() > 0.6 else 0
        monto_multas = multas_pendientes * random.randint(15000, 120000)
        
        # Tipo de licencia
        tipo = random.choice(["Primer Otorgamiento", "Renovación", "Renovación"])
        
        return {
            "tiene_licencia": True,
            "numero_licencia": f"LIC-{self.rut[:8]}-{random.randint(100, 999)}",
            "clase": clase,
            "tipo": tipo,
            "fecha_otorgamiento": fecha_otorgamiento.strftime("%Y-%m-%d"),
            "fecha_vencimiento": fecha_vencimiento.strftime("%Y-%m-%d"),
            "vigente": vigente,
            "estado": "VIGENTE" if vigente else "VENCIDA",
            "puntos": puntos,
            "restricciones": random.choice([
                "Uso de lentes ópticos",
                "Sin restricciones",
                "Solo con acompañante",
                "Sin restricciones"
            ]),
            "multas_pendientes": multas_pendientes,
            "monto_multas": monto_multas,
            "ultima_revision_medica": (datetime.now() - timedelta(days=random.randint(30, 700))).strftime("%Y-%m-%d")
        }
    
    def consultar_permisos_edificacion(self) -> List[Dict[str, Any]]:
        """
        Simula consulta a base de datos de Permisos de Edificación
        """
        tiene_permisos = random.choice([True, True, False])  # 67% tiene permisos
        
        if not tiene_permisos:
            return []
        
        num_permisos = random.randint(1, 3)
        permisos = []
        
        tipos_permiso = [
            "Permiso de Obra Menor",
            "Permiso de Obra Mayor",
            "Permiso de Demolición",
            "Permiso de Subdivisión",
            "Permiso de Instalación de Ascensor",
            "Permiso de Modificación de Fachada"
        ]
        
        estados = ["Aprobado", "En Revisión", "Pendiente de Documentación", "Rechazado", "Finalizado"]
        
        for i in range(num_permisos):
            fecha_solicitud = datetime.now() - timedelta(days=random.randint(30, 730))
            estado = random.choice(estados)
            
            permiso = {
                "numero_permiso": f"PE-{random.randint(1000, 9999)}-{datetime.now().year}",
                "tipo": random.choice(tipos_permiso),
                "direccion": f"{random.choice(['Av. Principal', 'Calle Los Robles', 'Pasaje Las Flores', 'Av. Libertador'])} #{random.randint(100, 9999)}",
                "fecha_solicitud": fecha_solicitud.strftime("%Y-%m-%d"),
                "estado": estado,
                "monto_pagado": random.randint(50000, 500000),
                "inspector_asignado": random.choice(["Juan Pérez", "María González", "Carlos Soto", "Ana Martínez"]),
                "observaciones": "Revisar planos en terreno" if estado == "En Revisión" else "Conforme"
            }
            permisos.append(permiso)
        
        return permisos
    
    def consultar_patentes_comerciales(self) -> List[Dict[str, Any]]:
        """
        Simula consulta a base de datos de Patentes Comerciales
        """
        tiene_patentes = random.choice([True, True, False])  # 67% tiene patentes
        
        if not tiene_patentes:
            return []
        
        num_patentes = random.randint(1, 2)
        patentes = []
        
        giros = [
            "Almacén y Rotisería",
            "Peluquería y Barbería",
            "Minimarket",
            "Taller Mecánico",
            "Restaurant",
            "Oficina Profesional",
            "Librería y Papelería",
            "Ferretería",
            "Panadería",
            "Centro de Estética"
        ]
        
        for i in range(num_patentes):
            fecha_inicio = datetime.now() - timedelta(days=random.randint(180, 1825))
            fecha_vencimiento = datetime.now() + timedelta(days=random.randint(30, 365))
            vigente = fecha_vencimiento > datetime.now()
            
            # Deuda acumulada (algunos tienen deuda)
            tiene_deuda = random.choice([True, False, False])
            deuda = random.randint(50000, 300000) if tiene_deuda else 0
            
            patente = {
                "numero_patente": f"PAT-{random.randint(10000, 99999)}",
                "giro": random.choice(giros),
                "nombre_comercial": f"Empresa {random.choice(['Los Andes', 'El Bosque', 'La Estrella', 'San José'])}",
                "direccion": f"{random.choice(['Av. Comercial', 'Calle del Centro', 'Paseo Peatonal'])} #{random.randint(100, 999)}",
                "fecha_inicio": fecha_inicio.strftime("%Y-%m-%d"),
                "fecha_vencimiento": fecha_vencimiento.strftime("%Y-%m-%d"),
                "vigente": vigente,
                "estado": "VIGENTE" if vigente else "POR RENOVAR",
                "monto_anual": random.randint(100000, 800000),
                "deuda_acumulada": deuda,
                "ultima_inspeccion": (datetime.now() - timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d")
            }
            patentes.append(patente)
        
        return patentes
    
    def consultar_jpl_multas(self) -> List[Dict[str, Any]]:
        """
        Simula consulta a Juzgado de Policía Local (JPL)
        """
        tiene_multas = random.choice([True, True, False])  # 67% tiene multas
        
        if not tiene_multas:
            return []
        
        num_multas = random.randint(1, 4)
        multas = []
        
        infracciones = [
            "Estacionamiento indebido",
            "Exceso de velocidad",
            "No respetar señal de PARE",
            "Conducir sin cinturón",
            "Uso de celular al conducir",
            "No respetar luz roja",
            "Ruidos molestos",
            "Alteración del orden público",
            "Construcción sin permiso"
        ]
        
        for i in range(num_multas):
            fecha_infraccion = datetime.now() - timedelta(days=random.randint(30, 365))
            pagada = random.choice([True, False])
            
            monto = random.choice([0.5, 1.0, 1.5, 2.0, 3.0]) * 45000  # En UTM
            
            multa = {
                "numero_causa": f"JPL-{random.randint(1000, 9999)}-{datetime.now().year}",
                "fecha_infraccion": fecha_infraccion.strftime("%Y-%m-%d"),
                "infraccion": random.choice(infracciones),
                "monto": int(monto),
                "pagada": pagada,
                "estado": "PAGADA" if pagada else "PENDIENTE",
                "fecha_vencimiento": (fecha_infraccion + timedelta(days=30)).strftime("%Y-%m-%d") if not pagada else None
            }
            multas.append(multa)
        
        return multas
    
    def consultar_servicio_aseo(self) -> Dict[str, Any]:
        """
        Simula consulta a Servicio de Aseo Municipal
        """
        propiedades = random.randint(0, 2)
        
        if propiedades == 0:
            return {
                "tiene_servicio": False,
                "mensaje": "No se encontraron propiedades registradas"
            }
        
        # Estado de pago
        al_dia = random.choice([True, True, False])  # 66% al día
        meses_deuda = 0 if al_dia else random.randint(1, 6)
        monto_deuda = meses_deuda * random.randint(5000, 15000)
        
        return {
            "tiene_servicio": True,
            "numero_cliente": f"ASEO-{random.randint(100000, 999999)}",
            "propiedades_registradas": propiedades,
            "direcciones": [
                f"{random.choice(['Av. Los Álamos', 'Calle Principal', 'Pasaje Verde'])} #{random.randint(100, 9999)}"
                for _ in range(propiedades)
            ],
            "al_dia": al_dia,
            "estado": "AL DÍA" if al_dia else "MOROSO",
            "meses_deuda": meses_deuda,
            "monto_deuda": monto_deuda,
            "tipo_servicio": random.choice(["Residencial", "Comercial"]),
            "frecuencia_recoleccion": random.choice(["3 veces por semana", "Diaria", "Interdiaria"]),
            "ultimo_pago": (datetime.now() - timedelta(days=random.randint(15, 90))).strftime("%Y-%m-%d") if al_dia else None
        }
    
    def consultar_todas_las_bases(self) -> Dict[str, Any]:
        """
        Consulta todas las bases de datos municipales y retorna un resumen completo
        """
        return {
            "rut": self.rut,
            "fecha_consulta": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "licencia_conducir": self.consultar_licencia_conducir(),
            "permisos_edificacion": self.consultar_permisos_edificacion(),
            "patentes_comerciales": self.consultar_patentes_comerciales(),
            "multas_jpl": self.consultar_jpl_multas(),
            "servicio_aseo": self.consultar_servicio_aseo()
        }


def simular_consulta_municipal(rut: str) -> Dict[str, Any]:
    """
    Función principal para simular consulta a bases municipales
    """
    simulator = MunicipalDatabaseSimulator(rut)
    return simulator.consultar_todas_las_bases()
