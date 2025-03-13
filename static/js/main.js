const url = "http://192.168.127.138:5002/"

const socket = io(url);

const imagenes = []


let formulario = document.getElementById("form");
let in_process = document.getElementById("in-process");
let pan_now = document.getElementById("pan-now");
let carousel = document.getElementById("carouselExampleIndicators");
let texto_pan = document.getElementById("texto-pan");
let boton_descargar = document.getElementById("descarga");
let boton_apagar = document.getElementById("boton-apagar");
let spinner = document.getElementById("spinner");
let spinner_text = document.getElementById("spinner-text");
spinner.style.display = "none";
spinner_text.textContent = "";

socket.emit("heartbeat")

socket.on('capturando', (data) => {
    console.log(data)
    if(data)
    {
        formulario.style.display = "none";
        in_process.style.display = "inline-block";
    }
    else
    {
        formulario.style.display = "inline-block";
        in_process.style.display = "none";
    }
});

socket.emit("get_image_now")


socket.on('nueva_imagen', async (data) => {
    const pan_actual = document.getElementById("pan-actual");

    try {
        // Mostrar el spinner mientras se carga la imagen
        spinner.style.display = "inline-block";
        spinner_text.textContent = "Cargando imagen";
        pan_now.style.display = "none";
        carousel.style.display = "none";
        texto_pan.style.display = "none";
        boton_descargar.style.display = "none";
        boton_apagar.style.display = "none";

        // Convertir la data en un Blob (simulando una operación asincrónica)
        let blob = new Blob([data], { type: "image/png" });

        // Crear una URL para el Blob
        let imageUrl = await new Promise((resolve) => {
            setTimeout(() => resolve(URL.createObjectURL(blob)), 1000); // Simulación de tiempo de carga
        });

        // Asignar la imagen cargada
        pan_actual.src = imageUrl;

        // Mostrar los elementos una vez que la imagen está lista
        pan_now.style.display = "inline-block";
        carousel.style.display = "block";
        texto_pan.style.display = "block";
        boton_descargar.style.display = "inline-block";
        boton_apagar.style.display = "inline-block";
        spinner.style.display = "none";
        spinner_text.textContent = "";
    } catch (error) {
        console.error("Error al cargar la imagen:", error);
    } finally {
        // Ocultar el spinner al terminar
        spinner.style.display = "none";
        spinner_text.textContent = "";
    }
});

socket.emit("get_images")

socket.on('nuevas_imagenes', (data) => {
    const carousel = document.getElementById("carousel");
    carousel.querySelectorAll("*").forEach(n => n.remove());
    for (let i=0; i<data.length; i++)
    {
        let blob = new Blob([data[i]], { type: "image/png" });
        // Crear una URL para el Blob
        let imageUrl = URL.createObjectURL(blob);
        let div = document.createElement("div");
        div.className = i==0 ? "carousel-item active" : "carousel-item";
        let img = document.createElement("img");
        img.className = "d-block w-100";
        img.alt = "Imagen de pan "+(i+2);
        img.id = "pan-"+i;
        img.src = imageUrl;
        div.appendChild(img);
        carousel.appendChild(div);
    }
});

const start_server = async () => {
    const pan = document.getElementById("pan").value;
    const frequencia = document.getElementById("time").value;
    const info_pan = document.getElementById("info-pan");
    const info_tiempo = document.getElementById("info-tiempo");
    formulario = document.getElementById("form");
    in_process = document.getElementById("in-process");

    if(pan === "")
    {
        info_pan.textContent = "Debe de colocar un tipo de pan antes de comenzar";
        info_pan.style.color = "darkred";
    }

    if(frequencia === "")
    {
        info_tiempo.textContent = "Debe de colocar un tiempo de frecuencia antes de comenzar";
        info_tiempo.style.color = "darkred";
    }

    if(info_pan.textContent === "" && info_tiempo.textContent === "")
    {
        socket.emit("iniciar_captura", { interval: frequencia, tipo_pan: pan })
        formulario.style.display = "none";
        in_process.style.display = "inline-block";
        pan_now.style.display = "none";
        carousel.style.display = "none";
        texto_pan.style.display = "none";
        boton_descargar.style.display = "none";
        boton_apagar.style.display = "none";
        spinner.style.display = "inline-block";
        spinner_text.textContent = "Encendiendo la cámara";
        iniciarGrafica();
    }
}

const stop_server = async () => {
    socket.emit("detener_captura")
    formulario.style.display = "inline-block";
    in_process.style.display = "none";
}

const descargar_imagen = ()=>{
    let imagenActual = document.querySelector("#carouselExampleIndicators .carousel-item.active img");
    let enlace = document.createElement("a");
    enlace.href = imagenActual.src;
    enlace.download = imagenActual.alt+".png"; // Nombre del archivo a descargar
    document.body.appendChild(enlace);
    enlace.click();
    document.body.removeChild(enlace);
}

// Obtener el carrusel
let myCarousel = new bootstrap.Carousel(document.querySelector('#carouselExampleIndicators'), {
    interval: 3000,  // Cambia cada 3 segundos
    wrap: true,      // Vuelve al inicio al llegar al final
    pause: 'hover'   // Se pausa cuando el usuario pone el mouse encima
  });
  
// Mover hacia adelante
document.getElementById("btn-next").addEventListener("click", () => {
    myCarousel.next(); 
    let imagenActual = document.querySelector("#carouselExampleIndicators .carousel-item.active img");
    let pan = document.getElementById("texto-pan");
    pan.textContent = imagenActual.alt;
  });
  
  // Mover hacia atrás
  document.getElementById("btn-prev").addEventListener("click", () => {
    myCarousel.prev(); 
    let imagenActual = document.querySelector("#carouselExampleIndicators .carousel-item.active img");
    let pan = document.getElementById("texto-pan");
    pan.textContent = imagenActual.alt; 
  });


// Vincular la función al botón
document.getElementById("submit").addEventListener("click", start_server);

const iniciarGrafica = () => {
    const ctx = document.getElementById("miGrafico").getContext("2d");
    new Chart(ctx, {
        type: "line",
        data: {
            labels: ["0 min", "5 min", "10 min", "15 min", "20 min", "25 min", "30 min"],
            datasets: [{
                label: "Volumen del pan (cm³)",
                data: [50, 80, 150, 220, 280, 320, 350],
                backgroundColor: "rgba(255, 99, 132, 0.5)",
                borderColor: "rgba(255, 99, 132, 1)",
                borderWidth: 2,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: "Volumen (cm³)"
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: "Tiempo (minutos)"
                    }
                }
            }
        }
    });
};

