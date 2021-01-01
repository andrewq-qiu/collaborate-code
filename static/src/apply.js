/*Apply operation to Ace Editor type.*/
function apply(op, editor_){
    if (op[0] == 'ID'){return;}

    // Default row 0 for now
    const pos = {'row': 0, 'column': op[1]};

    if (op[0] == 'INS'){
        editor_.session.insert(pos, op[2]);
    }else if (op[0] == 'DEL'){
        // const range = new ace.require('ace/range').Range(0, op[1], 0, op[1] + 1);
        // console.log(range);
        const range = {
            'start': {'row': 0, 'column': op[1]},
            'end': {'row': 0, 'column': op[1] + 1}
        }
        editor_.session.remove(range);
    }
    
}