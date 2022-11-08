/**
 * Given the page number return the requested instruction text
 * @param pageNumber : int
 */
getInstructionPage(){

    part_index = app.session.current_index.part_index;

    return app.instruction_pages[part_index][app.get_instruction_page_index()].text_html
},

get_instruction_page_index(){
    return app.get_current_session_player_part().current_instruction;
},

get_current_session_player_part(){
    return app.session_player.session_player_parts[app.session.current_index.part_index];
},

get_current_number_of_instruction_pages(){
    return app.instruction_pages[app.session.current_index.part_index].length;
},

/**
 * advance to next instruction page
 */
sendNextInstruction(direction){

    if(this.working) return;
    
    this.working = true;
    this.sendMessage("next_instruction", {"direction" : direction});
},

/**
 * advance to next instruction page
 */
takeNextInstruction(messageData){
    if(messageData.status.value == "success")
    {
        result = messageData.status.result;       

        session_player_part = this.session_player.session_player_parts[app.session.current_index.part_index];
        
        session_player_part.current_instruction = result.current_instruction;
        session_player_part.current_instruction_complete = result.current_instruction_complete;

        this.processInstructionPage();
        this.instructionDisplayScroll();
    } 
    else
    {
        
    }
    
},

/**
 * finish instructions
 */
sendFinishInstructions(){

    if(this.working) return;
    
    this.working = true;
    this.sendMessage("finish_instructions", {});
},

/**
 * finish instructions
 */
takeFinishInstructions(messageData){
    if(messageData.status.value == "success")
    {
        result = messageData.status.result;       

        session_player_part = this.session_player.session_player_parts[app.session.current_index.part_index];
        
        session_player_part.instructions_finished = result.instructions_finished;
        session_player_part.current_instruction_complete = result.current_instruction_complete;
    } 
    else
    {
        
    }
},

/**
 * process instruction page
 */
processInstructionPage(){

    //update view when instructions changes
    // switch(this.session_player.current_instruction){
    //     case 1:            
    //         break; 
    //     case 2:
    //         break;
    //     case 3:            
    //         break;
    //     case 4:
    //         break; 
    //     case 5:           
    //         break;
    //     case 6:
    //         break;
    // }

    session_player_part = this.session_player.session_player_parts[app.session.current_index.part_index];

    if(session_player_part.current_instruction_complete < session_player_part.current_instruction)
    {
        session_player_part.current_instruction_complete = session_player_part.current_instruction;
    }

    app.instructionDisplayScroll();    
},

/**
 * scroll instruction into view
 */
instructionDisplayScroll(){
    
    document.getElementById("instructions_frame").scrollIntoView();
    setTimeout(app.scroll_update, 500);
},

scroll_update()
{
    var scrollTop = document.getElementById('instructions_frame_a').scrollTop;
    var scrollHeight = document.getElementById('instructions_frame_a').scrollHeight; // added
    var offsetHeight = document.getElementById('instructions_frame_a').offsetHeight;
    // var clientHeight = document.getElementById('box').clientHeight;
    var contentHeight = scrollHeight - offsetHeight; // added
    if (contentHeight <= scrollTop) // modified
    {
        // Now this is called when scroll end!
        app.instruction_pages_show_scroll = false;
    }
    else
    {
        app.instruction_pages_show_scroll = true;
    }
},