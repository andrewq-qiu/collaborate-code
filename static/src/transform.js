/*This file is a mirror of the
transform.py file. The functions in this
file apply Operation Transformation algorithms
in the same implementation as transform.py,
just on different datatypes. 

Copyright and Usage Information
===============================

This project and file is licensed with the MIT License.
See https://github.com/andrewcoool/collaborate-code/
and the LICENSE file for more information.

Author: Andrew Qiu (GitHub @andrewcoool)
*/

/**
 * Return whether or not pos_1 is before pos_2
 * @param {Array} pos_1 - The first position
 * @param {Array} pos_2 - The second position
 * @returns {boolean} Whether or not pos_1 is before pos_2
 */
function is_pos_before(pos_1, pos_2){
    return pos_1[0] < pos_2[0] || (pos_1[0] == pos_2[0] && pos_1[1] < pos_2[1]);
}


/**
 * Return whether or not pos_1 is the same as pos_2
 * @param {Array} pos_1 - The first position
 * @param {Array} pos_2 - The second position
 * @returns {boolean} Whether or not pos_1 is the same as pos_2
 */
function is_same_pos(pos_1, pos_2){
    return pos_1[0] == pos_2[0] && pos_1[1] == pos_2[1];
}

/**
 * Transform op_1 against op_2, assuming that op_2
 * is executed first and op_1 is executing immediately
 * after.
 * @param {Array} op_1 - The first operation
 * @param {Array} op_2 - The second operation
 * @returns {Array} The transformed first operation
 */
function xform(op_1, op_2){
    const t_1 = op_1[0];
    const t_2 = op_2[0];

    if (t_1 == 'ID' || t_2 == 'ID'){return op_1;}

    if (t_1 == 'INS' && t_2 == 'INS'){
        return t_ii(op_1, op_2);
    }else if (t_1 == 'INS' && t_2 == 'DEL'){
        return t_id(op_1, op_2);
    }else if (t_1 == 'DEL' && t_2 == 'INS'){
        return t_di(op_1, op_2);
    }else if(t_1 == 'DEL' && t_2 == 'DEL'){
        return t_dd(op_1, op_2);
    }
}

/**
 * Transform an array of operations against another list
 * of operations. Return the operations each side must apply
 * to reach the same state space.
 * @param {Array} op_lefts - The first array of operations
 * @param {Array} op_rights - The second array of operations
 * @returns {Array} An array with two elements | 0 - the operations the left must apply, 1 - the operations the right must apply
 */
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

function t_ii(op_1, op_2){
    let pos_1 = op_1[1];
    let pos_2 = op_2[1];

    if (is_pos_before(pos_1, pos_1) || (is_same_pos(pos_1, pos_2) && op_1[3] < op_2[3])){
        return ['INS', pos_1, op_1[2], op_1[3]];
    }else{
        if(op_2[2] == '\n'){
            return ['INS', [pos_1[0] + 1, pos_1[1]], op_1[2], op_1[3]];
        }else if (pos_1[0] == pos_2[0]){
            return ['INS', [pos_1[0], pos_1[1] + 1], op_1[2], op_1[3]];
        }else{
            return ['INS', pos_1, op_1[2], op_1[3]];
        }
    }
}

function t_id(op_1, op_2){
    let pos_1 = op_1[1];
    let pos_2 = op_2[1];

    if(is_pos_before(pos_1, pos_2) || is_same_pos(pos_1, pos_2)){
        return ['INS', pos_1, op_1[2], op_1[3]];
    }else{
        if(pos_2[1] == -1){
            return ['INS', [pos_1[0] - 1, pos_1[1]], op_1[2], op_1[3]];
        }else if(pos_1[0] == pos_2[0]){
            return ['INS', [pos_1[0], pos_1[1] - 1], op_1[2], op_1[3]];
        }else{
            return ['INS', pos_1, op_1[2], op_1[3]];
        }
    }
}

function t_di(op_1, op_2){
    let pos_1 = op_1[1];
    let pos_2 = op_2[1];

    if(is_pos_before(pos_1, pos_2)){
        return ['DEL', pos_1, op_1[2]];
    }else{
        if(op_2[2] == '\n'){
            return ['DEL', [pos_1[0] + 1, pos_1[1]], op_1[2]];
        }else if(pos_1[0] == pos_2[0]){
            return ['DEL', [pos_1[0], pos_1[1] + 1], op_1[2]];
        }else{
            return ['DEL', pos_1, op_1[2]];
        }
    }
}

function t_dd(){
    let pos_1 = op_1[1];
    let pos_2 = op_2[1];

    if (is_pos_before(pos_1, pos_2)){
        return ['DEL', pos_1, op_1[2]];
    }else if(!is_same_pos(pos_1, pos_2)){
        if (pos_2[1] == -1){
            return ['DEL', [pos_1[0] - 1, pos_1[1]], op_1[2]];
        }else if(pos_1[0] == pos_2[0]){
            return ['DEL', [pos_1[0], pos_1[1]] - 1, op_1[2]];
        }else{
            return ['DEL', pos_1, op_1[2]];
        }
    }else{
        return ['ID', op_1[2]];
    }
}