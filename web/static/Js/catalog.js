document.querySelectorAll('.btn-see-more').forEach(button => {
    button.addEventListener('click', function (e) {
        e.preventDefault();
        const card = this.closest('.product-card');
        const details = card.querySelector('.product-details');
        
        // Alternar visibilidad de los detalles
        if (details.style.display === "none" || details.style.display === "") {
            details.style.display = "block";
            this.innerText = "Ver menos";
        } else {
            details.style.display = "none";
            this.innerText = "Saber más";
        }
    });
});
document.addEventListener("DOMContentLoaded", function() {
    const fadeElements = document.querySelectorAll('.fade-in');
    fadeElements.forEach((element, index) => {
        setTimeout(() => {
            element.classList.add('visible');
        }, index * 200); // Retraso en milisegundos para cada elemento
    });

    // Manejar el evento de clic en las imágenes de los productos
    const productImages = document.querySelectorAll('.product-image');
    productImages.forEach(image => {
        image.addEventListener('click', function() {
            const title = this.getAttribute('data-title');
            const description = this.getAttribute('data-description');
            const price = this.getAttribute('data-price');
            const imgSrc = this.src;

            // Actualizar el modal con la información del producto
            document.getElementById('productModalLabel').innerText = title;
            document.getElementById('modalProductDescription').innerText = description;
            document.getElementById('modalProductPrice').innerText = price;
            document.getElementById('modalProductImage').src = imgSrc;

            // Obtener la tarjeta padre y aplicar la clase de clic
            const card = this.closest('.product-card');
            card.classList.add('clicked');

            // Eliminar la clase después de un breve período
            setTimeout(() => {
                card.classList.remove('clicked');
            }, 200); // Tiempo en milisegundos
        });
    });
});




