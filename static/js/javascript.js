/* When a file is uploaded activate submit button and change the "Method" to "user-file"*/
function fileUploaded(object, model){
    document.getElementById(object.id).nextElementSibling.textContent = object.files[0].name;
    document.getElementById(model.concat("Method")).value = "user-file";
    var button = document.getElementById(model.concat("Submit"));
    button.disabled = false;
}

/* When a picture is selected activate submit button and change the "Method" to "random-picture"*/
function pictureSelected(model){
    document.getElementById(model.concat("Method")).value = "random-picture";
    var button = document.getElementById(model.concat("Submit"));
    button.disabled = false;
}

/* When a text is selected activate submit button and change the "Method" to "random-texts"*/
function textSelected(model){
    document.getElementById(model.concat("Method")).value = "random-text";
    var button = document.getElementById(model.concat("Submit"));
    button.disabled = false;
}

/* When a text is written activate submit button and change the "Method" to "custom-text"*/
function customText(input_text, model){
    document.getElementById(model.concat("Method")).value = "custom-text";
    var button = document.getElementById(model.concat("Submit"));
    button.disabled = false;
}