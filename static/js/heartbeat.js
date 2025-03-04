const starter = document.getElementById("starter");
const in_process = document.getElementById("in-process");

const url = "http://127.0.0.1:5002"

const socket = io(url);

socket.emit("heartbeat")

socket.on('heartbeat', (data) => {
    if(data)
    {
        starter.style.display = "none";
        in_process.style.display = "inline-block";
    }
    else
    {
        starter.style.display = "inline-block";
        in_process.style.display = "none";
    }
});