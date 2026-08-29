# Estándares de Simulaciones Anti-Phishing

## 1. DIFERENCIA CLARA: PHISHING vs NO-PHISHING

### SIMULACIÓN PHISHING (es_phishing=true)
**Objetivo**: Entrenar a usuarios a detectar ATAQUES REALES de phishing

#### Características Obligatorias:
1. **DOMINIO FALSO** - Domain spoofing similar al real
   - ✅ CORRECTO: bna-py.com.py (si real es bna.com.py)
   - ✅ CORRECTO: pj.int.gov.py (si real es pj.gov.py)
   - ❌ INCORRECTO: usando dominio oficial exacto
   - ❌ INCORRECTO: dominio completamente inventado (ej: banco-seguro.com)

2. **PROPÓSITO MALICIOSO CLARO** - Busca obtener algo del usuario
   - ✅ Capturar credenciales de acceso
   - ✅ Obtener datos bancarios / información personal
   - ✅ Instalar malware mediante descarga
   - ✅ Hacer clic en enlace malicioso
   - ❌ Solo informar (eso es legítimo)

3. **REMITENTE FALSO** - Email con dominio falso
   - ✅ seguridad@pj.int.gov.py (si verdadero es pj.gov.py)
   - ✅ info@itau-paraguay.com.py (si verdadero es itau.com.py)
   - ❌ contacto@pj.gov.py (es el real, no es phishing)

4. **ELEMENTOS SOSPECHOSOS** (al menos 2 de estos)
   - ✅ Adjuntos descargables (.exe, .zip, .pdf con macros)
   - ✅ Enlaces a dominios falsos
   - ✅ Urgencia artificial ("dentro de 24 horas", "acción inmediata")
   - ✅ Solicitud de credenciales o datos sensibles
   - ✅ Amenazas o miedo ("cuenta será bloqueada", "pérdida de acceso")
   - ✅ Forma de escribir informal/pobre (errores, redacción rara)
   - ✅ Discordancia entre remitente y contenido

5. **CONTEXTO REALISTA**
   - ✅ Basado en CASO REAL del artículo
   - ✅ Incorpora detalles específicos (producto, CVE, versión)
   - ✅ Mantiene coherencia con entidad objetivo
   - ✅ Usa procesos/trámites reales de Paraguay

#### Checklist PHISHING:
- [ ] Dominio falso pero similar (not exact match)
- [ ] Remitente: email con dominio falso
- [ ] Propósito: obtener dinero, datos o credenciales
- [ ] Incluye ≥2 elementos sospechosos (urgencia, adjunto, amenaza, etc)
- [ ] Redacción desde perspectiva de atacante
- [ ] Específico del caso reportado (no genérico)
- [ ] NO usa source provider domains (cert.gov.py, abc.com.py)
- [ ] Patrones reales de comportamiento del ataque
- [ ] Coherencia dominio-remitente-enlace

**Ejemplo CORRECTO:**
```
De: seguridad@pj.int.gov.py
Asunto: Actualización de sistema - Acción requerida hoy
Cuerpo: 
"Estimado ciudadano, se ha detectado actividad sospechosa en nuestros 
registros. Debe verificar su identidad AHORA accediendo a:
pj.int.gov.py
Tiene 2 horas para completar el proceso o su acceso será bloqueado."
Adjunto: "formulario-verificacion.exe"
```

**Ejemplo INCORRECTO:**
```
De: info@pj.gov.py  ❌ (es dominio real, no phishing)
Asunto: Aviso importante
Cuerpo: Mensaje genérico sin detalles específicos
```

---

### SIMULACIÓN NO-PHISHING (es_phishing=false)
**Objetivo**: Entrenar a usuarios a reconocer comunicación LEGÍTIMA y confiar en fuentes reales

#### Características Obligatorias:

1. **DOMINIO OFICIAL** - Domain del sitio real
   - ✅ CORRECTO: pj.gov.py (si entidad es Poder Judicial)
   - ✅ CORRECTO: bna.com.py (si entidad es Banco Nacional)
   - ❌ INCORRECTO: dominio falso
   - ❌ INCORRECTO: cualquier variación del dominio

2. **PROPÓSITO LEGÍTIMO** - Informar, educar, brindar servicio
   - ✅ Aviso oficial sobre un cambio de política
   - ✅ Información educativa sobre cómo protegerse
   - ✅ Confirmación de un trámite que el usuario solicitó
   - ✅ Comunicación de actualización de sistemas
   - ❌ Solicitar urgencia artificial
   - ❌ Pedir datos que la entidad ya tiene
   - ❌ Amenazar con cierre de cuenta

3. **REMITENTE OFICIAL** - Email real de la entidad
   - ✅ contacto@pj.gov.py (si es el dominio oficial)
   - ✅ info@bna.com.py (si es oficial)
   - ❌ Dominio falso o variación
   - ❌ Email personal/genérico si es entidad gubernamental

4. **SIN ELEMENTOS MALICIOSOS** - Ninguno de estos
   - ❌ PROHIBIDO: Adjuntos (documentos, ejecutables, archivos)
   - ❌ PROHIBIDO: Solicitar credenciales de acceso
   - ❌ PROHIBIDO: Solicitar números de tarjeta/datos bancarios
   - ❌ PROHIBIDO: Amenazas o presión artificial
   - ❌ PROHIBIDO: Enlaces a descargas de software
   - ✅ SÍ: Link a página oficial (sin parámetros sospechosos)
   - ✅ SÍ: Información educativa clara
   - ✅ SÍ: Detalles sobre qué hacer si recibe phishing

5. **TONO PROFESIONAL**
   - ✅ Lenguaje formal, correcto ortográficamente
   - ✅ Estructura clara (De/Asunto/Cuerpo bien organizado)
   - ✅ Información verificable (referencias a comunicados previos, trámites oficiales)
   - ❌ Prisa artificial
   - ❌ Tonos informales o coloquiales

#### Checklist NO-PHISHING:
- [ ] Dominio OFICIAL (exacto, sin variaciones)
- [ ] Remitente: email oficial de la entidad
- [ ] Propósito: informar, educar, brindar servicio oficial
- [ ] CERO adjuntos descargables (attachments = [])
- [ ] NO solicita credenciales ni datos sensibles
- [ ] NO pide acción urgente artificial
- [ ] Redacción formal y clara
- [ ] NO usar source providers como entidad (cert.gov.py, abc.com.py)
- [ ] Educativo: enseña cómo protegerse o qué esperar
- [ ] Coherencia dominio-remitente-contenido

**Ejemplo CORRECTO:**
```
De: contacto@pj.gov.py
Asunto: Información sobre nuevos servicios en línea
Cuerpo:
"Estimado ciudadano, informamos que se han implementado nuevas 
medidas de seguridad en nuestro sitio web. Le recomendamos:

1. Verificar que accede a https://pj.gov.py (sin variaciones)
2. No compartir contraseña por correo
3. Reportar actividad sospechosa a: contacto@pj.gov.py

Para más información sobre seguridad en línea, visite la sección
de FAQ en el sitio oficial."

Adjuntos: NINGUNO
```

**Ejemplo INCORRECTO:**
```
De: seguridad@pj-gob.gov.py  ❌ (dominio falso)
Asunto: Verificación urgente
Cuerpo: Textos con amenazas
Adjunto: "documento.pdf"  ❌ (tiene adjunto)
```

---

## 2. DIMENSIONES DE REALISMO EDUCATIVO

### A. VEROSIMILITUD TÉCNICA
**¿El ataque parece TÉCNICAMENTE posible y realista?**

#### Checklist:
- [ ] Menciona productos/sistemas REALES (no inventados)
- [ ] Incluye CVEs si el artículo los menciona
- [ ] Versiones plausibles (ej: v2.4.1, no v999.0)
- [ ] Procesos técnicos coherentes
- [ ] No promete cosas técnicamente imposibles
- [ ] Usa terminología técnica correcta (no mezcla conceptos)

#### Ejemplos:
- ✅ "Se detectó CVE-2024-5678 en tu versión de Firefox"
- ❌ "Tu sistema fue hackeado por quantum computing"
- ✅ "Necesitamos verificar tu identidad para acceso 2FA"
- ❌ "Actualiza tu DNI a través de un ejecutable"

---

### B. CONTEXTO PARAGUAYO
**¿Refleja la realidad de Paraguay?**

#### Checklist:
- [ ] Entidades reales (bancos, organismos, dependencias)
- [ ] Procesos reales de Paraguay (trámites, horarios, fechas cívicas)
- [ ] Nombres de funcionarios/departamentos reales
- [ ] Contexto de seguridad real de Paraguay
- [ ] Lenguaje y expresiones locales (no genérico/global)
- [ ] Moneda: Guaraní (PYG), no dólares/euros

#### Ejemplos:
- ✅ Mención a "IPS", "ANDE", "Poder Judicial", "SET"
- ❌ "Contacto con el FBI", "IRS", "Deutsche Bank"
- ✅ "verificar tu afiliación al IPS"
- ❌ "verificar tu Social Security Number"

---

### C. PATRONES DE COMPORTAMIENTO REALISTA
**¿Replica las tácticas reales de atacantes?**

#### Checklist:
- [ ] Urgencia artificial pero creíble (no exagerada)
- [ ] Aprovecha miedo/autoridad (instituciones respetadas)
- [ ] Usa reciprocidad (te ayudan si ayudas)
- [ ] Finge escasez ("solo hoy", "últimas actualizaciones")
- [ ] Crea compromiso ("ya iniciaste el proceso")
- [ ] Tono coherente con entidad (formal si es banco, etc)
- [ ] Lenguaje de urgencia sutilo (no gritos)

#### Ejemplos:
- ✅ "Su cuenta será suspendida en 24 horas si no verifica"
- ❌ "VERIFICA AHORA O SERÁS BLOQUEADO PARA SIEMPRE!!!1"
- ✅ "Como cliente, debe actualizar sus datos"
- ❌ "Te lo pedimos porfa plis"

---

## 3. VALIDACIÓN DE ESPECIFICIDAD (CRÍTICA)

### Descriptores Únicos del Artículo (DEBE incluir ≥50%)
La simulación DEBE incluir los detalles concretos del caso reportado, no puede ser genérica.

**Descriptores a validar:**
1. **Nombres de entidades específicas** (ej: "Banco Nacional", "CERT", "Poder Judicial")
2. **Técnicas de ataque específicas** (ej: "phishing", "smishing", "captura de credenciales")
3. **Sistemas/productos mencionados** (ej: "CVE-2024-...", "Firefox 125", versiones)
4. **Acciones específicas del atacante** (ej: "cambio de contraseña", "solicita 2FA")
5. **Indicadores de sospecha específicos** (ej: "dominio falso", "amenaza de cierre")

**Validación automática:**
- Sistema extrae descriptores únicos del artículo
- La simulación debe incluir MÍNIMO 50% de estos descriptores
- Si falta especificidad: ❌ SE RECHAZA

**Ejemplos:**

❌ RECHAZADO (Genérico):
```
"Estimado cliente, actualiza tu seguridad ahora. 
Haz clic aquí: portal.com.py"
→ No menciona el banco, técnica, CVE, ni proceso específico
```

✅ ACEPTADO (Específico):
```
"Estimado cliente del Banco Nacional,
Se reportó una vulnerabilidad CVE-2024-5678 que afecta a usuarios de Firefox 125.
Para proteger tu cuenta, verifica tu identidad en: bna-py.com.py
Tienes 24 horas para completar la verificación 2FA."
→ Menciona: BNA, CVE específico, Firefox 125, 2FA (descriptores únicos)
```

---

## 4. REGLAS DE RECHAZO (La IA debe rechazar si no cumple)

### Rechazar CUALQUIER SIMULACIÓN si:
- ❌ **NO INCLUYE DESCRIPTORES ÚNICOS** (menos del 50% de los descriptores del caso)
- ❌ Texto COMPLETAMENTE GENÉRICO (sin detalles específicos del artículo)
- ❌ Incoherencia dominio-remitente-enlace
- ❌ NO usa plain text (Markdown, \n literal, HTML entities)

### Rechazar PHISHING si:
- ❌ Usa dominio oficial (no falso)
- ❌ No tiene propósito malicioso claro
- ❌ Menos de 2 elementos sospechosos
- ❌ Propósito es legítimo (solo informar)
- ❌ **No menciona descriptores únicos del caso**

### Rechazar NO-PHISHING si:
- ❌ Usa dominio falso
- ❌ Incluye adjuntos descargables
- ❌ Solicita credenciales o datos sensibles
- ❌ Tiene urgencia artificial exagerada
- ❌ Amenaza con cierre/bloqueo de cuenta
- ❌ No educativo ni informativo
- ❌ **No menciona descriptores únicos del caso**

---

## 4. FORMATO ESPERADO

### JSON Requerido:
```json
{
  "simulacion": "texto completo en español natural",
  "tipo_mensaje": "correo|sms|whatsapp|sitio-web|otro",
  "sender_email": "remitente@dominio.py",
  "subject": "asunto (solo para correo)",
  "attachments": ["archivo1.pdf", "archivo2.exe"],
  "es_phishing": true,
  "feedback": "explicación de qué observar",
  "resultado": "correcto|incorrecto",
  "resumen_justificacion": "por qué eligió phishing vs legítimo"
}
```

### Reglas de Formato:
- ❌ NUNCA usar Markdown: `[texto](url)`
- ✅ Usar plain text: `dominio.com.py`
- ❌ NUNCA incluir `\n` literal
- ✅ Usar saltos de línea reales
- ❌ NUNCA mezc lar Html entities: `&lt;` `&gt;`
- ✅ Usar caracteres normales: `<` `>`
- `attachments = []` SI es no-phishing
- `attachments` con items SI es phishing

---

## 5. PROCESO DE VALIDACIÓN

### Antes de responder (validar):
1. ¿El `es_phishing` está fundamentado en los criterios?
2. ¿La simulación cumple ≥80% del checklist correspondiente?
3. ¿Es específica del artículo (no genérica)?
4. ¿La coherencia dominio-remitente-enlace es correcta?
5. ¿El feedback explica claramente POR QUÉ es phishing o no?

### Si no cumple:
- Rechazar explícitamente
- Explicar qué criterio falta
- Sugerir cómo corregirlo

---

## 6. EJEMPLOS COMPLETOS

### Caso: Phishing contra Banco Nacional
**Artículo base**: Reporta campaña phishing imitando BNA, solicitando verificación 2FA

```json
{
  "simulacion": "De: seguridad@bna-py.com.py\nAsunto: Verificación de cuenta requerida\n\nEstimado cliente,\n\nSe ha detectado un intento de acceso no autorizado a su cuenta. Para proteger sus datos, debe verificar su identidad en:\n\nbna-py.com.py\n\nTiempo límite: 2 horas\n\nAtentamente,\nDepartamento de Seguridad",
  "tipo_mensaje": "correo",
  "sender_email": "seguridad@bna-py.com.py",
  "subject": "Verificación de seguridad - Banco Nacional",
  "attachments": [],
  "es_phishing": true,
  "feedback": "Observe: (1) Dominio falso (bna-py vs bna). (2) Urgencia artificial (2 horas). (3) Solicita verificación en sitio falso. (4) Tono formal pero sospechoso.",
  "resultado": "correcto",
  "resumen_justificacion": "Simula ataque real reportado: phishing por dominio similar buscando credenciales 2FA."
}
```

### Caso: Comunicación legítima de IPS
**Artículo base**: Aviso educativo sobre cómo identificar phishing en comunicaciones de IPS

```json
{
  "simulacion": "De: comunicaciones@ips.gov.py\nAsunto: Información sobre seguridad en línea\n\nEstimado afiliado,\n\nLE informamos que IPS NUNCA solicitará su contraseña por correo. Si recibe mensaje que lo pida:\n\n1. Verifique que el dominio sea ips.gov.py (sin variaciones)\n2. No descargue archivos no solicitados\n3. Reporte a: comunicaciones@ips.gov.py\n\nPara acceder a sus servicios: https://ips.gov.py\n\nAtentamente,\nDepartamento de Comunicaciones IPS",
  "tipo_mensaje": "correo",
  "sender_email": "comunicaciones@ips.gov.py",
  "subject": "Recomendaciones de seguridad en línea",
  "attachments": [],
  "es_phishing": false,
  "feedback": "Este es un ejemplo de COMUNICACIÓN LEGÍTIMA. Observe: (1) Dominio oficial exacto. (2) Educativo (enseña cómo protegerse). (3) No solicita datos sensibles. (4) Cero adjuntos. (5) Tono profesional.",
  "resultado": "correcto",
  "resumen_justificacion": "Comunicación oficial educativa para enseñar diferencia entre sitios legítimos y fraudulentos."
}
```

---

## 7. PREGUNTAS DE VALIDACIÓN PARA LA IA

Después de generar, debe responder internamente:

1. **¿Especificidad?** - ¿Usa detalles del artículo o es texto genérico de plantilla?
   - Si es genérico: ❌ RECHAZA
   
2. **¿Coherencia de dominios?** - ¿Dominio, remitente y enlace son congruentes?
   - Si no: ❌ RECHAZA
   
3. **¿Criterios de es_phishing?** - ¿Cumple ≥3 items del checklist correspondiente?
   - Si no: ❌ RECHAZA
   
4. **¿Realismo educativo?** - ¿Se parece a un ataque/comunicación REAL?
   - Si es muy fantástico: ❌ RECHAZA
   
5. **¿Educativo?** - ¿El usuario aprende patrones reales de phishing o legítimidad?
   - Si es irrelevante: ❌ RECHAZA

---

## 8. REFERENCIA RÁPIDA: PHISHING vs NO-PHISHING

| Aspecto | PHISHING | NO-PHISHING |
|---------|----------|-------------|
| **Dominio** | Falso/Similar | Oficial exacto |
| **Remitente** | Falso | Oficial real |
| **Propósito** | Obtener datos/dinero | Informar/educar |
| **Adjuntos** | Sí, descargables | NO ([]
) |
| **Urgencia** | Artificial | Profesional |
| **Tono** | Puede ser pobre | Formal correcto |
| **Solicita datos** | Sí (credenciales) | No (ya tiene) |
| **Es educativo** | Enseña a detectar fraude | Enseña comunicación legítima |

