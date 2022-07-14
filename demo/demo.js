function add_header(str)
{
    var li = document.createElement('li');
    li.appendChild(document.createTextNode(str))
    li.innerHTML += ' <button onclick="this.parentNode.remove()">-</button>';
    document.getElementById("request-headers-input-list").appendChild(li);
}

function make_request() {
    headers = [
        "Host: backend.address",
        "User-Agent: My-Personal-Demo",
        "content-length: 50"
    ];

    var nodelist = document.getElementById("request-headers-input-list").childNodes
    nodelist.forEach((li) => {
        var header = li.innerText.slice(0,-2)
        headers.push(header);
    });
    add_diagram_entry(headers,null,"request");
    headers.push("src:" + document.forms.control_panel.elements.route_request.value);

    // console.log("Sent request with " + headers)
    fetch('http://127.0.0.1:80/proxy-compromise', {
        method: 'POST',
        headers: new Headers({
                    'Content-Type': 'application/json'
                }),
        body: JSON.stringify(headers)
    }).then(
        response => response.text()
    ).then(
        resp_headers => triage_response(resp_headers)
    ).catch((error) => {
        console.error('Error:', error);
    });
    
    //clear header list on page
    // removeAllChildNodes(document.getElementById("request-headers-input-list"), 0);
}

function triage_response(resp_headers){
    add_diagram_entry(JSON.parse(resp_headers.replace(/'/g, '"')),null,"response") 
}

function clear_diagram() {
    removeAllChildNodes(document.getElementById("requests-column"), 1);
}

function add_diagram_entry(headers,body,entry_type) {
    // console.log(headers)
    // create a new div element
    //// <div class="diagram-entry">
    ////  <span class="diagram-entry-arrow">&#10148;</span>
    ////  <span class="diagram-entry-arrow"></span>
    //// </div>
    var diagram_entry = document.createElement("div");
    var pre = document.createElement("pre");
    var diagram_entry_arrow = document.createElement("span");
    var network_demarcator = document.createElement("span");

    var arrow = document.createTextNode("\u27A4");
    diagram_entry_arrow.setAttribute("class", "diagram-entry-arrow")
    network_demarcator.setAttribute("class", "network-demarcator")
    network_demarcator.setAttribute("id", document.forms.control_panel.elements.route_request.value)
    network_demarcator.setAttribute("title", "This is where the server considers the end of internal zone where authentication is unnecessary")
    if (entry_type == "request"){
        diagram_entry.setAttribute("class", "diagram-entry request");
    }else if (entry_type == "response"){
        diagram_entry.setAttribute("class", "diagram-entry response");
    }

    diagram_entry_arrow.appendChild(arrow);
    diagram_entry.appendChild(diagram_entry_arrow);
    diagram_entry.appendChild(network_demarcator);

    // and give it some content
    var newContent = document.createTextNode(headers.join('\n'));

    // add the text node to the newly created div
    pre.appendChild(newContent);
    diagram_entry.appendChild(pre);

    // add the newly created element and its content into the DOM
    var requests_column = document.getElementById("requests-column")
    requests_column.appendChild(diagram_entry);
    requests_column.scrollTop = requests_column.scrollHeight;

}

function removeAllChildNodes(parent, spare) {
    while (parent.childElementCount > spare) {
        parent.removeChild(parent.lastChild);
    }
}
