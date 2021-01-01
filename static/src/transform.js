/*Transform op_1 based on op_2. Assume op_2 is chronologically first.*/
function xform(op_1, op_2){
    const t_1 = op_1[0];
    const t_2 = op_2[0];

    if (t_1 == 'INS' && t_2 == 'INS'){
        if (op_1[1] < op_2[1] || (op_1[1] == op_1[1] && op_1[3] < op_2[3])){
            return ['INS', op_1[1], op_1[2], op_1[3]];
        }else{
            return ['INS', op_1[1] + 1, op_1[2], op_1[3]];
        }
    }else if (t_1 == 'INS' && t_2 == 'DEL'){
        if (op_1[1] <= op_2[1]){
            return ['INS', op_1[1], op_1[2]], op_1[3];
        }else{
            return ['INS', op_1[1] - 1, op_1[2]], op_1[3];
        }
    }else if (t_1 == 'DEL' && t_2 == 'INS'){
        if (op_1[1] < op_2[1]){
            return ['DEL', op_1[1], op_1[2]];
        }else{
            return ['DEL', op_1[1] + 1, op_1[2]];
        }
    }else if(t_1 == 'DEL' && t_2 == 'DEL'){
        if (op_1[1] < op_2[1]){
            return ['DEL', op_1[1], op_1[2]];
        }else if(op_1[1] > op_2[1]){
            return ['DEL', op_1[1] - 1, op_1[2]];
        }else{
            return ['ID', op_1[1]]
        }
    }else if(t_1 == 'ID' || t_2 == 'ID'){
        return op_1;
    }
}

function xform_multiple(op_lefts, op_rights){
    /*See transform.py for documentation. This is a straight
    translation of python function xform_multiple.
    */

    var to_apply_left = [];
    var to_apply_right = [];

    var current_rights = op_rights;

    for (var i = 0; i < op_lefts.length; i++){
        var next_rights = [];
        let opl = op_lefts[i];

        var current_left = opl;

        for (var j = 0; j < current_rights.length; j++){
            let current_right = current_rights[j];

            next_rights.push(xform(current_right, current_left));
            current_left = xform(current_left, current_right);
        }

        to_apply_right.push(current_left);
        current_rights = next_rights;
    }

    to_apply_left = current_rights;

    return [to_apply_left, to_apply_right]
}