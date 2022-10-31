let video = document.querySelector("#video");
let capture = document.getElementById("capture");
let canvas = document.querySelector("#canvas");
let context = canvas.getContext("2d");

if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
  // console.log("Camera is Work")
  const cam = navigator.mediaDevices.enumerateDevices().then((devides) => {
    // console.log(devides);

    let count = 1;
    for (i = 0; i != devides.length; i++) {
      if (devides[i].kind === "videoinput") {
        var ul = document.getElementById("cameraList");
        var li = document.createElement("li");
        li.appendChild(document.createTextNode(devides[i].kind));
        ul.appendChild(li);
        count++;
      }
    }
  });

  navigator.mediaDevices
    .getUserMedia({
      video: {
        width: { ideal: 200 },
        height: { ideal: 200 },
      },
    })
    .then((stream) => {
      video.srcObject = stream;
    })
    .catch((error) => {
      console.log(error);
    });
} else {
  console.log("getUserMedia not supported");
}

function add_click() {
  context.drawImage(video, 0, 0, 200, 200);
  let image_data_url = canvas.toDataURL("image/jpeg");
  console.log(image_data_url);
}

capture.addEventListener("click", add_click);
