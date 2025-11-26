# Informe de Laboratorio: Análisis y Mitigación de Vulnerabilidades

**Estudiante:** Augusto Fuenzalida
**Fecha:** 25 de Noviembre de 2025
**Asignatura:** Administración de Redes / Seguridad en Sistemas
**Proyecto:** Admin 3 - Hardening de Infraestructura

---

## 1. Introducción
El objetivo de este laboratorio fue realizar una auditoría de seguridad sobre la arquitectura de la aplicación "Admin 3" y aplicar parches para mitigar las vulnerabilidades detectadas en el sistema operativo y las dependencias de los contenedores. Se priorizó la migración de imágenes base y la reconfiguración de los procesos de construcción para reducir la superficie de ataque.

## 2. Metodología y Acciones Realizadas

Para lograr el endurecimiento (hardening) de la infraestructura, se procedió a intervenir tres capas principales del sistema: Infraestructura de datos, Microservicios y Frontend.

### 2.1. Capa de Infraestructura (Base de Datos y Almacenamiento)
Se detectó que las imágenes oficiales de Redis y MinIO contenían vulnerabilidades críticas debido a sus sistemas base.
* **Redis:** Se reemplazó la imagen oficial por una personalizada basada en **Alpine Linux**. Se implementó un script de actualización automática (`apk upgrade`).
    * *Resultado:* Se eliminaron el 100% de las vulnerabilidades del SO. Se observó una alerta menor en el binario interno `gosu`, pero se determinó que el vector de ataque es local y de bajo riesgo en este entorno contenedorizado.
* **MinIO:** La imagen original basada en RedHat (microdnf) presentaba múltiples CVEs. Se realizó una migración completa a una arquitectura Alpine Linux, copiando únicamente los binarios oficiales necesarios.
    * *Resultado:* Vulnerabilidades de sistema operativo reducidas a 0.
* **PostgreSQL:** Se aplicaron imágenes personalizadas para los servicios de Auth, Reservations y Documents, forzando la actualización de paquetes al momento del build.

### 2.2. Capa de Microservicios (Python)
Se actualizaron los `Dockerfile` de los servicios de backend (Auth, Reservations, Documents, Datos Municipalidad y Notificación) para incluir:
* Actualización mandatoria del sistema base (`apt-get upgrade` / `apk upgrade`).
* Actualización de herramientas de gestión de paquetes de Python (`pip`, `setuptools`).

### 2.3. Capa de Frontend y Gateway
El análisis posterior a la remediación indica que tanto el Frontend como el API Gateway se encuentran limpios, reportando **0 vulnerabilidades detectadas**.

## 3. Análisis de Resultados

A continuación, se presenta una tabla comparativa entre el estado inicial (estimado según escaneos previos) y el estado actual post-remediación:

| Servicio | Estado Inicial | Estado Post-Hardening | Observaciones |
|----------|----------------|-----------------------|---------------|
| **Redis** | Vulnerable (SO) | **Seguro (SO)** | Alerta menor en binario `gosu`. |
| **MinIO** | Crítico (RedHat) | **Seguro (Alpine)** | Migración de arquitectura exitosa. |
| **Postgres** | Vulnerable | **Seguro** | 0 Vulnerabilidades de SO. |
| **Python Apps**| Vulnerable | **Endurecido** | Persiste CVE-2024-23342 en librería `ecdsa`. |
| **Frontend** | Seguro | **Seguro** | Limpio. |

**Nota sobre CVE-2024-23342:** A pesar de las medidas tomadas, persiste una alerta en la librería `ecdsa` utilizada por dependencias criptográficas en los microservicios Python. Esta vulnerabilidad está pendiente de un parche oficial *upstream*, por lo que se considera un riesgo aceptado temporalmente.

## 4. Conclusiones y Trabajo Futuro
La infraestructura actual se encuentra operativa y presenta una reducción drástica de vulnerabilidades críticas. Para mantener este estado de seguridad, se proponen los siguientes pasos:
1.  **Monitoreo:** Ejecución semanal del script `scan_vulnerabilities.ps1` desarrollado en el laboratorio.
2.  **Mantenimiento:** Revisión periódica del archivo `requirements.txt` para aplicar parches a `python-jose` y `cryptography` tan pronto como se libere la corrección para `ecdsa`.