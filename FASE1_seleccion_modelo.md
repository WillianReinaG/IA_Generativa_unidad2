# Fase 1 — Selección y justificación del modelo de IA (EcoMarket)

## Contexto

EcoMarket es un comercio electrónico que necesita optimizar la atención al cliente en consultas frecuentes: estado de pedidos, envíos, catálogo y políticas (por ejemplo, devoluciones). La solución debe equilibrar **precisión factual**, **calidad conversacional**, **coste** y **integración** con sistemas internos.

## Modelo propuesto: arquitectura híbrida con LLM de propósito general

Se propone una **solución híbrida** centrada en un **modelo de lenguaje grande (LLM) de propósito general** de última generación, accesible vía API (por ejemplo, **GPT-4o** o **GPT-4o mini** de OpenAI), combinado con **recuperación de información desde la base de datos y APIs internas** de EcoMarket.

| Componente | Función |
|------------|---------|
| **LLM (API)** | Redacta respuestas naturales, empáticas y coherentes; sigue instrucciones y formato del prompt; maneja variaciones del lenguaje del cliente. |
| **Capa de datos (BD / microservicios)** | Fuente de verdad para pedidos, seguimiento, fechas, enlaces de transportista, catálogo, stock y políticas de devolución. |
| **Orquestación** | El backend consulta la BD según la intención detectada, inyecta los hechos en el contexto del modelo (patrón tipo RAG o “tool use”) y valida salidas críticas. |

### Justificación frente a los criterios solicitados

1. **Precisión en temas de pedidos**  
   Los datos concretos (número de seguimiento, estado, ventanas de entrega, URL de rastreo) **no deben inferirse solo por el modelo**. El LLM es excelente para formular la respuesta, pero la **precisión** la aporta la **consulta a la base de datos** (u orden management system) y la inyección de esos campos en el prompt o en herramientas. Así se reduce el riesgo de inventar estados o fechas.

2. **Fluidez en preguntas generales**  
   Un modelo **generalista** reciente ofrece buen español, tono de servicio y capacidad para aclarar dudas sobre políticas o productos cuando el contenido está respaldado por el catálogo o documentación interna.

3. **Costo, escalabilidad e integración**  
   - **GPT-4o mini** (o equivalente económico) es adecuado para muchos flujos de alto volumen con buena calidad. **GPT-4o** puede reservarse para casos sensibles o conversaciones complejas (reglas de enrutado en el backend).  
   - La **API** escala con demanda y evita mantener infraestructura propia de inferencia al inicio.  
   - La **integración** es estándar (HTTPS, SDK): el equipo de EcoMarket ya puede exponer REST/GraphQL sobre pedidos y envíos.

4. **Calidad de las respuestas esperadas**  
   Con **instrucciones claras** (rol, formato, límites), **ejemplos** cuando haga falta y **contexto factual** desde BD, la calidad percibida por el cliente suele ser alta: respuestas completas, empáticas y alineadas con la marca.

### Alternativas consideradas (breve)

| Opción | Ventaja | Inconveniente para EcoMarket |
|--------|---------|-------------------------------|
| **Solo reglas / chatbot clásico** | Muy controlable | Frágil ante lenguaje natural variado. |
| **Solo LLM sin datos en vivo** | Rápido de prototipar | Alto riesgo de **alucinaciones** en pedidos y fechas. |
| **Fine-tuning del LLM** | Mejor tono y vocabulario de marca | No sustituye la BD; coste y ciclo de reentrenamiento. |

**Conclusión:** La opción híbrida **LLM generalista + datos en tiempo real** ofrece el mejor equilibrio para atención al cliente en e-commerce.

## Arquitectura de integración con la base de datos de EcoMarket

```
Cliente (web/app) → API Gateway / Backend EcoMarket
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
   Intención        Consultas        Políticas /
   (NLU/clasif.)    a BD:            docs:
                   - pedidos         catálogo,
                   - envíos          FAQ devoluciones
                   - productos
                        │
                        ▼
              Contexto estructurado (JSON o texto)
              inyectado al LLM (prompt) o vía tools
                        │
                        ▼
                   Respuesta al cliente
              (opcional: moderación, log, métricas)
```

- **Catálogo de productos:** tablas o servicio de catálogo (SKU, nombre, categoría, restricciones de devolución, perecederos, etc.).  
- **Pedidos y envíos:** tabla de pedidos, líneas, estados, transportista, `tracking_number`, `estimated_delivery`, URL de rastreo.  
- **Seguridad:** el backend valida que el cliente autenticado solo reciba datos de **sus** pedidos.

## ¿Propósito general o afinado con datos de la empresa?

- **Fase inicial:** modelo **de propósito general** vía API, con **contexto recuperado** de EcoMarket (no se asume fine-tuning obligatorio).  
- **Evolución opcional:** **fine-tuning ligero** o **ajuste de instrucciones** con conversaciones anonimizadas y aprobadas, para reforzar tono, plantillas y cumplimiento normativo, **sin** usar el fine-tuning como sustituto de la BD para datos transaccionales.

---

*Proyecto: IA Generativa — Unidad 2 — EcoMarket*
