document.getElementById('predict-form').addEventListener('submit', function (e) {
  e.preventDefault();
  const form = e.target;
  const formData = new FormData(form);

  fetch('/predict', {
    method: 'POST',
    body: formData
  })
    .then(res => res.json())
    .then(data => {
      if (data.prediction) {
        document.getElementById('result').textContent = 'Predicted Cuisines: ' + data.prediction.join(', ');
      } else {
        document.getElementById('result').textContent = 'Error: ' + data.error;
      }
    });
});

document.getElementById('reset-btn').addEventListener('click', function () {
  document.getElementById('predict-form').reset();
  document.getElementById('result').textContent = '';
});