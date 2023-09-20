
var options = {
  key: "rzp_test_ha0ktmZzSu1erb", // Enter the Key ID generated from the Dashboard
  amount: "1000",
  currency: "INR",
  name: "JoyeHotels",
  description: "Acme Corp",
  image: "https://s3.amazonaws.com/rzp-mobile/images/rzp.jpg",
  prefill: {
    email: "gaurav.kumar@example.com",
    contact: +919900000000,
  },
  config: {
    display: {
      blocks: {
        utib: {
          //name for Axis block
          name: "Pay using Axis Bank",
          instruments: [
            {
              method: "card",
              issuers: ["UTIB"],
            },
            {
              method: "netbanking",
              banks: ["UTIB"],
            },
          ],
        },
        other: {
          //  name for other block
          name: "Other Payment modes",
          instruments: [
            {
              method: "card",
              issuers: ["ICIC"],
            },
            {
              method: "netbanking",
            },
          ],
        },
      },
      hide: [
        {
          method: "upi",
        },
      ],
      sequence: ["block.utib", "block.other"],
      preferences: {
        show_default_blocks: false, // Should Checkout show its default blocks?
      },
    },
  },
  handler: function (response) {
    alert(response.razorpay_payment_id);
  },
  modal: {
    ondismiss: function () {
      if (confirm("Are you sure, you want to close the form?")) {
        txt = "You pressed OK!";
        console.log("Checkout form closed by the user");
      } else {
        txt = "You pressed Cancel!";
        console.log("Complete the Payment");
      }
    },
  },
};
var rzp1 = new Razorpay(options);
document.getElementById("rzp-button1").onclick = function (e) {
  rzp1.open();
  e.preventDefault();
};
