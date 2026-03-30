git reset resumido
--soft : mueve HEAD, staging y working intactos.
--mixed : mueve HEAD, limpia staging, working igual.
--hard : mueve HEAD, limpia staging y working.

Uso:

reset solo local, porque reescribe historial.
revert seguro en ramas compartidas, porque añade commit que deshace cambios.

Ejemplos:

--soft : unir commits sin tocar archivos.
mixed : sacar archivos del staging para reorganizar commits.
--hard : borrar todo y volver a un commit seguro (solo local).
