# 🎯 VALIDACIÓN DE ESPECIFICIDAD - Sistema de Simulaciones

## 📌 ¿QUÉ ES LA VALIDACIÓN DE ESPECIFICIDAD?

Es un **sistema automático que garantiza que cada simulación es ESPECÍFICA del caso real reportado**, no una plantilla genérica reutilizable.

**Problema que resuelve:**
- ❌ "Actualiza tu seguridad ahora" (genérica, no educativa)
- ✅ "Actualiza Firefox 125 por CVE-2024-5678 en Banco Nacional" (específica, educativa)

---

## 🔍 DESCRIPTORES ÚNICOS DEL ARTÍCULO

El sistema automáticamente extrae 5 categorías de descriptores del artículo:

### 1. **Nombres de Entidades Específicas**
Organismos, bancos, instituciones mencionadas en el caso.

**Ejemplos:**
- Banco Nacional (BNA)
- Poder Judicial (PJ)
- CERT Paraguay
- IPS (Instituto de Previsión Social)
- Policía Nacional
- Hacienda / SET (Administración Tributaria)

### 2. **Técnicas de Ataque Específicas**
Métodos técnicos usados en el ataque reportado.

**Ejemplos:**
- Phishing
- Smishing (SMS)
- Vishing (voz)
- QR malicioso
- Deepfake
- Suplantación de identidad
- Captura de credenciales
- Robo de datos
- Malware/Ransomware

### 3. **Sistemas/Productos Mencionados**
Software, versiones, CVEs específicas del caso.

**Ejemplos:**
- Firefox 125.0.x
- CVE-2024-5678
- Windows 11
- Android 14
- Chrome navegador
- Versión 2.4.1 de sistema X

### 4. **Acciones Específicas del Atacante**
Pasos concretos que ejecuta el atacante.

**Ejemplos:**
- Cambio de contraseña
- Solicita 2FA
- Descarga archivo ejecutable
- Verifica identidad
- Actualiza cuenta
- Confirma datos
- Ingresa credenciales
- Activa JavaScript

### 5. **Indicadores de Sospecha Específicos**
Señales que hacen que algo sea sospechoso en este caso.

**Ejemplos:**
- Dominio falso (bna-py vs bna)
- Remitente sospechoso (seguridad@dominio-falso)
- Urgencia artificial (24 horas, "acción inmediata")
- Amenaza de cierre (cuenta será bloqueada)
- Archivo sospechoso (descarga de .exe)

---

## ✅ VALIDACIÓN AUTOMÁTICA

### Cómo Funciona:

1. **Extracción**: Sistema lee el artículo
2. **Identificación**: Extrae descriptores únicos de cada categoría
3. **Generación**: IA genera simulación (DEBE incluir descriptores)
4. **Validación**: Sistema verifica que la simulación incluyó ≥50% de descriptores
5. **Resultado**:
   - ✅ SI cumple → Simulación aceptada
   - ❌ NO cumple → Simulación rechazada, pide regeneración

### Umbral de Especificidad:
- **Mínimo requerido**: 50% de descriptores únicos
- **Ejemplo**: Si hay 6 descriptores, debe incluir mínimo 3

---

## 📊 EJEMPLOS PRÁCTICOS

### CASO: Phishing contra Banco Nacional

**Artículo:**
```
"Se reporta campaña phishing imitando Banco Nacional.
Atacantes envían SMS falsos solicitando verificación 2FA.
Los usuarios son redirigidos a sitio falso bna-py.com.py donde 
se roba sus credenciales. CVE-2024-1234 afecta a navegadores."
```

**Descriptores extraídos:**
- Entidades: Banco Nacional
- Técnicas: Phishing, Smishing, Robo de credenciales
- Sistemas: CVE-2024-1234, navegadores
- Acciones: Solicita 2FA, Redirige a sitio falso
- Indicadores: Dominio falso (bna-py), SMS falso, robo de credenciales

**Simulación ✅ ACEPTADA** (Incluye ≥50%):
```
De: seguridad@bna-py.com.py
Asunto: Verificación urgente de cuenta

Estimado cliente del Banco Nacional,

Se detectó intentos de acceso no autorizado a su cuenta.
Para proteger sus datos frente a CVE-2024-1234 que afecta
a navegadores, debe verificar su identidad ahora.

Acceda a: bna-py.com.py

Se le solicitará verificación 2FA por SMS.
Tiene 24 horas.

Departamento de Seguridad BNA
```
→ Incluye: BNA, CVE-2024-1234, 2FA, dominio falso bna-py (✓ 4/5 descriptores)

**Simulación ❌ RECHAZADA** (Genérica):
```
Estimado cliente,

Actualiza tu seguridad ahora haciendo clic aquí: portal.com.py

Gracias
```
→ NO incluye: BNA, CVE, técnica específica, 2FA (✗ 0/5 descriptores)

---

### CASO: Comunicación legítima de IPS

**Artículo:**
```
"IPS emite aviso sobre nuevas medidas de seguridad.
Recomenda activar autenticación de dos factores 2FA.
Advierte sobre campañas de phishing dirigidas a afiliados.
Sitio oficial: ips.gov.py"
```

**Descriptores extraídos:**
- Entidades: IPS
- Técnicas: Phishing, Autenticación 2FA
- Sistemas: N/A
- Acciones: Activar 2FA
- Indicadores: Riesgos de phishing

**Simulación ✅ ACEPTADA** (Específica):
```
De: comunicaciones@ips.gov.py
Asunto: Recomendaciones de seguridad para afiliados

Estimado afiliado de IPS,

Informamos sobre nuevas medidas de seguridad:

1. ACTIVAR AUTENTICACIÓN 2FA:
   - Acceder a: ips.gov.py
   - Ir a Seguridad → Autenticación de dos factores
   
2. CUIDADO CON PHISHING:
   - IPS nunca solicita contraseña por correo
   - Verifique que el dominio sea ips.gov.py (sin variaciones)
   
Para apoyo: comunicaciones@ips.gov.py

Departamento de Comunicaciones IPS
```
→ Incluye: IPS, Phishing, 2FA, ips.gov.py oficial (✓ 4/5 descriptores)

**Simulación ❌ RECHAZADA** (Genérica):
```
Hola cliente,

Actualiza tu contraseña. Es importante.

Gracias
```
→ NO incluye: IPS, 2FA, phishing, recomendaciones específicas (✗ 0/5)

---

## 🔧 CÓMO IMPLEMENTARLO EN TU GENERACIÓN

### Para Usuario/Desarrollador:

La validación es **automática**. Simplemente:

1. Proporciona un artículo con detalles específicos
2. El sistema extrae descriptores
3. Proporciona simulación (con descriptores destacados)
4. Sistema valida automáticamente

**No necesitas hacer nada especial**, pero asegúrate de que:
- El artículo tenga contenido detallado (no un resumen de 2 líneas)
- Los descriptores que extraiga sean relevantes
- La IA entienda qué debe incluir

---

## 📋 CHECKLIST DE ESPECIFICIDAD

Antes de aceptar una simulación, verifica:

```
□ ¿Menciona la entidad específica del caso? (ej: BNA, no "banco")
□ ¿Menciona la técnica específica? (ej: phishing, no "ataque")
□ ¿Menciona sistemas/versiones? (ej: CVE-2024-..., Firefox 125)
□ ¿Menciona acciones específicas? (ej: 2FA, no "verificación")
□ ¿Menciona indicadores específicos? (ej: dominio falso bna-py)
□ ¿Es diferente de una plantilla genérica? SÍ → ✅ ACEPTAR
```

Si ≥50% es sí: ✅ Simulación aceptada

---

## ⚙️ CONFIGURACIÓN TÉCNICA

### Umbral Flexible:
- Mínimo: 50% de descriptores (por defecto)
- Máximo: 100% (ideal pero no obligatorio)
- Rango típico: 60-80%

### Categorías Ponderadas:
Todas las categorías tienen igual peso (20% cada una).

### Validación Post-Generación:
Ejecuta DESPUÉS de que la IA responde.
Si no cumple: rechaza automáticamente y solicita regeneración.

---

## 📊 IMPACTO EN CALIDAD

### Antes (sin validación):
```
Genérica: 40% (plantillas reutilizables, poco educativas)
Específica: 60% (detalladas del caso, educativas)
```

### Después (con validación):
```
Genérica: 0% (rechazadas automáticamente)
Específica: 100% (TODAS deben ser específicas)
```

---

## 🎓 EDUCACIÓN DEL USUARIO

Las simulaciones específicas enseñan PATRONES REALES:

**Genérica → No educativa:**
```
"Actualiza seguridad" 
→ El usuario no aprende qué específicamente atacar
```

**Específica → Educativa:**
```
"CVE-2024-5678 en Firefox afecta a Banco Nacional"
→ El usuario aprende: producto, versión, entidad, CVE específicos
```

---

## ✨ RESULTADO FINAL

Con esta validación:
1. **Cero simulaciones genéricas** → 100% específicas
2. **Mayor valor educativo** → Patrones reales
3. **Mejor retención** → Detalles concretos se recuerdan más
4. **Más realismo** → Basadas en casos actuales

**Sistema de simulaciones completamente alineado con objetivos educativos.**
