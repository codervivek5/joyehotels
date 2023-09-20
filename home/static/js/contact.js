function sendWhatsapp() {

    let name = document.getElementById("name");
    let email = document.getElementById("email");
    let number = document.getElementById("number");
    let subject = document.getElementById("subject");
    let message = document.getElementById("message");
    let mobileNumber = "917393017587"; //Enter your mobile number here

    if (name.value.trim() == "") {
        name.style.background = "lightpink";
        name.style.border = "4px solid red";
        alert("Please enter your name");
        return false;
    }
    // else if (email.value.trim() === "") {
    //     email.style.background = "lightpink";
    //     email.style.border = "4px solid red";
    //     alert("Please enter your email");
    //     return false;
    // }

    let url =
        `https://wa.me/${mobileNumber}?text=` +
        "*Name:* " + name.value + "%0a" +
        "*User e-mail:* " + email.value + "%0a" +
        "*Mobile Number:* " + number.value + "%0a" +
        "*Subject:* " + subject.value + "%0a" +
        "*Message:* " + message.value;

    window.open(url, "_blank").focus();
}