function fileUploaded(object){
    document.getElementById(object.id).nextElementSibling.textContent = object.files[0].name;
}