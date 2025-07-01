let carrito = JSON.parse(localStorage.getItem('carrito')) || [];

// Mostrar contenido del carrito
document.addEventListener("DOMContentLoaded", () => {
  renderizarCarrito();
});


function renderizarCarrito() {
  const contenedor = document.getElementById("carrito-contenido");
  if (!contenedor) return;

  contenedor.innerHTML = "";

  if (carrito.length === 0) {
    contenedor.innerHTML = "<p>No hay productos en el carrito.</p>";
    return;
  }

  let total = 0;
  carrito.forEach((p, index) => {
    const subtotal = p.precio * p.cantidad;
    total += subtotal;

    const card = document.createElement('div');
    card.className = 'card mb-3 card-carrito';
    card.innerHTML = `
      <div class="row g-0 align-items-center">
        <div class="col-md-3 text-center">
          <img src="${p.imagen}" class="img-fluid rounded-start" alt="${p.nombre}" style="max-height: 100px;">
        </div>
        <div class="col-md-6">
          <div class="card-body">
            <h5 class="card-title">${p.nombre}</h5>
            <p class="card-text mb-1"><strong>Precio:</strong> S/. ${parseFloat(p.precio).toFixed(2)}</p>
            <p class="card-text mb-1"><strong>Subtotal:</strong> S/. ${subtotal.toFixed(2)}</p>

            <div class="d-flex align-items-center mt-2">
              <button class="btn btn-outline-secondary cantidad-btn me-2" onclick="cambiarCantidad(${index}, -1)">-</button>
              <span>${p.cantidad}</span>
              <button class="btn btn-outline-secondary cantidad-btn ms-2" onclick="cambiarCantidad(${index}, 1)">+</button>
            </div>
          </div>
        </div>
        <div class="col-md-3 text-center">
          <button class="btn btn-outline-danger" onclick="eliminarProducto(${index})">Eliminar</button>
        </div>
      </div>
    `;
    contenedor.appendChild(card);
  });

  const totalDiv = document.createElement('div');
  totalDiv.className = "text-end mt-3 fw-bold fs-5";
  totalDiv.innerHTML = `Total: S/. ${total.toFixed(2)}`;
  contenedor.appendChild(totalDiv);
}

function cambiarCantidad(index, cambio) {
  if (carrito[index]) {
    carrito[index].cantidad += cambio;
    if (carrito[index].cantidad <= 0) {
      carrito.splice(index, 1);
    }
    localStorage.setItem('carrito', JSON.stringify(carrito));
    renderizarCarrito();
  }
}

function eliminarProducto(index) {
  if (carrito[index]) {
    carrito.splice(index, 1);
    localStorage.setItem('carrito', JSON.stringify(carrito));
    renderizarCarrito();
  }
}

function confirmarVaciarCarrito() {
  Swal.fire({
    title: '¿Vaciar carrito?',
    text: 'Se eliminarán todos los productos del carrito. ¿Continuar?',
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#d33',
    cancelButtonColor: '#3085d6',
    confirmButtonText: 'Sí, vaciar',
    cancelButtonText: 'Cancelar'
  }).then((result) => {
    if (result.isConfirmed) {
      localStorage.removeItem('carrito');
      carrito = [];
      renderizarCarrito();

      Swal.fire({
        title: 'Carrito vaciado',
        icon: 'success',
        timer: 1500,
        showConfirmButton: false,
        toast: true,
        position: 'bottom-start'
      });
    }
  });
}

function confirmarIrAPagar() {
  Swal.fire({
    title: '¿Ir a pagar?',
    text: '¿Seguro que no quieres agregar más productos?',
    icon: 'question',
    showCancelButton: true,
    confirmButtonColor: '#28a745',
    cancelButtonColor: '#6c757d',
    confirmButtonText: 'Sí, ir a pagar',
    cancelButtonText: 'Seguir comprando'
  }).then((result) => {
    if (result.isConfirmed) {
      window.location.href = '/pago';
    }
  });
}


// Función para añadir productos (usada desde productos.html)
function addToCart(btn) {
  const id = parseInt(btn.dataset.id);
  const nombre = btn.dataset.nombre;
  const precio = parseFloat(btn.dataset.precio);
  const imagen = btn.dataset.imagen;

  const existente = carrito.find(p => p.id === id);
  if (existente) {
    existente.cantidad += 1;
  } else {
    carrito.push({ id, nombre, precio, imagen, cantidad: 1 });
  }

  localStorage.setItem('carrito', JSON.stringify(carrito));
}