"""
Knowledge Base del Sistema de Reservas de Licencias de Conducir
Contiene información estructurada sobre trámites, requisitos y procedimientos
"""

KNOWLEDGE_BASE = {
    "sistema": {
        "nombre": "Sistema de Reservas para Licencias de Conducir",
        "descripcion": "Plataforma municipal para gestión de citas y documentación digital",
        "horarios": "Lunes a Viernes: 8:30 - 17:30, Sábados: 9:00 - 13:00"
    },
    
    "licencias": {
        "clase_b": {
            "nombre": "Licencia Clase B",
            "descripcion": "Para automóviles, station wagons y camionetas hasta 3,500 kg",
            "requisitos": [
                "Ser mayor de 18 años",
                "Cédula de identidad vigente",
                "Certificado médico (disponible en el municipio)",
                "Examen psicotécnico (disponible en el municipio)",
                "Certificado de antecedentes",
                "2 fotografías tamaño carnet",
                "Comprobante de pago de tasas municipales"
            ],
            "documentos_digitales": [
                "Cédula de identidad (escaneada)",
                "Certificado de antecedentes (PDF)",
                "Fotografías digitales"
            ],
            "duracion_tramite": "Aproximadamente 30 minutos",
            "costo": "$25.000 (tasas municipales + exámenes)"
        },
        "clase_a": {
            "nombre": "Licencia Clase A (Profesional)",
            "descripcion": "Para vehículos de transporte de pasajeros y carga",
            "requisitos": [
                "Tener licencia clase B con al menos 2 años de antigüedad",
                "Ser mayor de 21 años",
                "Cédula de identidad vigente",
                "Certificado médico especial para conductor profesional",
                "Examen psicotécnico avanzado",
                "Certificado de antecedentes",
                "2 fotografías tamaño carnet",
                "Curso de conducción profesional aprobado",
                "Comprobante de pago de tasas"
            ],
            "duracion_tramite": "Aproximadamente 45 minutos",
            "costo": "$45.000 (tasas municipales + exámenes especiales)"
        },
        "renovacion": {
            "nombre": "Renovación de Licencia",
            "descripcion": "Renovación de licencia existente antes de su vencimiento",
            "requisitos": [
                "Licencia anterior (original)",
                "Cédula de identidad vigente",
                "Certificado médico actualizado",
                "1 fotografía tamaño carnet",
                "Comprobante de pago de tasas"
            ],
            "nota": "Se recomienda renovar con 60 días de anticipación al vencimiento",
            "duracion_tramite": "Aproximadamente 20 minutos",
            "costo": "$15.000"
        },
        "duplicado": {
            "nombre": "Duplicado de Licencia",
            "descripcion": "Por pérdida, robo o deterioro de la licencia",
            "requisitos": [
                "Denuncia policial (en caso de robo o pérdida)",
                "Cédula de identidad vigente",
                "Licencia deteriorada (si aplica)",
                "1 fotografía tamaño carnet",
                "Comprobante de pago de tasas"
            ],
            "duracion_tramite": "Aproximadamente 15 minutos",
            "costo": "$12.000"
        }
    },
    
    "proceso_reserva": {
        "pasos": [
            "1. Iniciar sesión o registrarse en el sistema",
            "2. Seleccionar el tipo de trámite (Primera licencia, Renovación, etc.)",
            "3. Elegir fecha y hora disponible en el calendario",
            "4. Subir documentación digital requerida (si es primera vez)",
            "5. Confirmar la reserva",
            "6. Recibir correo de confirmación con código QR",
            "7. Presentarse el día de la cita con documentos originales"
        ],
        "cancelacion": "Puede cancelar hasta 24 horas antes de su cita desde el menú de reservas",
        "reprogramacion": "Puede reprogramar hasta 48 horas antes de la cita",
        "consejos": [
            "Reserve con anticipación, especialmente en temporada alta (verano)",
            "Llegue 10 minutos antes de su hora reservada",
            "Traiga todos los documentos originales",
            "El sistema le recordará su cita 24 horas antes por email"
        ]
    },
    
    "navegacion": {
        "login": "Ingrese con su email y contraseña en la página principal",
        "registro": "Haga clic en 'Registrarse' y complete con email, nombre y RUT",
        "menu_principal": "Después de iniciar sesión verá: Reservas, Documentos, y Mi Perfil",
        "crear_reserva": "Ir a Menú → Reservas → Nueva Reserva",
        "ver_reservas": "Ir a Menú → Reservas para ver todas sus citas",
        "subir_documentos": "Ir a Menú → Documentos → Subir Archivo",
        "cambiar_contrasena": "Ir a Mi Perfil → Cambiar Contraseña"
    },
    
    "documentos_digitales": {
        "formatos_aceptados": ["PDF", "JPG", "JPEG", "PNG"],
        "tamano_maximo": "5 MB por archivo",
        "calidad": "Las imágenes deben ser legibles, sin cortes ni manipulación",
        "tipos": {
            "cedula": "Foto clara de ambos lados de la cédula de identidad",
            "certificado_antecedentes": "PDF emitido por Registro Civil (no mayor a 30 días)",
            "foto_carnet": "Fotografía reciente, fondo blanco, rostro visible",
            "certificado_medico": "Firmado y timbrado por médico autorizado",
            "comprobante_pago": "Voucher o comprobante de transferencia bancaria"
        }
    },
    
    "horarios_atencion": {
        "oficina": {
            "lunes_viernes": "8:30 AM - 5:30 PM",
            "sabado": "9:00 AM - 1:00 PM",
            "domingo": "Cerrado"
        },
        "sistema_online": "24/7 (puede reservar en cualquier momento)",
        "examen_practico": "Solo mañanas (9:00 AM - 1:00 PM)",
        "examen_teorico": "Mañana y tarde (9:00 AM - 5:00 PM)"
    },
    
    "preguntas_frecuentes": [
        {
            "pregunta": "¿Cuánto tiempo demora obtener la licencia?",
            "respuesta": "Una vez completados todos los requisitos, la licencia física se entrega el mismo día. El proceso completo (exámenes + trámite) puede tomar de 2 a 4 horas."
        },
        {
            "pregunta": "¿Puedo cambiar mi hora de reserva?",
            "respuesta": "Sí, puede reprogramar hasta 48 horas antes de su cita desde el menú de Reservas en el sistema."
        },
        {
            "pregunta": "¿Qué pasa si llego tarde?",
            "respuesta": "Hay una tolerancia de 15 minutos. Después de ese tiempo, su reserva se marca como 'no presentado' y deberá agendar nuevamente."
        },
        {
            "pregunta": "¿Necesito llevar documentos físicos si ya los subí al sistema?",
            "respuesta": "Sí, debe presentar los documentos originales el día de la cita. Los documentos digitales son para pre-validación."
        },
        {
            "pregunta": "¿Cómo pago las tasas municipales?",
            "respuesta": "Puede pagar en caja de la municipalidad o mediante transferencia bancaria. Debe presentar el comprobante el día de la cita."
        },
        {
            "pregunta": "¿Puedo sacar licencia si tengo multas pendientes?",
            "respuesta": "No, debe regularizar todas las multas de tránsito antes de obtener o renovar su licencia."
        },
        {
            "pregunta": "¿El examen médico lo hacen en la municipalidad?",
            "respuesta": "Sí, contamos con médico municipal. Puede solicitar hora para examen médico al momento de reservar."
        },
        {
            "pregunta": "¿Cuándo vence mi licencia?",
            "respuesta": "Puede verificar la fecha de vencimiento en el sistema, sección 'Mis Documentos' o en su licencia física."
        }
    ],
    
    "soporte_tecnico": {
        "problemas_comunes": [
            {
                "problema": "No puedo iniciar sesión",
                "solucion": "Verifique su email y contraseña. Use la opción 'Recuperar Contraseña' si es necesario."
            },
            {
                "problema": "No veo fechas disponibles",
                "solucion": "Intente con fechas más adelante. Las horas se liberan 30 días antes."
            },
            {
                "problema": "Error al subir documento",
                "solucion": "Verifique que el archivo sea menor a 5MB y en formato PDF, JPG o PNG."
            },
            {
                "problema": "No recibí el email de confirmación",
                "solucion": "Revise su carpeta de spam. Puede ver su reserva en el sistema en 'Mis Reservas'."
            }
        ],
        "contacto": {
            "email": "soporte@municipalidad.cl",
            "telefono": "+56 2 2345 6789",
            "horario": "Lunes a Viernes 9:00 - 18:00"
        }
    }
}

def get_knowledge_context() -> str:
    """
    Genera un contexto resumido de la knowledge base para el modelo de IA
    OPTIMIZADO: Contexto reducido para minimizar uso de RAM y tokens
    """
    context = """
Eres un asistente del Sistema de Licencias de Conducir Municipal.

**ALCANCE LIMITADO - SOLO RESPONDE SOBRE:**
1. Requisitos para licencias (Clase A, B, renovación, duplicado)
2. Proceso de reserva en el sistema
3. Documentos necesarios
4. Horarios de atención
5. Navegación básica del sistema

**NO RESPONDAS** sobre temas generales, noticias, código, matemáticas u otros temas.

LICENCIAS:
- Clase B: Autos (18+, $25.000)
- Clase A: Profesional (21+, $45.000)
- Renovación: $15.000
- Duplicado: $12.000

REQUISITOS BÁSICOS:
- Cédula vigente, certificado médico, antecedentes, fotos, comprobante pago

RESERVA:
1. Login → 2. Tipo trámite → 3. Fecha/hora → 4. Subir docs → 5. Confirmar

HORARIOS: L-V 8:30-17:30, Sáb 9:00-13:00

Si la pregunta NO es sobre licencias de conducir, responde:
"Solo puedo ayudar con consultas sobre licencias de conducir y el sistema de reservas. Contacta soporte: soporte@municipalidad.cl"

Sé breve (máximo 3 párrafos).
"""
    return context

def search_knowledge(query: str) -> dict:
    """
    Busca información relevante en la knowledge base según la consulta
    """
    query_lower = query.lower()
    relevant_info = {}
    
    # Búsqueda por palabras clave
    keywords_map = {
        "clase b": ["licencias", "clase_b"],
        "clase a": ["licencias", "clase_a"],
        "profesional": ["licencias", "clase_a"],
        "renovación": ["licencias", "renovacion"],
        "renovar": ["licencias", "renovacion"],
        "duplicado": ["licencias", "duplicado"],
        "perdida": ["licencias", "duplicado"],
        "reserva": ["proceso_reserva"],
        "reservar": ["proceso_reserva"],
        "cita": ["proceso_reserva"],
        "documentos": ["documentos_digitales"],
        "subir": ["documentos_digitales"],
        "archivo": ["documentos_digitales"],
        "horario": ["horarios_atencion"],
        "navegación": ["navegacion"],
        "como usar": ["navegacion"],
        "login": ["navegacion", "login"],
        "iniciar sesión": ["navegacion", "login"],
        "registro": ["navegacion", "registro"],
        "soporte": ["soporte_tecnico"],
        "error": ["soporte_tecnico"],
        "problema": ["soporte_tecnico"],
    }
    
    # Buscar secciones relevantes
    for keyword, sections in keywords_map.items():
        if keyword in query_lower:
            for section in sections:
                if section in KNOWLEDGE_BASE:
                    relevant_info[section] = KNOWLEDGE_BASE[section]
    
    # Si no se encontró nada específico, incluir preguntas frecuentes
    if not relevant_info and any(word in query_lower for word in ["?", "como", "qué", "cuál", "dónde", "cuando"]):
        relevant_info["preguntas_frecuentes"] = KNOWLEDGE_BASE["preguntas_frecuentes"]
    
    return relevant_info if relevant_info else {"sistema": KNOWLEDGE_BASE["sistema"]}
