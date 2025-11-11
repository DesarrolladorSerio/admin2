# Validación de Horarios - Sistema de Reservas

## 🕐 **Funcionalidad Implementada**

### **Objetivo**
Evitar conflictos de horarios en las reservas considerando la duración de cada tipo de trámite, para que no se puedan crear reservas que se solapen en el tiempo.

### **Lógica de Validación**

#### **Escenario Ejemplo:**
- Reserva A: 14:00 - Licencia de Conducir (30 minutos) → Ocupa hasta 14:30
- Reserva B: 14:20 - Cualquier trámite → **❌ NO PERMITIDO** (solapamiento)
- Reserva C: 14:30 - Cualquier trámite → **✅ PERMITIDO**

#### **Duraciones por Tipo de Trámite:**
- 🚗 Licencia de Conducir: **30 minutos**
- 🚗 Permiso de Circulación: **15 minutos**
- 🏠 Certificado de Residencia: **10 minutos**
- 🏪 Patente Comercial: **45 minutos**
- 🏗️ Permiso de Edificación: **60 minutos**
- 📄 Registro Civil: **20 minutos**
- 💰 Subsidios Municipales: **40 minutos**
- 📋 Otros Trámites: **30 minutos**

## 🔧 **Implementación Técnica**

### **Backend (FastAPI)**

#### **Función de Validación:**
```python
def check_time_conflict(session, fecha, hora, tipo_tramite, exclude_reservation_id=None):
    # Verifica solapamientos considerando:
    # 1. Hora de inicio y fin de la nueva reserva
    # 2. Hora de inicio y fin de reservas existentes
    # 3. Exclusión de reserva actual (para ediciones)
```

#### **Endpoints Afectados:**
- `POST /reservations` - Validación en creación
- `PUT /reservations/{id}` - Validación en edición
- `GET /check-availability/{fecha}/{hora}/{tipo_tramite}` - Verificación previa

#### **Códigos de Error:**
- `409 CONFLICT` - Horario ocupado o conflicto detectado
- `400 BAD REQUEST` - Datos inválidos

### **Frontend (React)**

#### **Validación en Tiempo Real:**
- ✅ Verificación automática al cambiar fecha/hora/tipo
- ✅ Indicador visual de disponibilidad
- ✅ Botón de envío deshabilitado si hay conflicto
- ✅ Delay de 500ms para evitar consultas excesivas

#### **Estados Visuales:**
- 🔄 **Verificando**: "Verificando disponibilidad..."
- ✅ **Disponible**: Fondo verde - "Horario disponible"
- ❌ **Ocupado**: Fondo rojo - "Horario ocupado o genera conflicto"

## 📋 **Casos de Uso Validados**

### **✅ Escenarios Permitidos:**
1. Reservas consecutivas sin solapamiento
2. Edición de reserva propia sin crear conflictos
3. Reservas en días diferentes (sin restricción)
4. Reservas con suficiente espacio entre horarios

### **❌ Escenarios Rechazados:**
1. Misma hora exacta para cualquier trámite
2. Hora de inicio dentro del rango de otra reserva
3. Hora de fin que solape con inicio de otra reserva
4. Cualquier solapamiento parcial de horarios

## 🚀 **Beneficios para el Usuario**

1. **Retroalimentación Inmediata**: Ve disponibilidad antes de enviar
2. **Prevención de Errores**: No puede crear reservas conflictivas
3. **Experiencia Fluida**: Validación en tiempo real
4. **Claridad Visual**: Estados claros de disponibilidad

## 🔄 **Flujo de Validación**

```
Usuario selecciona fecha/hora/trámite
    ↓
Frontend valida en tiempo real (500ms delay)
    ↓
API verifica conflictos en BD
    ↓
Respuesta visual al usuario
    ↓
Usuario puede/no puede enviar formulario
    ↓
Backend valida nuevamente antes de guardar
    ↓
Confirmación o error específico
```

## 🎯 **Resultado**

**Sistema robusto que garantiza:**
- ❌ Sin conflictos de horarios
- ✅ Experiencia de usuario mejorada  
- ✅ Validación dual (frontend + backend)
- ✅ Consideración de duraciones reales
- ✅ Edición segura de reservas existentes