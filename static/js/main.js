const url = "http://127.0.0.1:5002"

const socket = io(url);

let formulario = document.getElementById("form");
let in_process = document.getElementById("in-process");

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
        iniciarGrafica();
    }
}
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
