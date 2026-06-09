# Manual de Administrador: LexiScan-PAES

Este documento detalla el uso del **Panel de Administrador** y los comandos necesarios para gestionar cuentas de administrador en la plataforma LexiScan-PAES.

## 1. Acceso al Panel

Para acceder al Panel de Administrador, el usuario debe tener privilegios elevados (`es_admin = True` en la base de datos). 

Si el usuario cuenta con estos privilegios, al iniciar sesión verá un botón especial de color **dorado con forma de escudo** (`ADMIN`) en la barra superior del **Dashboard (Inicio)**, justo al lado del botón para cerrar sesión.

Al presionar dicho botón, el administrador será redirigido a la interfaz de gestión de usuarios.

---

## 2. Funcionalidades del Panel

El panel está diseñado para ser rápido y responsivo, mostrando la lista completa de usuarios registrados en la plataforma.

### Búsqueda y Filtros
- En la parte superior encontrarás una barra de búsqueda inteligente.
- Puedes buscar usuarios por su **Nombre Completo**, su **RUT**, o su **Correo Electrónico**. La lista se filtrará en tiempo real.

### Estadísticas Rápidas
Se muestran dos indicadores principales:
- **Usuarios Totales**: La suma histórica de todos los usuarios registrados en el sistema.
- **Activos**: El número de usuarios cuyas cuentas no han sido suspendidas o dadas de baja.

### Acciones sobre Usuarios
Cada usuario en la lista mostrará su Avatar, Nombre (con una etiqueta `ADMIN` si también tiene privilegios), Correo, RUT, puntos de experiencia (XP) y su racha actual.

Junto a la información de cada usuario existen dos botones de acción rápida:

1. **Botón de Candado (Activar / Desactivar)**
   - Si el candado está verde y abierto (`lock-open`), el usuario está activo y puede iniciar sesión.
   - Al presionarlo, el candado se volverá gris y cerrado (`lock-closed`). El usuario se considerará "Inactivo" y perderá el acceso a la plataforma (su cuenta queda suspendida pero no borrada). Puedes presionar el botón nuevamente para devolverle el acceso.

2. **Botón de Basurero Rojo (Eliminar)**
   - Al presionarlo, se te pedirá confirmar la acción a través de una ventana emergente.
   - **Precaución**: Si confirmas, el usuario y absolutamente **todo su historial de progreso**, estadísticas, rachas, y registros de error serán borrados permanentemente de la base de datos (acción irreversible).

*(Nota: Por medidas de seguridad, no puedes desactivar ni eliminar tu propia cuenta de administrador)*.

---

## 3. Otorgar y Revocar Privilegios (Por Consola)

El panel gráfico no permite (por diseño) promover a un usuario normal a Administrador, para evitar escalamiento de privilegios accidentales. Esta acción debe realizarse directo en la base de datos o mediante el script proporcionado.

### Crear un Administrador por Defecto
El sistema cuenta con un script preparado para agregar la columna de seguridad y crear un usuario administrador de forma automática (o convertir uno existente). 
Para correr el script, colócate en la raíz del proyecto y entra a tu entorno virtual de Python:
```bash
cd Producto/backend
python scripts/upgrade_admin.py
```
*Este comando generará o promoverá al usuario `admin@lexiscan.cl` con el RUT `admin-1` y contraseña `admin123`.*

### Promover a un Administrador Manualmente (vía PostgreSQL)
Si deseas convertir a un estudiante existente (ejemplo: RUT "12345678-9") en Administrador, puedes correr la siguiente consulta SQL directamente en tu base de datos:
```sql
UPDATE usuarios SET es_admin = true WHERE rut = '12345678-9';
```

De la misma manera, para revocarle los permisos:
```sql
UPDATE usuarios SET es_admin = false WHERE rut = '12345678-9';
```
