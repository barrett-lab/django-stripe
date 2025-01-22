// payment.js

// Set up Stripe.js with your Publishable Key
var stripe = Stripe('{{ STRIPE_PUBLIC_KEY }}');

// Create an instance of Elements
var elements = stripe.elements();

// Create an instance of the card Element
var card = elements.create('card');

// Add an instance of the card Element into the `card-element` div
card.mount('#card-element');

// Handle real-time validation errors from the card Element
card.addEventListener('change', function(event) {
  var displayError = document.getElementById('card-errors');
  if (event.error) {
    displayError.textContent = event.error.message;
  } else {
    displayError.textContent = '';
  }
});

// Handle form submission
var form = document.getElementById('payment-form');
form.addEventListener('submit', function(event) {
  event.preventDefault();

  // Disable the submit button to prevent multiple submissions
  document.getElementById('submit-payment').disabled = true;

  // Create payment method using card Element
  stripe.createPaymentMethod({
    type: 'card',
    card: card,
  }).then(function(result) {
    if (result.error) {
      // Show error to customer
      var errorElement = document.getElementById('card-errors');
      errorElement.textContent = result.error.message;

      // Enable the submit button
      document.getElementById('submit-payment').disabled = false;
    } else {
      // Send payment method to your server to process payment
      var paymentMethodId = result.paymentMethod.id;
      fetch('/process_payment/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': '{{ csrf_token }}',
        },
        body: JSON.stringify({
          payment_method_id: paymentMethodId,
        }),
      }).then(function(response) {
        return response.json();
      }).then(function(result) {
        // Handle server response
        console.log(result);
      });
    }
  });
});
