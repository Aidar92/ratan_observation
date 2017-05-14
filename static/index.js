window.onload = function() {
    document.querySelectorAll("[id*=range]").forEach(function(item, i) {
        document.getElementById("lbl" + i).innerHTML = item.value;
    });
    const selectElem = document.getElementById('chanel')
    for (let i = 0; i <= 179; i++) {
        let option = document.createElement("option");
        option.text = i;
        option.value = i;
        selectElem.add(option);
    }
}


function getJSON(url, success, error) {
    const xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                success(JSON.parse(xhr.responseText));
            } else {
                error(xhr.responseText);
            }
        }
    }
    xhr.open('GET', url);
    xhr.send();
};

document.getElementById('syncRange').addEventListener("change", function(e) {
    document.getElementById('syncLbl').innerHTML = this.value;
});
document.querySelectorAll("[id*=range]").forEach(function(item, i) { 
    item.addEventListener("change", function() {        
        document.getElementById("lbl" + i).innerHTML = item.value;
    });
});
document.getElementById('getBtn').addEventListener("click", function() {
    getJSON('/get', function(data) {
        data.data.forEach(function(item, i) {
            document.getElementById("range" + i).value = item;
            document.getElementById("lbl" + i).innerHTML = item
        }, this);
        data.status.forEach(function(item, i) {
            document.querySelectorAll('input[type=checkbox]')[i].checked = item;
        });
        document.getElementById('syncRange').value = data.syncRange;
        document.getElementById('syncLbl').innerHTML = data.syncRange;
    });
});
document.getElementById('sendBtn').addEventListener("click", function() {
    const xhr = new XMLHttpRequest();
    data = []
    document.querySelectorAll('[id*=range]').forEach(function(item, i) {
        data.push(item.value);
    });
    document.querySelectorAll('input[type=checkbox]').forEach(function(item, i) {
        data.push(item.checked);
    });
    data.push(document.getElementById('syncRange').value);
    xhr.open("POST", '/send', true);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    
    xhr.send(JSON.stringify({data: data}));
});
function delChannel(e) {
    document.getElementById("item" + e.id).remove();
    document.querySelector('option[value=' + "'" + e.id + "'" + ']').selected = false;    
}
function randomColorGenerator() { 
    return '#' + (Math.random().toString(16) + '0000000').slice(2, 8); 
};
document.getElementById('plotBtn').addEventListener("click", function(){
    document.getElementsByClassName('content')[0].style.display = 'inline-flex';
    const ctx = document.getElementById("chart");  
    ctx.width = window.innerWidth*0.65;
    ctx.height = 400  
    let chart = new Chart(ctx, {
        width: ctx.width,
        height: ctx.height,
        type: 'line',        
        data: {
            datasets: []
        },
        options: { 
            legend: {
                labels: {
                    generateLabels: function(chart) {
                        labels = Chart.defaults.global.legend.labels.generateLabels(chart);
                        let showestLabels = []
                        for (let i = 0; i < chart.data.datasets.length; i++) {
                            if (!chart.data.datasets[i].hidden) {
                                showestLabels.push(labels[i])
                                
                            }
                        }
                        return showestLabels;
                    }
                }
            },
            responsive: false,
            maintainAspectRatio: false,
            animation: false,
            scales: {
                xAxes: [{
                    stacked: false,
                    type: 'linear',
                    position: 'bottom',
                     
                                     
                }],
                yAxes: [{
                    stacked: false,
                    
                }]
            }
        }  
    });
    document.getElementById("chanel").addEventListener("change", function() {
        document.getElementById("saveBtn").disabled = false;
        chart.data.datasets = [];
        for (let i = 0; i < this.options.length; i++) {                
                chart.data.datasets.push({ 
                    label: 'Channel ' + i,
                    fill: false,
                    borderColor: randomColorGenerator(), 
                    data: [],  
                   
                    hidden: !this.options[i].selected                     
                });
                if (chart.data.datasets[i].hidden) {
                    delete chart.data.datasets[i].label;
                }
                
        }      
        let count = 0;   
        let interval = setInterval(function(){
            count++;
            getJSON('/graph', function(data) {
                for (let i = 0; i < document.getElementById('chanel').options.length; i++) {
                    if (document.getElementById('chanel').options[i].selected) {                                               
                        chart.data.datasets[i].data.push({x: count, y: data.data[i]});
                        chart.update();
                    }   
                }
                
            }, this);
        }, parseInt(document.getElementById("period").value)*1000);   
        if (count >= parseInt(document.getElementById("time").value)) {
            clearInterval(interval);
            let result = {};
            chart.data.datasets.forEach(function(dataset, i) {
                if (!dataset.hidden) {
                  result[dataset.label] = dataset.data.map(function(item) 
                    {
                        return item;
                    });
                }                
            });
            const keys = Object.keys(result).sort();
            for (let i = 0; i < keys.length; i++) {
                let key = keys[i];
            }
            for (let i = 0; i < document.getElementById('chanel').options.length; i++) {
                document.getElementById('chanel').options[i].selected = false;
            }
            
            
        };
        document.getElementById("saveBtn").addEventListener("click", function() {
            const xhr = new XMLHttpRequest();
            xhr.open("POST", '/save', true);
            xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
            xhr.send(JSON.stringify({data: result}));
        });
    });
}, false);



