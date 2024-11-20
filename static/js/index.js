const balance = document.getElementById('balance');
const moneyPlus = document.getElementById('money-plus');
const moneyMinus = document.getElementById('money-minus');
const list = document.getElementById('list');
const form = document.getElementById('form');
const text = document.getElementById('text');
const amount = document.getElementById('amount');
const email = document.getElementById('email').value;
const notification = document.getElementById('notification');

let transactions = [];

// Show notification
function showNotification() {
  notification.classList.add('show');
  setTimeout(() => {
    notification.classList.remove('show');
  }, 2000);
}

// Add transaction
async function addTransaction(e) {
  e.preventDefault();

  if (text.value.trim() === '' || amount.value.trim() === '') {
    showNotification();
    return;
  }

  const transaction = {
    email: email,
    description: text.value,
    amount: parseFloat(amount.value),
  };

  try {
    const response = await fetch('/add_transaction', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(transaction),
    });

    const data = await response.json();

    if (response.ok) {
      transactions.push(data.transaction);
      addTransactionDOM(data.transaction);
      updateValues();
      text.value = '';
      amount.value = '';
    } else {
      alert(data.error || 'Failed to add transaction');
    }
  } catch (error) {
    alert('An error occurred: ' + error.message);
  }
}

// Add transaction to DOM
function addTransactionDOM(transaction) {
  const sign = transaction.amount < 0 ? '-' : '+';
  const item = document.createElement('li');
  item.classList.add(sign === '+' ? 'plus' : 'minus');
  item.innerHTML = `
    ${transaction.description} <span>${sign}${Math.abs(transaction.amount)}</span>
    <button class="delete-btn" onclick="removeTransaction(${transaction.id})">
      <i class="fa fa-times"></i>
    </button>
  `;
  list.appendChild(item);
}

// Update values
function updateValues() {
  const amounts = transactions.map((transaction) => transaction.amount);
  const total = amounts.reduce((acc, item) => (acc += item), 0).toFixed(2);
  const income = amounts
    .filter((item) => item > 0)
    .reduce((acc, item) => (acc += item), 0)
    .toFixed(2);
  const expense = (
    amounts.filter((item) => item < 0).reduce((acc, item) => (acc += item), 0) *
    -1
  ).toFixed(2);

  balance.innerText = `₹${total}`;
  moneyPlus.innerText = `₹${income}`;
  moneyMinus.innerText = `₹${expense}`;
}

// Init
function init() {
  list.innerHTML = '';
  transactions.forEach(addTransactionDOM);
  updateValues();
}

init();

// Event listeners
form.addEventListener('submit', addTransaction);
