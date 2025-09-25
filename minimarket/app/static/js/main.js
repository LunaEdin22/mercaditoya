// JavaScript principal para MiniMarket

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar componentes
    initializeTooltips();
    initializeScrollToTop();
    initializeCartFunctions();
    initializeQuantityControls();
    initializeImageLazyLoading();
    
    // Event listeners globales
    setupGlobalEventListeners();
});

// Inicializar tooltips de Bootstrap
function initializeTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Scroll to top button
function initializeScrollToTop() {
    // Crear botón scroll to top
    const scrollButton = document.createElement('button');
    scrollButton.className = 'scroll-to-top';
    scrollButton.innerHTML = '<i class="fas fa-chevron-up"></i>';
    scrollButton.setAttribute('aria-label', 'Ir arriba');
    document.body.appendChild(scrollButton);
    
    // Mostrar/ocultar botón basado en scroll
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            scrollButton.style.display = 'flex';
        } else {
            scrollButton.style.display = 'none';
        }
    });
    
    // Scroll suave al hacer click
    scrollButton.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// Funciones del carrito
function initializeCartFunctions() {
    // Configurar formularios de agregar al carrito
    const carritoForms = document.querySelectorAll('.agregar-carrito-form');
    carritoForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            agregarCarritoAjax(this);
        });
    });
}

// Agregar producto al carrito con AJAX
function agregarCarritoAjax(form) {
    const formData = new FormData(form);
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    
    // Deshabilitar botón y mostrar loading
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Agregando...';
    
    fetch('/pedidos/agregar_carrito', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Actualizar badge del carrito
            updateCartBadge(data.total_items);
            
            // Mostrar mensaje de éxito
            showToast('success', data.message);
            
            // Restaurar botón
            submitBtn.innerHTML = '<i class="fas fa-check me-1"></i>¡Agregado!';
            setTimeout(() => {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }, 2000);
        } else {
            showToast('error', data.message);
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('error', 'Error al agregar el producto');
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    });
}

// Actualizar badge del carrito
function updateCartBadge(totalItems) {
    const badge = document.getElementById('carrito-badge');
    if (badge) {
        badge.textContent = totalItems;
        
        // Animación de pulse
        badge.classList.add('pulse');
        setTimeout(() => {
            badge.classList.remove('pulse');
        }, 1000);
    }
}

// Controles de cantidad
function initializeQuantityControls() {
    // Event delegation para botones de cantidad
    document.addEventListener('click', function(e) {
        // Buscar si es un botón de cantidad dentro de un input-group
        if (e.target.matches('.input-group .btn') && 
            (e.target.textContent.trim() === '+' || e.target.textContent.trim() === '-')) {
            e.preventDefault();
            const button = e.target;
            const increment = button.textContent.trim() === '+' ? 1 : -1;
            cambiarCantidad(button, increment);
        }
    });
}

// Cambiar cantidad en formularios
function cambiarCantidad(button, increment) {
    const inputGroup = button.closest('.input-group');
    const input = inputGroup.querySelector('input[type="number"]');
    const currentValue = parseInt(input.value) || 0;
    const min = parseInt(input.min) || 0;
    const max = parseInt(input.max) || 999;
    
    let newValue = currentValue + increment;
    
    if (newValue < min) newValue = min;
    if (newValue > max) newValue = max;
    
    input.value = newValue;
    
    // Trigger change event
    input.dispatchEvent(new Event('change'));
}

// Sistema de notificaciones toast
function showToast(type, message, duration = 3000) {
    // Crear contenedor de toasts si no existe
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }
    
    // Crear toast
    const toastId = 'toast-' + Date.now();
    const iconClass = {
        'success': 'fas fa-check-circle text-success',
        'error': 'fas fa-exclamation-circle text-danger',
        'warning': 'fas fa-exclamation-triangle text-warning',
        'info': 'fas fa-info-circle text-info'
    }[type] || 'fas fa-info-circle text-info';
    
    const toastHtml = `
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <i class="${iconClass} me-2"></i>
                <strong class="me-auto">MiniMarket</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    // Mostrar toast
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: duration
    });
    
    toast.show();
    
    // Limpiar después de ocultar
    toastElement.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
}

// Lazy loading de imágenes
function initializeImageLazyLoading() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
}

// Event listeners globales
function setupGlobalEventListeners() {
    // Confirmación para eliminaciones
    document.addEventListener('click', function(e) {
        const deleteButton = e.target.closest('[data-confirm]');
        if (deleteButton) {
            const message = deleteButton.dataset.confirm || '¿Estás seguro de que quieres realizar esta acción?';
            if (!confirm(message)) {
                e.preventDefault();
                return false;
            }
        }
    });
    
    // Auto-submit para filtros
    document.querySelectorAll('.auto-submit').forEach(element => {
        element.addEventListener('change', function() {
            this.closest('form').submit();
        });
    });
    
    // Validación de formularios en tiempo real
    document.querySelectorAll('input[type="email"]').forEach(input => {
        input.addEventListener('blur', validateEmail);
    });
    
    document.querySelectorAll('input[type="password"]').forEach(input => {
        input.addEventListener('input', validatePassword);
    });
}

// Validaciones
function validateEmail(e) {
    const input = e.target;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (input.value && !emailRegex.test(input.value)) {
        input.classList.add('is-invalid');
        showValidationMessage(input, 'Por favor ingresa un email válido');
    } else {
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
        hideValidationMessage(input);
    }
}

function validatePassword(e) {
    const input = e.target;
    const minLength = 6;
    
    if (input.value.length > 0 && input.value.length < minLength) {
        input.classList.add('is-invalid');
        showValidationMessage(input, `La contraseña debe tener al menos ${minLength} caracteres`);
    } else if (input.value.length >= minLength) {
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
        hideValidationMessage(input);
    }
}

function showValidationMessage(input, message) {
    hideValidationMessage(input);
    
    const feedback = document.createElement('div');
    feedback.className = 'invalid-feedback';
    feedback.textContent = message;
    feedback.setAttribute('data-validation-for', input.id || input.name);
    
    input.parentNode.appendChild(feedback);
}

function hideValidationMessage(input) {
    const existingFeedback = input.parentNode.querySelector(`[data-validation-for="${input.id || input.name}"]`);
    if (existingFeedback) {
        existingFeedback.remove();
    }
}

// Utilidades
function formatCurrency(amount) {
    return new Intl.NumberFormat('es-AR', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function debounce(func, wait, immediate) {
    var timeout;
    return function() {
        var context = this, args = arguments;
        var later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        var callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

// Búsqueda en tiempo real
function initializeRealTimeSearch() {
    const searchInput = document.querySelector('input[name="q"]');
    if (searchInput) {
        const debouncedSearch = debounce(function() {
            // Implementar búsqueda AJAX aquí si es necesario
        }, 300);
        
        searchInput.addEventListener('input', debouncedSearch);
    }
}

// Exportar funciones principales para uso global
window.MiniMarket = {
    showToast,
    cambiarCantidad,
    agregarCarritoAjax,
    updateCartBadge,
    formatCurrency,
    debounce
};