# Fase 2 — Fortalezas, limitaciones y riesgos éticos (EcoMarket)

## Fortalezas del modelo propuesto (híbrido: LLM + datos internos)

1. **Reducción del tiempo de primera respuesta**  
   Automatiza consultas repetitivas (¿dónde va mi pedido?, ¿cuándo llega?) con respuestas inmediatas, 24/7.

2. **Escalado de volumen**  
   Absorbe picos (campañas, fechas clave) sin multiplicar linearmente el personal de soporte en el primer contacto.

3. **Consistencia informativa**  
   Si el **contenido factual** proviene de la BD y políticas versionadas, las respuestas pueden alinearse con las mismas reglas que ve el agente humano.

4. **Experiencia conversacional**  
   Buena capacidad para reformular, empatizar y guiar pasos (por ejemplo, devoluciones) en lenguaje natural claro.

5. **Multicanal**  
   Mismo núcleo lógico puede alimentar chat web, app y, con adaptación, otros canales.

## Limitaciones

1. **Casos que exigen empatía profunda o juicio situacional**  
   Conflictos legales, situaciones de salud ligadas a un producto, o clientes en fuerte distrés pueden requerir **intervención humana**; el modelo no sustituye el criterio profesional.

2. **Dependencia de la calidad del contexto inyectado**  
   Si la consulta a BD falla, está desactualizada o el prompt no incluye los campos correctos, la respuesta puede ser incompleta o genérica.

3. **Límites de conocimiento y alucinaciones residuales**  
   Incluso con RAG, puede **extrapolar** o **mezclar** políticas si el prompt es ambiguo o si se mezclan fuentes sin control.

4. **Coste y latencia**  
   Modelos más capaces o contextos muy largos aumentan coste y tiempo de respuesta; hace falta **caché**, **enrutado** (modelo pequeño vs grande) y límites de tokens.

5. **Integración operativa**  
   Requiere monitoreo, versionado de prompts, pruebas de regresión y trazabilidad de incidencias (no es “configurar y olvidar”).

## Riesgos éticos y mitigaciones orientativas

### 1. Alucinaciones (respuestas incorrectas o inventadas)

- **Riesgo:** Inventar un número de seguimiento, una fecha de entrega o una política que no existe.  
- **Mitigación:** **No** pedir al modelo que adivine datos; solo usar valores devueltos por la API/BD. Instrucciones explícitas del tipo: “Si un dato no está en el contexto, dilo y ofrece canal humano”. Revisión humana en casos de reclamación o alto valor.

### 2. Sesgos en los datos de entrenamiento

- **Riesgo:** Estereotipos en el lenguaje, trato desigual sugerido o contenido ofensivo.  
- **Mitigación:** Políticas de uso, filtros de salida, diversidad en pruebas, revisión periódica de conversaciones muestreadas y ajuste de instrucciones.

### 3. Privacidad de datos sensibles de clientes

- **Riesgo:** Filtrar datos de un cliente a otro, o enviar PII innecesaria al proveedor del modelo.  
- **Mitigación:** Autenticación/autorización estricta en backend, **minimización de datos** en el prompt, anonimización cuando sea posible, acuerdos (DPA) con el proveedor, opción de **retención cero** o regiones según normativa, logs sin datos sensibles en claro.

### 4. Impacto laboral en agentes de servicio al cliente

- **Riesgo:** Presión por productividad, desvalorización del trabajo humano o despidos mal gestionados.  
- **Mitigación:** Reposicionar al equipo hacia **casos complejos**, **calidad**, **escalamientos** y **supervisión del sistema**; formación en IA; transparencia interna; negociación según marco laboral aplicable.

---

*Proyecto: IA Generativa — Unidad 2 — EcoMarket*
