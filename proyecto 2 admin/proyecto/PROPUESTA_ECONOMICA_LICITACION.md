# 💰 PROPUESTA ECONÓMICA - SISTEMA MUNICIPAL DE RESERVACIONES CON IA





## 1. COSTOS DE DESARROLLO

### 1.1 Estructura y costo del equipo 

| Rol | Horas de Trabajo | Valor Hora | Subtotal CLP | Fuente |
|-----|----------------|-----------------|--------------|--------|
| **Arquitecto de Software Sr.** | 80 hrs | $12.290 | $983.200 | Ingeniero de software (Indeed) (se asume +50% por senior): https://cl.indeed.com/career/ingeniero-de-software/salaries |
| **Desarrollador Backend** | 120 hrs | $6.782 | $813.840 | Desarrollador/a de software (Indeed): https://cl.indeed.com/career/desarrollador-backend/salaries |
| **Desarrollador Frontend** | 100 hrs | $6.188 | $618.800 | Programador/a front end (Indeed): https://cl.indeed.com/career/desarrollador-frontend/salaries |
| **Especialista en DevOps** | 60 hrs | $10.696 | $641.760 | DevOps (Indeed): https://cl.indeed.com/career/devops-engineer/salaries |
| **Especialista en IA/ML** | 40 hrs | $11.686 | $467.440 | Data Scientist / IA (Indeed): https://cl.indeed.com/career/data-scientist/salaries |
| **QA/Testing Engineer** | 50 hrs | $7.276 | $363.800 | Quality assurance (Indeed): https://cl.indeed.com/career/quality-assurance-analyst/salaries |
| **Project Manager** | 70 hrs | $7.505 | $525.350 | Gestor/a de proyectos (Indeed): https://cl.indeed.com/career/project-manager/salaries |

**SUBTOTAL DESARROLLO:** **$4.414.190 CLP**
**TIEMPO ESTIMADO DEL PROYECTO:** **12 Semanas**


##  2. COSTOS DE INFRAESTRUCTURA (AÑO 1)

### 2.1 Servidores Cloud

| Componente | Especificaciones | Costo Mensual (CLP) | Costo Anual (CLP) | Fuente |
|------------|------------------|---------------:|-------------:|--------|
| **Servidor Principal** | 4 vCPU, 16GB RAM, 100GB SSD | $140.632 | $1.687.584 | Precio representativo VM (~USD 140/mo) promedio AWS/GCP/DigitalOcean + 100GB block storage; conversión USD→CLP: X‑Rates (USD=CLP 937.5446) — https://aws.amazon.com/ec2/pricing/ , https://cloud.google.com/compute/pricing , https://www.digitalocean.com/pricing/ , https://www.x-rates.com/table/?from=USD&amount=1 |
| **Servidor Base de Datos** | 2 vCPU, 8GB RAM, 200GB SSD | $84.379 | $1.012.548 | Precio representativo VM (~USD 90/mo) + 200GB block storage; fuentes: AWS/GCP pricing pages + X‑Rates conversion (links arriba) |
| **Servidor Monitoreo** | 2 vCPU, 4GB RAM, 50GB SSD | $46.877 | $562.524 | Precio representativo VM (~USD 50/mo) + 50GB storage; fuentes: AWS/GCP/DigitalOcean + X‑Rates |

**SUBTOTAL SERVIDORES:** **$271.888/mes - $3.262.656/año**

> Nota metodológica: para cada componente tomé un precio representativo de instancia (on‑demand) en proveedores públicos (AWS EC2, Google Compute, DigitalOcean) y añadí un costo de almacenamiento block (estimado en ~USD 0.10/GB‑mes). Convertí USD→CLP usando la tasa pública consultada en X‑Rates (1 USD ≈ 937.5446 CLP, consulta Nov 11, 2025). En las celdas "Fuente" se incluyen enlaces a las páginas de precios utilizadas. Para cotizaciones exactas por región/IOPS/tienda (gp3, SSD, snapshots) recomiendo usar las calculadoras oficiales (AWS Pricing Calculator / GCP Pricing Calculator / DigitalOcean pricing) y validar la conversión cambiaria bancaria al momento de la oferta.

### 2.2 Almacenamiento y Red

| Tipo | Capacidad | Costo Mensual | Costo Anual |
|------|-----------|---------------|-------------|
| **Almacenamiento** | 500GB | $12.000 | $144.000 |
| **Backups** | 200GB | $4.000 | $48.000 |


**SUBTOTAL RED: 16.000 CLP mensual - 192.000 CLP anual**

### 2.3 Ancho de banda
**Ancho de Banda de 1TB/mes:** **90.000 CLP mensual - 1.080.000 CLP anual**  


### 2.4 Licencias

| Software | Costo Anual |
|----------|-------------|
| **Stack Completo Open Source** | **$0** |

**TOTAL INFRAESTRUCTURA AÑO 1:** **$4.392.000 CLP**



## 3. COSTOS DE OPERACIÓN Y MANTENIMIENTO (ANUAL)

### 3.1 Soporte Técnico

| Nivel de Soporte | Horas Anuales | Tarifa CLP/Hora | Costo Anual |
|-------------------|---------------|-----------------|-------------|
| **Soporte L1** | 480 hrs | $25.000 | $12.000.000 |
| **Soporte L2 Crítico** | 48 hrs | $40.000 | $1.920.000 |

**SUBTOTAL SOPORTE:** **$13.920.000 CLP/año**

### 3.2 Mantenimiento y Actualizaciones

| Concepto | Costo Anual |
|----------|-------------|
| **Actualizaciones de Seguridad** | $1.200.000 |
| **Nuevas Funcionalidades** | $2.000.000 |
| **Monitoreo 24/7** | $600.000 |
| **Respaldos y Disaster Recovery** | $600.000 |

**SUBTOTAL MANTENIMIENTO:** **$4.400.000 CLP/año**

**TOTAL OPERACIÓN Y MANTENIMIENTO:** **$18.320.000 CLP/año**

---

## 4. COSTOS DE IA

### 4.1 Comparación de Alternativas

#### Solución Comercial (OpenAI/Claude)
| Concepto | Costo Anual |
|----------|-------------|
| **API Comercial** | $3.600.000-12.000.000 CLP |
| **Tokens limitados** | Costos adicionales |
| **Dependencia externa** | Costos por riesgo operacional |

#### Nuestra Solución (IA Local)
| Concepto | Costo Anual |
|----------|-------------|
| **Ollama + Llama 2** | **$0 CLP** |
| **Tokens ilimitados** | **$0 CLP** |
| **100% local** | **$0 CLP** |

### 4.2 Ahorro por IA Local
**AHORRO ANUAL ESTIMADO ~** **$3.600.000-15.000.000 CLP** 


## 💲 5. PRECIO FINAL DE LA PROPUESTA

### 5.1 Precio de Implementación (Una Vez)

| Concepto | Costo CLP |
|----------|-----------|
| **Desarrollo del Sistema** | $4.623.997 |
| **Setup e Instalación** | $2.000.000 |
| **Capacitación** | $1.500.000 |
| **Migración de Datos** | $1.200.000 |

**TOTAL IMPLEMENTACIÓN:** **$9.323.997 CLP**

### 5.2 Precio de Mantenimiento (Anual)

| Concepto | Costo CLP/año |
|----------|---------------|
| **Infraestructura** | $4.392.000 |
| **Soporte y Mantenimiento** | $11.600.000 |
| **IA Local** | **$0** ⭐ |

**TOTAL MANTENIMIENTO:** **$15.992.000 CLP/año**


## 🏆 6. JUSTIFICACIÓN DEL PRECIO

### 6.1 Valor Entregado
- ✅ **Sistema Completo:** Frontend + Backend + Base de Datos + IA
- ✅ **IA Sin Costos Recurrentes:** Ahorro significativo vs. competencia  
- ✅ **Alta Disponibilidad:** Replicación y respaldos automáticos
- ✅ **Tecnologías Probadas:** Stack moderno y escalable
- ✅ **Documentación y Capacitación:** Incluidas en el precio
- ✅ **Soporte 6 meses:** Garantía post-implementación

## VENTAJAS ECONÓMICAS CLAVE
-  **IA Local sin Costos Recurrentes** (Ollama + Llama 2): Ahorro de $2.400.000-$12.000.000 CLP anuales
-  **Tecnologías Open Source**: Reducción significativa en licencias
-  **Implementación Rápida**: 12 semanas vs. 24-48 semanas competencia
-  **ROI Positivo**: Retorno de inversión en 18 meses

### 6.2 ROI Estimado
- **Ahorro anual por IA local:** $7.800.000 CLP
- **Recuperación de inversión:** 18-24 meses
- **Beneficio neto 3 años:** $15.000.000+ CLP

---

## 📊 7. COMPARACIÓN CON MERCADO

### 7.1 Competencia vs. Nuestra Propuesta

| Concepto | Competencia Promedio | Nuestra Propuesta | Ahorro |
|----------|---------------------|------------------|--------|
| **Implementación** | $35.000.000 CLP | **$25.970.000 CLP** | 26% |
| **Mantenimiento Anual** | $25.000.000 CLP | **$15.992.000 CLP** | 36% |
| **IA (Anual)** | $8.000.000 CLP | **$0 CLP** | 100% |
| **Total 3 años** | $110.000.000 CLP | **$57.954.000 CLP** | **47%** |

### 7.2 Ventajas Diferenciales
✅ **47% más económico** que competencia directa  
✅ **IA local sin costos recurrentes**  
✅ **Tecnología open source** sin vendor lock-in  
✅ **Implementación en 12 semanas** vs. 24+ semanas  
✅ **Soporte técnico local**



## 📋 8. Apectos Comerciales

### 8.1 Modalidades de Pago

#### Opción Recomendada: Pago en Hitos
- **Hito 1 (Inicio):** $12.985.000 CLP (50%)
- **Hito 2 (Entrega Beta):** $7.791.000 CLP (30%)
- **Hito 3 (Go-Live):** $5.194.000 CLP (20%)

### 8.2 Garantías
- **Uptime:** 99.5% mensual
- **Soporte:** 6 meses incluidos
- **Corrección de bugs:** Sin costo durante garantía
- **Documentación completa:** Incluida



