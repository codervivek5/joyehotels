function sendWA() {
    let place = document.getElementById("place");
    let guest = document.getElementById("numberOfGuests");
    let checkInDate = document.getElementById("checkInDate");
    let checkOutDate = document.getElementById("checkOutDate");
    let mobileNumber = "917393017587"; //Enter your mobile number here

    if (place.value.trim() == "") {
        place.style.background = "lightpink";
        place.style.border = "4px solid red";
        alert("Please Enter your guest");
        return false;
    }

    let url =
        `https://wa.me/${mobileNumber}?text=` +
        "*Place:* " + place.value + "%0a" +
        "*Number of guest:* " + guest.value + "%0a" +
        "*check in date:* " + checkInDate.value + "%0a" +
        "*check out date:* " + checkOutDate.value;

    window.open(url, "_blank").focus();
}
