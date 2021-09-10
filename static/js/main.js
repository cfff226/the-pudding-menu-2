var form_options = document.getElementById("form_options");
var add_more_fields = document.getElementById("add_more_fields");
var remove_fields = document.getElementById("remove_fields");

add_more_fields.onclick = function(){
    var newField = document.createElement('input');
    newField.setAttribute('type', 'text');
    newField.setAttribute('name', 'form_options[]');
    newField.setAttribute('class', 'form_options');
    newField.setAttribute('size', 50);
    newField.setAttribute('placeholder', 'Another Field');
    form_options.appendChild(newField)


}