# 🤝 Cómo trabajamos (Javier Ojeda · Javier Concha)

## Ramas, commits y Pull Requests (enlazados con Jira, clave `GPF`)

| Elemento | Formato | Ejemplo |
|---|---|---|
| Rama | `feature/GPF-<n>-<descripcion-corta>` | `feature/GPF-12-validar-rut` |
| Commit | `<Tipo>(GPF-<n>): <qué se hizo>` + cuerpo explicando **por qué** | `Feat(GPF-12): validar RUT con algoritmo módulo 11` |
| Pull Request | `GPF-<n> <Título de la historia>` | `GPF-12 Socio con validación de RUT` |

Tipos de commit: `Feat`, `Fix`, `Refactor`, `Docs`, `Test`, `Chore`.

## Flujo

1. Mover la historia a **En curso** en Jira.
2. `git checkout main && git pull` y crear la rama de la historia.
3. Programar, comentar cada línea y agregar pruebas.
4. `python -m pytest` debe pasar completo.
5. Abrir el PR hacia `main`, mover la historia a **En revisión** y pedir revisión al compañero.
6. Con la aprobación, hacer merge, mover a **Finalizado** y anotar el avance en la bitácora del `README.md`.

## ✅ Definition of Done

- [ ] Comentario en cada línea lógica y docstring en cada clase y método.
- [ ] Type hints; atributos privados con `@property` y setters que validan.
- [ ] SQL siempre parametrizado (`?`).
- [ ] Pruebas nuevas para los criterios de aceptación y `pytest` en verde.
- [ ] PR revisado y aprobado por el compañero.
- [ ] Bitácora del README actualizada.
