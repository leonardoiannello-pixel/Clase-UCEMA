# Clase-UCEMA
Repositorio para los proyectos de la clase de Agentes IA
# Agente de búsqueda y postulación laboral

## Qué construí

Construí con Codex un agente para asistir el proceso de búsqueda y postulación a empleos.

El agente parte de un CV base y de los criterios definidos por el usuario, analiza búsquedas laborales, evalúa su adecuación al perfil, identifica información que falta, prepara versiones del CV adaptadas a cada posición y permite llevar un registro de las postulaciones.

El diseño incorpora supervisión humana: el agente no debe inventar antecedentes y debe consultar cuando encuentra información ambigua o faltante. La intención original era llegar a automatizar también la postulación, pero esa parte todavía no está completamente implementada.

## Cómo se lo pedí

El trabajo comenzó con este pedido a Codex:

> ¿es posible crear un agente para que busque en linkedin y otros portales, identifique búsquedas alineadas con mi perfil, arme un cv adaptado sobre la base de mi información laboral real, me pida información complementaria que pueda ser útil para mejorar el CV y alinearlo mejor con la búsqueda, luego subir el CV en linkedin o en el portal de la empresa, completar todos los campos y enviar la postulación?

A partir de ese pedido inicial fui agregando instrucciones y restricciones a medida que avanzaba el trabajo. Entre ellas, le pedí que:

* analizara primero la Job Description y sus requisitos;
* identificara keywords, hard skills, soft skills, seniority, alcance y responsabilidades;
* utilizara únicamente experiencia real del CV base;
* no inventara empresas, puestos, estudios, idiomas, herramientas, logros ni métricas;
* hiciera preguntas cuando necesitara información adicional;
* adaptara el CV al idioma de la búsqueda;
* generara documentos utilizables para una postulación;
* mantuviera supervisión humana antes de realizar acciones externas.

Durante la preparación de esta entrega también le pedí que generara versiones anonimizadas de los CV para poder publicar el proyecto en un repositorio público sin exponer nombre, teléfono, correo electrónico ni perfil de LinkedIn.

## Qué funciona

El agente ya cuenta con una lógica definida para analizar oportunidades laborales, trabajar a partir de información verificada del candidato, solicitar información adicional cuando sea necesaria y preparar materiales de postulación.

También se definieron criterios configurables de búsqueda y una estructura para registrar las oportunidades y evitar duplicaciones.

Para esta entrega probé además el proceso de anonimización de los CV. Codex generó versiones en español e inglés eliminando la información identificatoria y verificó tanto el contenido como los metadatos antes de su publicación.

El repositorio contiene las instrucciones del agente, ejemplos de configuración y seguimiento y dos CV anonimizados que permiten mostrar el proyecto sin publicar información personal.

## Qué falta o qué falló

La idea original era que el agente pudiera completar el proceso de postulación de punta a punta. Esa parte todavía no funciona de manera general, porque las postulaciones pueden requerir distintos portales, autenticaciones, formularios y acciones externas.

También encontré una dificultad al intentar publicar el proyecto directamente desde Codex. Aunque Codex podía acceder al repositorio de GitHub, la integración tenía permiso de lectura pero no de escritura y devolvía el error `403: Resource not accessible by integration`.

En lugar de quedar trabado intentando resolver la integración, descargué desde Codex los archivos preparados y los subí manualmente a GitHub desde el navegador. El problema de permisos de escritura entre Codex y GitHub queda pendiente para una siguiente iteración.

## Qué aprendí

La principal conclusión fue que trabajar con un agente no consiste solamente en escribir un prompt y aceptar el primer resultado. El trabajo fue evolucionando al definir mejor el objetivo, agregar restricciones, revisar resultados y decidir qué acciones podían automatizarse y cuáles requerían supervisión humana.

También entendí la importancia de separar el contexto privado de lo que se publica: el agente necesita información real para trabajar bien, pero eso no significa que esa información deba formar parte del repositorio.

Finalmente, el problema con GitHub me mostró que una limitación técnica no necesariamente impide completar el objetivo. Cuando la integración automática no permitió publicar, pude cambiar el procedimiento y hacer manualmente ese paso sin descartar el trabajo realizado por el agente.
