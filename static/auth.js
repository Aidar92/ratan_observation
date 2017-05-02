document.getElementById('signUp').addEventListener("click", function() {
    const xhr = new XMLHttpRequest();
    const data = [document.getElementById('user').value, document.getElementById('pass').value];
    console.log(data)
    xhr.open("POST", '/signup', true);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");    
    xhr.send(JSON.stringify({data: data}));
});

document.getElementById('auth').addEventListener("click", function() {
    const xhr = new XMLHttpRequest();
    const data = [document.getElementById('user').value, document.getElementById('pass').value];
    console.log(data);
    xhr.open("POST", '/signin', true);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");    
    xhr.send(JSON.stringify({data: data}));
    location.reload(true);
});