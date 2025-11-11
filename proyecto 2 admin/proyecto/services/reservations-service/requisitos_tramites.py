"""
📋 CONFIGURACIÓN DE REQUISITOS POR TIPO DE TRÁMITE (RF05)

Define qué requisitos debe cumplir un ciudadano para poder realizar cada tipo de trámite,
basándose en sus datos municipales.
"""

# =============================================================================
# CONFIGURACIÓN DE REQUISITOS
# =============================================================================

REQUISITOS_POR_TRAMITE = {
    # =========================================================================
    # PRIMER OTORGAMIENTO - CLASES NO PROFESIONALES
    # =========================================================================
    "primer_otorg_clase_b": {
        "nombre": "Primer Otorgamiento - Clase B (Autos)",
        "categoria": "primer_otorgamiento",
        "requisitos": [
            {
                "campo": "jpl_multas_pendientes",
                "operador": "==",
                "valor": 0,
                "mensaje": "❌ No puede obtener licencia con multas pendientes del Juzgado de Policía Local",
                "tipo": "bloqueante"
            },
            {
                "campo": "aseo_estado_pago",
                "operador": "==",
                "valor": "al_dia",
                "mensaje": "⚠️ Tiene deudas pendientes en servicio de aseo",
                "tipo": "advertencia"
            }
        ],
        "documentos_requeridos": [
            "Certificado de educación básica",
            "Cédula de identidad vigente",
            "Certificado de residencia",
            "Declaración jurada"
        ]
    },
    
    "primer_otorg_clase_c": {
        "nombre": "Primer Otorgamiento - Clase C (Motos)",
        "categoria": "primer_otorgamiento",
        "requisitos": [
            {
                "campo": "jpl_multas_pendientes",
                "operador": "==",
                "valor": 0,
                "mensaje": "❌ No puede obtener licencia con multas pendientes del JPL",
                "tipo": "bloqueante"
            }
        ],
        "documentos_requeridos": [
            "Certificado de educación básica",
            "Cédula de identidad vigente",
            "Certificado de residencia",
            "Declaración jurada"
        ]
    },
    
    "primer_otorg_clase_cr": {
        "nombre": "Primer Otorgamiento - Clase CR (Triciclos Motorizados)",
        "categoria": "primer_otorgamiento",
        "requisitos": [
            {
                "campo": "jpl_multas_pendientes",
                "operador": "==",
                "valor": 0,
                "mensaje": "❌ No puede obtener licencia con multas pendientes",
                "tipo": "bloqueante"
            }
        ],
        "documentos_requeridos": [
            "Cédula de identidad vigente",
            "Certificado de residencia",
            "Declaración jurada"
        ]
    },
    
    "primer_otorg_clase_b_17": {
        "nombre": "Primer Otorgamiento - Clase B para 17 años",
        "categoria": "primer_otorgamiento",
        "requisitos": [
            {
                "campo": "jpl_multas_pendientes",
                "operador": "==",
                "valor": 0,
                "mensaje": "❌ No puede obtener licencia con multas pendientes",
                "tipo": "bloqueante"
            }
        ],
        "documentos_requeridos": [
            "Certificado de educación básica",
            "Cédula de identidad vigente",
            "Certificado de residencia",
            "Declaración jurada",
            "Autorización notarial de ambos padres",
            "Certificado de escuela de conductores acreditada"
        ]
    },
    
    # =========================================================================
    # PRIMER OTORGAMIENTO - CLASES ESPECIALES
    # =========================================================================
    "primer_otorg_clase_d": {
        "nombre": "Primer Otorgamiento - Clase D (Maquinaria)",
        "categoria": "primer_otorgamiento",
        "requisitos": [
            {
                "campo": "jpl_multas_pendientes",
                "operador": "==",
                "valor": 0,
                "mensaje": "❌ No puede obtener licencia con multas pendientes",
                "tipo": "bloqueante"
            }
        ],
        "documentos_requeridos": [
            "Cédula de identidad vigente",
            "Certificado de residencia",
            "Declaración jurada"
        ]
    },
    
    "primer_otorg_clase_e": {
        "nombre": "Primer Otorgamiento - Clase E (Tracción Animal)",
        "categoria": "primer_otorgamiento",
        "requisitos": [],
        "documentos_requeridos": [
            "Cédula de identidad vigente",
            "Certificado de residencia",
            "Declaración jurada"
        ]
    },
    
    "primer_otorg_clase_f": {
        "nombre": "Primer Otorgamiento - Clase F",
        "categoria": "primer_otorgamiento",
        "requisitos": [],
        "documentos_requeridos": [
            "Cédula de identidad vigente",
            "Certificado de residencia",
            "Declaración jurada"
        ]
    },
    
    # =========================================================================
    # PRIMER OTORGAMIENTO - CLASES PROFESIONALES
    # =========================================================================
    "primer_otorg_clase_a1": {
        "nombre": "Primer Otorgamiento - Clase A1 (Taxis)",
        "categoria": "primer_otorgamiento_profesional",
        "requisitos": [
            {
                "campo": "jpl_multas_pendientes",
                "operador": "==",
                "valor": 0,
                "mensaje": "❌ No puede obtener licencia profesional con multas pendientes",
                "tipo": "bloqueante"
            },
            {
                "campo": "aseo_estado_pago",
                "operador": "==",
                "valor": "al_dia",
                "mensaje": "❌ Debe estar al día con pagos municipales",
                "tipo": "bloqueante"
            }
        ],
        "documentos_requeridos": [
            "Certificado de escuela de conductores",
            "Cédula de identidad vigente",
            "Certificado de residencia",
            "Declaración jurada"
        ]
    },
    
    "primer_otorg_clase_a2": {
        "nombre": "Primer Otorgamiento - Clase A2 (Transporte Pasajeros Medianos)",
        "categoria": "primer_otorgamiento_profesional",
        "requisitos": [
            {
                "campo": "jpl_multas_pendientes",
                "operador": "==",
                "valor": 0,
                "mensaje": "❌ No puede obtener licencia profesional con multas pendientes",
                "tipo": "bloqueante"
            }
        ],
        "documentos_requeridos": [
            "Certificado de escuela de conductores",
            "Cédula de identidad vigente",
            "Certificado de residencia",
            "Declaración jurada"
        ]
    },
    
    "primer_otorg_clase_a3": {
        "nombre": "Primer Otorgamiento - Clase A3 (Buses)",
        "categoria": "primer_otorgamiento_profesional",
        "requisitos": [
            {
                "campo": "jpl_multas_pendientes",
                "operador": "==",
                "valor": 0,
                "mensaje": "❌ No puede obtener licencia profesional con multas pendientes",
                "tipo": "bloqueante"
            }
        ],
        "documentos_requeridos": [
            "Certificado de escuela de conductores",
            "Cédula de identidad vigente",
            "Certificado de residencia",
            "Declaración jurada"
        ]
    },
    
    "primer_otorg_clase_a4": {
        "nombre": "Primer Otorgamiento - Clase A4 (Camiones Simples)",
        "categoria": "primer_otorgamiento_profesional",
        "requisitos": [
            {
                "campo": "jpl_multas_pendientes",
                "operador": "==",
                "valor": 0,
                "mensaje": "❌ No puede obtener licencia profesional con multas pendientes",
                "tipo": "bloqueante"
            }
        ],
        "documentos_requeridos": [
            "Certificado de escuela de conductores",
            "Cédula de identidad vigente",
            "Certificado de residencia",
            "Declaración jurada"
        ]
    },
    
    "primer_otorg_clase_a5": {
        "nombre": "Primer Otorgamiento - Clase A5 (Camiones Articulados)",
        "categoria": "primer_otorgamiento_profesional",
        "requisitos": [
            {
                "campo": "jpl_multas_pendientes",
                "operador": "==",
                "valor": 0,
                "mensaje": "❌ No puede obtener licencia profesional con multas pendientes",
                "tipo": "bloqueante"
            }
        ],
        "documentos_requeridos": [
            "Certificado de escuela de conductores",
            "Cédula de identidad vigente",
            "Certificado de residencia",
            "Declaración jurada"
        ]
    },
    
    # =========================================================================
    # CONTROL / RENOVACIÓN
    # =========================================================================
    "renovacion_licencia": {
        "nombre": "Renovación de Licencia de Conducir",
        "categoria": "renovacion",
        "requisitos": [
            {
                "campo": "jpl_multas_pendientes",
                "operador": "==",
                "valor": 0,
                "mensaje": "❌ No puede renovar licencia con multas pendientes del Juzgado de Policía Local",
                "tipo": "bloqueante"
            },
            {
                "campo": "licencia_multas_pendientes",
                "operador": "==",
                "valor": 0,
                "mensaje": "⚠️ Tiene multas de tránsito pendientes. Se recomienda pagarlas antes de renovar",
                "tipo": "advertencia"
            },
            {
                "campo": "aseo_estado_pago",
                "operador": "==",
                "valor": "al_dia",
                "mensaje": "⚠️ Tiene deudas pendientes en servicio de aseo",
                "tipo": "advertencia"
            }
        ],
        "documentos_requeridos": [
            "Cédula de identidad vigente",
            "Declaración jurada"
        ]
    },
    
    "duplicado_licencia": {
        "nombre": "Duplicado de Licencia de Conducir",
        "categoria": "duplicado",
        "requisitos": [
            {
                "campo": "licencia_vigente",
                "operador": "==",
                "valor": True,
                "mensaje": "⚠️ Debe tener una licencia vigente para solicitar duplicado",
                "tipo": "advertencia"
            }
        ],
        "documentos_requeridos": [
            "Cédula de identidad vigente"
        ]
    },
    
    "canje_licencia_extranjera": {
        "nombre": "Canje de Licencia Extranjera",
        "categoria": "canje",
        "requisitos": [
            {
                "campo": "jpl_multas_pendientes",
                "operador": "==",
                "valor": 0,
                "mensaje": "❌ No puede realizar canje con multas pendientes",
                "tipo": "bloqueante"
            }
        ],
        "documentos_requeridos": [
            "Cédula de identidad vigente",
            "Declaración jurada",
            "Certificado de canje del MTT",
            "Licencia extranjera original"
        ]
    },
    
    "licencia_diplomatico": {
        "nombre": "Licencia de Diplomático",
        "categoria": "especial",
        "requisitos": [],
        "documentos_requeridos": [
            "Licencia de conducir vigente (extranjera)",
            "Documento que acredite calidad de diplomático"
        ]
    },
    
    "cambio_domicilio": {
        "nombre": "Cambio de Domicilio",
        "categoria": "modificacion",
        "requisitos": [],
        "documentos_requeridos": [
            "Cédula de identidad vigente",
            "Certificado de residencia"
        ]
    },
    
    "cambio_restriccion": {
        "nombre": "Cambio de Restricción",
        "categoria": "modificacion",
        "requisitos": [],
        "documentos_requeridos": [
            "Cédula de identidad vigente",
            "Declaración jurada"
        ]
    },
    
    # =========================================================================
    # OTROS TRÁMITES MUNICIPALES
    # =========================================================================
    "licencia_conducir": {
        "nombre": "Licencia de Conducir (General)",
        "categoria": "general",
        "requisitos": [
            {
                "campo": "jpl_multas_pendientes",
                "operador": "==",
                "valor": 0,
                "mensaje": "❌ No puede realizar trámites de licencia con multas pendientes",
                "tipo": "bloqueante"
            }
        ],
        "documentos_requeridos": [
            "Cédula de Identidad vigente",
            "Documentos según tipo de trámite"
        ]
    },
    
    "permiso_circulacion": {
        "nombre": "Permiso de Circulación",
        "requisitos": [
            {
                "campo": "jpl_multas_pendientes",
                "operador": "==",
                "valor": 0,
                "mensaje": "❌ No puede obtener permiso de circulación con multas pendientes",
                "tipo": "bloqueante"
            },
            {
                "campo": "aseo_estado_pago",
                "operador": "==",
                "valor": "al_dia",
                "mensaje": "❌ Debe estar al día con el servicio de aseo domiciliario",
                "tipo": "bloqueante"
            }
        ],
        "documentos_requeridos": [
            "Cédula de Identidad",
            "Certificado de revisión técnica vigente",
            "Certificado de seguro obligatorio (SOAP)",
            "Padrón del vehículo"
        ]
    },
    
    "certificado_residencia": {
        "nombre": "Certificado de Residencia",
        "requisitos": [
            {
                "campo": "permisos_construccion",
                "operador": "exists",
                "mensaje": "✅ Se verificará su dirección registrada en permisos de construcción",
                "tipo": "informativo"
            }
        ],
        "documentos_requeridos": [
            "Cédula de Identidad",
            "Cuenta de luz, agua o gas (últimos 3 meses)"
        ]
    },
    
    "patente_comercial": {
        "nombre": "Patente Comercial",
        "requisitos": [
            {
                "campo": "aseo_estado_pago",
                "operador": "==",
                "valor": "al_dia",
                "mensaje": "❌ Debe estar al día con el pago del servicio de aseo",
                "tipo": "bloqueante"
            },
            {
                "campo": "jpl_monto_total_deuda",
                "operador": "==",
                "valor": 0,
                "mensaje": "⚠️ Tiene deuda pendiente en el Juzgado de Policía Local",
                "tipo": "advertencia"
            },
            {
                "campo": "patentes_comerciales",
                "operador": "check_vigencia",
                "mensaje": "⚠️ Ya tiene patentes comerciales registradas. Verifique su vigencia",
                "tipo": "informativo"
            }
        ],
        "documentos_requeridos": [
            "Cédula de Identidad o RUT empresa",
            "Inicio de actividades (SII)",
            "Plano de ubicación del local",
            "Contrato de arriendo o escritura",
            "Autorización sanitaria (si corresponde)"
        ]
    },
    
    "permiso_edificacion": {
        "nombre": "Permiso de Edificación",
        "requisitos": [
            {
                "campo": "aseo_estado_pago",
                "operador": "==",
                "valor": "al_dia",
                "mensaje": "❌ Debe regularizar deudas municipales antes de solicitar permisos",
                "tipo": "bloqueante"
            },
            {
                "campo": "permisos_construccion",
                "operador": "check_pendientes",
                "mensaje": "⚠️ Tiene permisos de construcción en trámite. Revise su estado",
                "tipo": "advertencia"
            }
        ],
        "documentos_requeridos": [
            "Planos arquitectónicos firmados por arquitecto",
            "Planos de cálculo estructural",
            "Certificado de dominio vigente",
            "Plano de ubicación del terreno",
            "Memoria de cálculo",
            "Especificaciones técnicas"
        ]
    },
    
    "registro_civil": {
        "nombre": "Registro Civil",
        "requisitos": [],  # Sin requisitos previos
        "documentos_requeridos": [
            "Cédula de Identidad vigente",
            "Documentos específicos según el trámite"
        ]
    },
    
    "subsidios": {
        "nombre": "Subsidios Municipales",
        "requisitos": [
            {
                "campo": "aseo_estado_pago",
                "operador": "==",
                "valor": "al_dia",
                "mensaje": "⚠️ Se recomienda estar al día con pagos municipales",
                "tipo": "advertencia"
            }
        ],
        "documentos_requeridos": [
            "Cédula de Identidad",
            "Certificado de residencia",
            "Ficha de Protección Social",
            "Declaración jurada simple",
            "Comprobantes de ingresos"
        ]
    },
    
    "otros": {
        "nombre": "Otros Trámites",
        "requisitos": [],
        "documentos_requeridos": [
            "Cédula de Identidad",
            "Documentos según el trámite específico"
        ]
    }
}

# =============================================================================
# FUNCIONES DE VALIDACIÓN
# =============================================================================

def validar_requisitos_tramite(tipo_tramite: str, datos_municipales: dict) -> dict:
    """
    Valida si un ciudadano cumple los requisitos para realizar un trámite.
    
    Args:
        tipo_tramite: ID del tipo de trámite
        datos_municipales: Diccionario con los datos municipales del usuario
        
    Returns:
        {
            "puede_realizar": bool,
            "bloqueantes": [...],  # Requisitos no cumplidos que bloquean el trámite
            "advertencias": [...],  # Requisitos no cumplidos pero no bloquean
            "informativos": [...],  # Mensajes informativos
            "documentos_requeridos": [...]
        }
    """
    
    if tipo_tramite not in REQUISITOS_POR_TRAMITE:
        return {
            "puede_realizar": True,
            "bloqueantes": [],
            "advertencias": [],
            "informativos": [f"⚠️ Tipo de trámite '{tipo_tramite}' no configurado"],
            "documentos_requeridos": ["Cédula de Identidad"]
        }
    
    config = REQUISITOS_POR_TRAMITE[tipo_tramite]
    resultado = {
        "puede_realizar": True,
        "bloqueantes": [],
        "advertencias": [],
        "informativos": [],
        "documentos_requeridos": config["documentos_requeridos"]
    }
    
    for requisito in config["requisitos"]:
        cumple = evaluar_requisito(requisito, datos_municipales)
        
        if not cumple:
            if requisito["tipo"] == "bloqueante":
                resultado["bloqueantes"].append(requisito["mensaje"])
                resultado["puede_realizar"] = False
            elif requisito["tipo"] == "advertencia":
                resultado["advertencias"].append(requisito["mensaje"])
            elif requisito["tipo"] == "informativo":
                resultado["informativos"].append(requisito["mensaje"])
    
    return resultado


def evaluar_requisito(requisito: dict, datos_municipales: dict) -> bool:
    """
    Evalúa si se cumple un requisito específico.
    """
    campo = requisito["campo"]
    operador = requisito["operador"]
    
    # Obtener el valor del campo de los datos municipales
    valor_actual = obtener_valor_campo(campo, datos_municipales)
    
    if operador == "==":
        return valor_actual == requisito["valor"]
    elif operador == "!=":
        return valor_actual != requisito["valor"]
    elif operador == ">":
        return valor_actual > requisito["valor"]
    elif operador == "<":
        return valor_actual < requisito["valor"]
    elif operador == "exists":
        return valor_actual is not None and len(valor_actual) > 0 if isinstance(valor_actual, list) else valor_actual is not None
    elif operador == "check_vigencia":
        # Para patentes comerciales, verificar si hay alguna vigente
        if isinstance(valor_actual, list) and len(valor_actual) > 0:
            return any(p.get("estado") == "vigente" for p in valor_actual)
        return True  # Si no hay patentes, no aplica
    elif operador == "check_pendientes":
        # Para permisos de construcción, verificar si hay pendientes
        if isinstance(valor_actual, list) and len(valor_actual) > 0:
            return any(p.get("estado") == "en_tramite" for p in valor_actual)
        return True  # Si no hay permisos, no aplica
    
    return True


def obtener_valor_campo(campo: str, datos_municipales: dict) -> any:
    """
    Obtiene el valor de un campo específico de los datos municipales.
    """
    # Mapeo de campos a ubicación en los datos municipales
    if campo == "jpl_multas_pendientes":
        return len(datos_municipales.get("multas_jpl", []))
    elif campo == "jpl_monto_total_deuda":
        multas = datos_municipales.get("multas_jpl", [])
        return sum(m.get("monto", 0) for m in multas)
    elif campo == "licencia_multas_pendientes":
        return datos_municipales.get("licencia_conducir", {}).get("multas_pendientes", 0)
    elif campo == "aseo_estado_pago":
        return datos_municipales.get("servicio_aseo", {}).get("estado_pago", "al_dia")
    elif campo == "aseo_deuda_total":
        return datos_municipales.get("servicio_aseo", {}).get("deuda_total", 0)
    elif campo == "permisos_construccion":
        return datos_municipales.get("permisos_edificacion", [])
    elif campo == "patentes_comerciales":
        return datos_municipales.get("patentes_comerciales", [])
    
    return None
