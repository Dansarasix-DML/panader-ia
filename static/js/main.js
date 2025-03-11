const url = "http://192.168.127.138:5002/"

const socket = io(url);
const start_server = async() => {
    const pan = document.getElementById("pan").value;
    const frequencia = document.getElementById("time").value;

    console.log("He llegado bien")

    socket.emit("iniciar_captura",{interval:frequencia,tipo_pan:pan})

    console.log("He llegado bien")
}
