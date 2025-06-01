function filtrarContactos() {
  const input = document.getElementById('searchInput');
  const filter = input.value.toLowerCase();
  const tabla = document.querySelector('.tabla-contactos tbody');
  const filas = tabla.getElementsByTagName('tr');

  for (let i = 0; i < filas.length; i++) {
    const td = filas[i].getElementsByTagName('td')[0]; // nombre en la primera columna
    if (td) {
      const texto = td.textContent || td.innerText;
      filas[i].style.display = texto.toLowerCase().includes(filter) ? '' : 'none';
    }
  }
}
