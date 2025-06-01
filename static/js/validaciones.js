const form = document.getElementById('form');

const inputs = {
  usuario: {
    el: document.getElementById('usuario'),
    icon: document.getElementById('icon-usuario'),
    msg: document.getElementById('msg-usuario'),
    validate: val => val.trim().length >= 3,
    successMsg: 'Usuario válido ✔️',
    errorMsg: 'El usuario debe tener al menos 3 caracteres.'
  },
  password: {
    el: document.getElementById('password'),
    icon: document.getElementById('icon-password'),
    msg: document.getElementById('msg-password'),
    validate: val => val.trim().length >= 5,
    successMsg: 'Contraseña segura ✔️',
    errorMsg: 'La contraseña debe tener al menos 5 caracteres.'
  }
};

function updateValidation(field) {
  const val = field.el.value.trim();
  if (val === '') {
    field.msg.textContent = '';
    field.msg.classList.remove('visible', 'error', 'success');
    field.icon.innerHTML = '';
    return;
  }
  if (field.validate(val)) {
    field.msg.textContent = field.successMsg;
    field.msg.classList.remove('error');
    field.msg.classList.add('success', 'visible');
    field.icon.innerHTML = '';
  } else {
    field.msg.textContent = field.errorMsg;
    field.msg.classList.remove('success');
    field.msg.classList.add('error', 'visible');
    field.icon.innerHTML = '';
  }
}
Object.values(inputs).forEach(field => {
  field.el.addEventListener('input', () => updateValidation(field));
});

form.addEventListener('submit', e => {
  e.preventDefault();
  let allValid = true;
  Object.values(inputs).forEach(field => {
    updateValidation(field);
    if (!field.validate(field.el.value.trim())) {
      allValid = false;
    }
  });
  if (allValid) {
    form.submit();  // Enviar el formulario al servidor
  } else {
    alert('Corrige los campos antes de enviar.');
  }
});
