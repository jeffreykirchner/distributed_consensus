/**update text of move on button based on current state
         */
 updatePhaseButtonText(){
    if(this.session.finished && this.session.current_experiment_phase == "Done")
    {
        this.move_to_next_phase_text = '** Experiment complete **';
    }
    else if(this.session.current_experiment_phase == "Names")
    {
        this.move_to_next_phase_text = 'Complete Expermient <i class="fas fa-flag-checkered"></i>';
    }
    else if(this.session.current_experiment_phase == "Results")
    {
        this.move_to_next_phase_text = 'Enter Names <i class="far fa-address-card"></i>';
    }    
    else if(this.session.current_experiment_phase == "Instructions")
    {
        this.move_to_next_phase_text = 'Start Expermient <i class="far fa-play-circle"></i>';
    }
    else if(this.session.current_experiment_phase == "Run")
    {
        this.move_to_next_phase_text = 'Running ...';
    }
    // else if(this.session.started && !this.session.finished)
    // {
    //     if(this.session.current_experiment_phase == "Selection" && this.session.parameter_set.show_instructions == "True")
    //     {
    //         this.move_to_next_phase_text = 'Show Instrutions <i class="fas fa-map"></i>';
    //     }
    //     else
    //     {
    //         this.move_to_next_phase_text = 'Start Expermient <i class="far fa-play-circle"></i>';
    //     }
    // }
},

/**start the experiment
*/
start_experiment(){
    app.working = true;
    app.sendMessage("start_experiment", {});
},

/** take start experiment response
 * @param messageData {json}
*/
takeStartExperiment(messageData){
    app.takeGetSession(messageData);
},

/** update start status
*    @param messageData {json} session day in json format
*/
takeUpdateStartExperiment(messageData){
    app.takeGetSession(messageData);
},

/** update start status
*    @param messageData {json} session day in json format
*/
takeUpdateResetExperiment(messageData){
    app.takeGetSession(messageData);
},

/**reset experiment, remove all bids, asks and trades
*/
reset_experiment(){
    if (!confirm('Reset session? All activity will be removed.')) {
        return;
    }

    app.working = true;
    app.sendMessage("reset_experiment", {});
},

/** take reset experiment response
 * @param messageData {json}
*/
takeResetExperiment(messageData){
    app.chat_list_to_display=[];
    app.takeGetSession(messageData);
},

resetConnections(){
    if (!confirm('Reset connection status?.')) {
        return;
    }

    app.working = true;
    app.sendMessage("reset_connections", {});
},

/** update start status
*    @param messageData {json} session day in json format
*/
takeUpdateResetConnections(messageData){
    app.takeGetSession(messageData);
},

/** take reset experiment response
 * @param messageData {json}
*/
takeResetConnections(messageData){
    app.takeGetSession(messageData);
},

/**advance to next phase
*/
next_experiment_phase(){
   
    if (!confirm('Continue to the next phase of the experiment?')) {
        return;
    }    

    app.working = true;
    app.sendMessage("next_phase", {});
},

/** take next period response
 * @param messageData {json}
*/
takeNextPhase(messageData){
    
    app.session.current_experiment_phase = messageData.status.current_experiment_phase;
    app.session.finished = messageData.status.finished;
    app.updatePhaseButtonText();

},

/** take next period response
 * @param messageData {json}
*/
takeUpdateNextPhase(messageData){
    
    app.session.current_experiment_phase = messageData.status.current_experiment_phase;
    app.session.finished = messageData.status.finished;
    app.updatePhaseButtonText();
},

/**
 * start the period timer
*/
startTimer(){
    app.working = true;

    let action = "";

    if(app.session.timer_running)
    {
        action = "stop";
    }
    else
    {
        action = "start";
    }

    app.sendMessage("start_timer", {action : action});
},

/** take start experiment response
 * @param messageData {json}
*/
takeStartTimer(messageData){
    app.takeUpdateTime(messageData);
},

/**reset experiment, remove all bids, asks and trades
*/
endEarly(){
    if (!confirm('End the experiment after this period completes?')) {
        return;
    }

    app.working = true;
    app.sendMessage("end_early", {});
},

/** take reset experiment response
 * @param messageData {json}
*/
takeEndEarly(messageData){
   this.session.parameter_set.part_count = messageData.status.result;
},

/** send invitations
*/
sendSendInvitations(){

    this.sendMessageModalForm.text = tinymce.get("id_invitation_subject").getContent();

    if(this.sendMessageModalForm.subject == "" || this.sendMessageModalForm.text == "")
    {
        this.emailResult = "Error: Please enter a subject and email body.";
        return;
    }

    this.cancelModal = false;
    this.working = true;
    this.emailResult = "Sending ...";

    app.sendMessage("send_invitations",
                   {"formData" : this.sendMessageModalForm});
},

/** take update subject response
 * @param messageData {json} result of update, either sucess or fail with errors
*/
takeSendInvitations(messageData){
    app.clearMainFormErrors();

    if(messageData.status.value == "success")
    {           
        this.emailResult = "Result: " + messageData.status.result.email_result.mail_count.toString() + " messages sent.";

        this.session.invitation_subject = messageData.status.result.invitation_subject;
        this.session.invitation_text = messageData.status.result.invitation_text;
    } 
    else
    {
        this.emailResult = messageData.status.result;
    } 
},

/** show edit subject modal
*/
showSendInvitations(){

    this.cancelModal=true;

    this.sendMessageModalForm.subject = this.session.invitation_subject;
    this.sendMessageModalForm.text = this.session.invitation_text;

    tinymce.get("id_invitation_subject").setContent(this.sendMessageModalForm.text);

    app.sendMessageModal.toggle();
},

/** hide edit subject modal
*/
hideSendInvitations(){
    this.emailResult = "";
},

/**
 * fill invitation with default values
 */
fillDefaultInvitation(){
    this.sendMessageModalForm.subject = this.emailDefaultSubject;
    
    tinymce.get("id_invitation_subject").setContent(this.emailDefaultText);
},

/** show edit subject modal
*/
show_payment_modal(){
    
    app.paymentPeriodsModal.toggle();
},

/** show edit subject modal
*/
send_payment_periods(){

    if (!confirm('Send Payment Periods?')) {
        return;
    }

    payment_periods = [];

    for(let i=0;i<app.session.session_parts.length;i++)
    {
        if(app.session.session_parts[i].parameter_set_part.mode != 'A')
        {
            session_part = app.session.session_parts[i];
            value = document.getElementById('payment_input_' + session_part.id).value;
            v = {id:session_part.id, periods: value};
            payment_periods.push(v);
        }
    }

    app.working = true;
    app.sendMessage("payment_periods", {payment_periods:payment_periods});
},

/** show edit subject modal
*/
take_payment_periods(messageData){

    if(messageData.status.value == "success")
    {           
        result = messageData.status.result;

        app.paymentPeriodsModal.hide();
        this.payment_periods_result = "";
        app.session = result.session;
        app.updatePhaseButtonText();
    } 
    else
    {
        this.payment_periods_result = messageData.status.message;
    } 
},

send_refresh_screens(messageData){
    if (!confirm('Refresh the cliet and server screens?')) {
        return;
    }

    app.working = true;
    app.sendMessage("refresh_screens", {});
},

take_refresh_screens(messageData){
    if(messageData.value == "success")
    {           
        result = messageData.result
        app.session = result.session;
    } 
    else
    {
       
    }
},