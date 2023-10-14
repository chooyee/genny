const txtprompt = document.getElementById('txtprompt');
const blockHistory = document.querySelector('.history-block');
const hidvisitorid = document.getElementById('visitorid');
const btnUpload = document.getElementById('btnUpload');
const divResult = document.getElementById('divResult');
const lblcurrentdoc = document.getElementById('lblcurrentdoc');
var chatHistory = [];

document.addEventListener('DOMContentLoaded', function () { 
    let visitorid = getCookie('visitorid');
    if (visitorid==null)
    {
        visitorid = uuidv4();
        setCookie('visitorid', visitorid);
        console.log(document.cookie)
    }
    hidvisitorid.value = visitorid; 

    let currentDoc = getCookie('currentDoc');
    if (currentDoc)
    {
        
        lblcurrentdoc.innerHTML = currentDoc;
    }

    const filebrowser = document.getElementById('customFile');
    filebrowser.addEventListener('change', function(ev) {
        var file = ev.target.files[0];
        var reader = new FileReader();
        reader.readAsText(file);
        reader.onload = function(e) {      
            lblcurrentdoc.innerHTML = file.name;
            setCookie('currentDoc', file.name);
        };
    });
}, false);


function checkStatus(response) {            
    if (response.status >= 200 && response.status < 300) {
        return Promise.resolve(response)
    } else {                
        return Promise.reject(response.text())
    }
}

function parseJson(response) {
    return response.json()
}

txtprompt.addEventListener('keyup',async (e)=>{
    e.preventDefault();

    if ( e.keyCode == 13 ) {
        promptValue = txtprompt.value;
        txtprompt.setAttribute("disabled", true);
        let jsonData = {}; 
        jsonData["visitorid"] = hidvisitorid.value;
        jsonData["prompt"] = promptValue;
        jsonData["chathistory"] = chatHistory;

        json = JSON.stringify(jsonData);
        console.log(json);
        var req = new Request('prompt', {
            method: 'post',
            mode: 'cors',
            headers: {
                "Content-Type": "application/json",
                // 'Content-Type': 'application/x-www-form-urlencoded',
              },       
            body: JSON.stringify(jsonData)
        });

        result = await fetch(req)
        .then(checkStatus)
        .then(parseJson)
        .then(function (data) {
            console.log('Request succeeded with JSON response', data);
            return data
        }).catch(async function (error) {
            errMsg =  await error
            console.log('Request failed', errMsg);
            divResult.appendChild(CreateErrorMsgCard(errMsg));
            btnUpload.disabled = false;
        });
        //console.log(result);
        //blockHistory.innerHTML = result["answer"]
        txtprompt.value = "";
        txtprompt.removeAttribute("disabled");
        popHistory(result);
    }
})

btnUpload.addEventListener('click', async (e)=>{
    btnUpload.disabled = true;
    txtprompt.disabled = true;
    var submit = MandatoryValidation();
    if (customFile.files.length < 1)
    {
        alert("Please select a file to upload!");
    }
    if (submit)
    {      
        let formData = new FormData(); 
        formData.append("visitorid", hidvisitorid.value);
        formData.append("file", customFile.files[0]);
        var req = new Request('upload/pdf', {
            method: 'post',
            mode: 'cors',
            redirect: 'follow',          
            body: formData
        });
       
        result = await  fetch(req)
        .then(checkStatus)
        .then(parseJson)
        .then(function (data) {
            console.log('Request succeeded with JSON response', data);
            return data
        }).catch(async function (error) {
            errMsg =  await error
            console.log('Request failed', errMsg);
            divResult.appendChild(CreateErrorMsgCard(errMsg));
            btnUpload.disabled = false;
        });
        txtprompt.disabled = false;
        btnUpload.disabled = false;
        divResult.innerHTML = "";
        divResult.appendChild(CreateCard(result));
        //console.log(result)

    }   
   
})

function CreateCard(result)
{
    const card = document.createElement('div');
    card.classList.add("card")
    const cardBody = document.createElement('div');
    cardBody.classList.add("card-body")
    const cardTitle = document.createElement('h5');
    cardTitle.innerHTML = `Message: ${result.msg}`
    cardTitle.classList.add("card-title")
    const cardContent = document.createElement('p');
    cardContent.innerHTML = `Elapsed time (seconds): ${result.elapsed_time}`;

    cardBody.appendChild(cardTitle);
    cardBody.appendChild(cardContent);
    card.appendChild(cardBody);
    return card;
}

function CreateErrorMsgCard(result)
{
    const card = document.createElement('div');
    card.classList.add("card");
    const cardBody = document.createElement('div');
    cardBody.classList.add("card-body");
    const cardTitle = document.createElement('h5');
    cardTitle.innerHTML = `An Unexpected Error`;
    cardTitle.classList.add("card-title");
    const cardContent = document.createElement('p');
    cardContent.innerHTML = `${result}`;

   
    cardBody.appendChild(cardTitle);
    cardBody.appendChild(cardContent);
    card.appendChild(cardBody);
    return card;
}

function getHistory()
{
    chatHistory = [];
    const chatHistoryElements = [...document.querySelectorAll("[ref='question-el']")];
    i = 0;

    chatHistoryElements.forEach((questionEl)=>{
        console.log(questionEl)
        answerElId = questionEl.getAttribute("for");
        let answerEl = document.getElementById(answerElId);

        q = questionEl.innerHTML;
        a = answerEl.innerHTML;
        chatHistory.push({q, a});
        i++;
    })

    return chatHistory;
}

function popHistory(result)
{
    chatHistory = result["chat_history"];
    divCard = createElement("div", {"class":"card"});

    i = 0;
    chatHistory.forEach(element => {
      
        let blockq = createElement("div", {"class":"card-body pre-question text-capitalize", "ref":"question-el", "for": `history-${i}`});
        let blocka = createElement("div", {"class":"card-body pre-answer", "ref":"answer-el", "id": `history-${i}`});
        blockq.innerHTML = element[0];
        blocka.innerHTML = element[1];

        divCard.appendChild(blockq);
        divCard.appendChild(blocka);
        i++;
    });
    blockHistory.innerHTML = "";
    blockHistory.appendChild(divCard);
}
const createElement = (elementType, attrs = {})=>
{
	const el = document.createElement(elementType);
	for (const [k, v] of Object.entries(attrs)) {
		el.setAttribute(k, v);
	}
	return el;
}

function getCookie (name) {
	let value = `; ${document.cookie}`;
	let parts = value.split(`; ${name}=`);
	if (parts.length === 2) return parts.pop().split(';').shift();
}

function setCookie(name, val, expiryDays =30)
{
    // expires in two weeks: 60 seconds x 60 minutes x 24 hours x 14 days
    // we'll look at the math behind this in the next section
    document.cookie = `${name}=${val}; path=/; max-age=${60 * 60 * 24 * expiryDays};`;
}

function uuidv4() { 
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'
    .replace(/[xy]/g, function (c) { 
        const r = Math.random() * 16 | 0,  
            v = c == 'x' ? r : (r & 0x3 | 0x8); 
        return v.toString(16); 
    }); 
}