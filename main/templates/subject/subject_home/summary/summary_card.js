sendName(){

    app.working = true;
    app.sendMessage("name", {"formData" : {name : document.getElementById("id_name").value, 
                                           student_id : document.getElementById("id_student_id").value}});
                     
},

/** take result of submitting name
*/
takeName(messageData){

    app.clearMainFormErrors();

    if(messageData.status.value == "success")
    {
        app.session_player.name = messageData.status.result.name; 
        app.session_player.student_id = messageData.status.result.student_id;           
        app.session_player.name_submitted = messageData.status.result.name_submitted;       
    } 
    else
    {
        app.displayErrors(messageData.status.errors);
    }
},