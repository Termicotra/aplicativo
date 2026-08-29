# ⚡ GUÍA RÁPIDA - Sistema Mejorado 2.0

## 📌 CAMBIOS PRINCIPALES

### 1. Ingestion (Extracción de Artículos)
**¿Qué cambió?**
- ✅ 80% menos ruido (navegación, metadata)
- ✅ Mejor especificidad (detalles reales)
- ✅ Sin duplicados en campos
- ✅ +180 palabras clave nuevas
- ✅ Contexto paraguayo mejorado

**¿Qué esperar?**
- Campos más limpios
- Menos frases genéricas
- Más información específica del ataque
- Mejor detección de canal

**Archivos:**
- `articulos/ingestion.py` (mejorado)
- `articulos/ingestion_backup.py` (original)
- Documentación: `MEJORAS_INGESTION.md`

---

### 2. Simulaciones (Generación)
**¿Qué cambió?**
- ✅ Criterios EXPLÍCITOS para phishing vs no-phishing
- ✅ Validación automática de estándares
- ✅ Checklists claros (9 items phishing, 10 items no-phishing)
- ✅ 3 dimensiones de realismo (técnico + Paraguay + comportamiento)
- ✅ Cero adjuntos en simulaciones legítimas

**¿Qué esperar?**
- Simulaciones más específicas del caso
- Mejor diferenciación entre phishing/legítimo
- Mayor consistencia en dominio-remitente-enlace
- Simulaciones realistas educativamente

**Archivos:**
- `simulaciones/ai_service.py` (mejorado)
- Documentación: `ESTANDARES_SIMULACIONES.md`

---

## 🎯 CÓMO USAR: Generación de Simulaciones

### Decisión: ¿PHISHING o NO-PHISHING?

**Usa PHISHING (es_phishing=true) si:**
```
El artículo describe un ATAQUE REAL
Objetivo: Entrenar a detectar fraude

Ejemplos:
- "Se reporta campaña phishing imitando BNA"
- "Atacantes envían SMS falsos de IPS"
- "Campañas de smishing activas en Paraguay"
```

**Usa NO-PHISHING (es_phishing=false) si:**
```
El artículo describe CÓMO PROTEGERSE
Objetivo: Entrenar a confiar en comunicación legítima

Ejemplos:
- "Recomendaciones de seguridad de CERT"
- "Cómo identificar sitios fraudulentos"
- "Comunicado oficial sobre nuevas medidas"
```

---

## ✓ CHECKLIST PHISHING

La simulación DEBE cumplir MÍNIMO 4:

- [ ] Dominio FALSO (similar al real)
- [ ] Remitente FALSO (con dominio falso)
- [ ] Propósito MALICIOSO (obtener datos, dinero)
- [ ] ≥2 elementos sospechosos (urgencia, adjunto, amenaza, etc)
- [ ] Redacción fraudulenta (errores, informalidad)
- [ ] Específica del artículo (no genérica)
- [ ] Coherencia dominio-remitente-enlace
- [ ] Tono coherente con entidad
- [ ] Educativo (usuario aprende patrones reales)

---

## ✓ CHECKLIST NO-PHISHING

La simulación DEBE cumplir MÍNIMO 6:

- [ ] Dominio OFICIAL exacto (sin variaciones)
- [ ] Remitente OFICIAL real (mismo dominio)
- [ ] Propósito LEGÍTIMO (informar, educar, servicio)
- [ ] Cero elementos maliciosos
- [ ] NO urgencia artificial
- [ ] NO solicita credenciales
- [ ] NO tiene adjuntos (attachments = [])
- [ ] Redacción formal y correcta
- [ ] Específica del artículo (no genérica)
- [ ] Educativo (enseña protección/legitimidad)

---

## 🚫 REGLAS DE RECHAZO (Automático)

Si hay PHISHING pero:
```
❌ Usa dominio oficial
❌ No tiene propósito malicioso
❌ Es completamente genérica
❌ <2 elementos sospechosos
❌ Incoherencia dominio-remitente-enlace
→ SE RECHAZA
```

Si hay NO-PHISHING pero:
```
❌ Usa dominio falso
❌ Incluye adjuntos
❌ Solicita credenciales
❌ Tiene urgencia artificial
❌ No es educativa
→ SE RECHAZA
```

---

## 📊 TABLA RÁPIDA: PHISHING vs NO-PHISHING

| Aspecto | PHISHING | NO-PHISHING |
|---------|----------|-------------|
| **Dominio** | Falso (similar) | Oficial (exacto) |
| **Remitente** | Falso | Oficial real |
| **Propósito** | Obtener datos/dinero | Informar/educar |
| **Adjuntos** | Sí, descargables | NO ([]) |
| **Urgencia** | Artificial | Profesional |
| **Solicita datos** | Sí, credenciales | No |
| **Ejemplos** | bna-py, seguridad@bna-py | bna.com.py, info@bna |
| **Educativo** | Detectar fraude | Confiar en legítimos |

---

## 🌍 CONTEXTO PARAGUAYO (Obligatorio)

**Entidades reales:**
- Bancos: BNA, Itaú, GNB
- Gobierno: Poder Judicial, Hacienda, IPS, ANDE, SET, DINAC
- Organismos: CERT, Superintendencia de Bancos

**Procesos reales:**
- Transacciones bancarias (PYG)
- Trámites de IPS, ANDE
- Acceso a sistemas judiciales
- Impuestos/multas municipales

**Lenguaje local:**
- No: "Social Security" → Sí: "IPS"
- No: "FBI" → Sí: "Policía Nacional"
- No: "dollars" → Sí: "Guaraní"

---

## 💡 TIPS PRÁCTICOS

### Para PHISHING realista:
1. Basarse en caso real del artículo
2. Usar detalles técnicos (CVE, versión)
3. Crear urgencia creíble (24h)
4. Incluir 2-3 elementos sospechosos
5. Tono coherente con entidad

### Para NO-PHISHING educativa:
1. Usar dominio oficial EXACTO
2. Incluir consejos de protección
3. Nunca pedir datos sensibles
4. Tono profesional y claro
5. Dejar claro qué es legítimo

---

## ✅ VALIDACIÓN RÁPIDA

```
1. ¿ESPECÍFICA del artículo? SÍ → Continúa
2. ¿Coherencia dominio-remitente? SÍ → Continúa
3. ¿Cumple ≥N criterios? SÍ → Continúa
4. ¿Realismo 3D? SÍ → Devuelve JSON
Si alguno es NO → RECHAZA
```

---

**Versión**: 2.0  
**Última actualización**: 27/08/2026  
**Estado**: Listo para usar
