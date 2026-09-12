# Reflexion: Patron Builder en la creacion de la Orden

El `OrdenBuilder` reduce el riesgo de errores porque encapsula en un solo lugar
las reglas de validacion (usuario y productos obligatorios) y el calculo del
total con IVA, en vez de dejar que cada vista repita esa logica de forma manual.
Si la orden se construyera directamente en la vista, cualquier desarrollador
podria olvidar aplicar el IVA, saltarse una validacion o dejar el objeto en un
estado incompleto antes de guardarlo en la base de datos. Con el Builder, el
metodo `build()` es el unico punto de entrada que garantiza que la Orden nunca
se persista sin los datos minimos necesarios, y la interfaz fluida
(`con_usuario` -> `con_productos` -> `para_envio` -> `build`) hace explicito y
legible el proceso de ensamblaje, facilitando las pruebas y el mantenimiento a
futuro.
